import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import re
import os
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

warnings.filterwarnings('ignore')

# --- FONKSİYONLAR ---
def calculate_ars(src_series):
    ema1 = src_series.ewm(span=3, adjust=False).mean()
    band = 1.23 / 100
    ars_values = np.zeros(len(ema1))
    ars_values[0] = ema1.iloc[0]
    for i in range(1, len(ema1)):
        prev_out = ars_values[i-1]
        curr_ema = ema1.iloc[i]
        if (curr_ema * (1 - band)) > prev_out:
            ars_values[i] = curr_ema * (1 - band)
        elif (curr_ema * (1 + band)) < prev_out:
            ars_values[i] = curr_ema * (1 + band)
        else:
            ars_values[i] = prev_out
    return pd.Series(ars_values, index=src_series.index)

def find_cross_up(fast, slow):
    f = fast.tail(8); s = slow.tail(8)
    if len(f) < 8 or len(s) < 8: return "-"
    for i in range(1, len(f)):
        if f.iloc[i-1] <= s.iloc[i-1] and f.iloc[i] > s.iloc[i]:
            return f"{round(f.iloc[i], 2)} ({len(f)-1-i})"
    return "-"

def find_cross_down(fast, slow):
    f = fast.tail(8); s = slow.tail(8)
    if len(f) < 8 or len(s) < 8: return "-"
    for i in range(1, len(f)):
        if f.iloc[i-1] >= s.iloc[i-1] and f.iloc[i] < s.iloc[i]:
            return f"{round(f.iloc[i], 2)} ({len(f)-1-i})"
    return "-"

async def main():
    bist_raw = "ACSEL, ADEL, ADESE, AGHOL, AGESA, AGROT, AHGAZ, AKBNK, AKCNS, AKSA, AKSEN, ALARK, ALBRK, ALFAS, ALKIM, ANGEN, ARCLK, ARDYZ, ASELS, ASTOR, AYDEM, AYGAZ, BAGFS, BANVT, BERA, BIMAS, BIOEN, BOBET, BRSAN, BRYAT, BUCIM, CANTE, CCOLA, CIMSA, CWENE, DOAS, DOHOL, EGEEN, EKGYO, ENJSA, ENKAI, EREGL, EUHOL, EUPWR, FROTO, GARAN, GESAN, GLYHO, GOLTS, GOZDE, GSDHO, GUBRF, HALKB, HEKTS, HUBVC, IEYHO, IHLGM, IHLAS, INGRM, INVEO, ISCTR, ISGYO, ISMEN, JANTS, KARDMD, KAREL, KARSN, KAYSE, KCAER, KCHOL, KLKIM, KONTR, KONYA, KORDS, KOZAA, KOZAL, KRDMD, LOGO, MAVI, MEDTR, MGROS, MIATK, MPARK, NATEN, NETAS, ODAS, OTKAR, OYAKC, PASEU, PGSUS, PETKM, QUAGR, REEDR, SAHOL, SASA, SAYAS, SDTTR, SISE, SKBNK, SOKM, TARKM, TAVHL, TCELL, THYAO, TKFEN, TKNSA, TOASO, TSKB, TSPOR, TTKOM, TTRAK, TUKAS, TUPRS, TURSG, ULKER, VAKBN, VESBE, VESTL, YEOTK, YKBNK, ZOREN"
    all_stocks = [k.strip() + ".IS" for k in bist_raw.split(",") if k.strip()]

    print("BIST Taranıyor...")
    data = yf.download(all_stocks, period="2y", interval="1d", auto_adjust=True, progress=False, group_by='ticker')
    
    results = []
    for ticker in all_stocks:
        try:
            df = data[ticker].dropna()
            if len(df) < 201: continue
            
            last_close = df['Close'].iloc[-1]
            df['hlc3'] = (df['High'] + df['Low'] + df['Close']) / 3
            ars_d = calculate_ars(df['hlc3'])
            df_w = df.resample('W').agg({'High':'max', 'Low':'min', 'Close':'last'}).dropna()
            ars_w = calculate_ars((df_w['High'] + df_w['Low'] + df_w['Close']) / 3)
            ars_w_daily = ars_w.reindex(df.index, method='ffill')
            
            bb_mid = df['Close'].rolling(window=200).mean()
            bb_upper = bb_mid + (df['Close'].rolling(window=200).std() * 2)

            results.append([
                ticker.replace(".IS",""), 
                find_cross_up(ars_d, ars_w_daily),
                find_cross_down(ars_d, ars_w_daily),
                find_cross_up(df['Close'], bb_mid),
                find_cross_up(df['Close'], bb_upper)
            ])
        except: continue

    df_res = pd.DataFrame(results, columns=["Hisse", "G↑H", "G↓H", "F↑BB Orta", "F↑BB Üst"])

    # --- SİNYAL AYIKLAMA (Bugün olanlar: (0)) ---
    g_up = df_res[df_res['G↑H'].str.contains("\(0\)", na=False)]['Hisse'].tolist()
    g_down = df_res[df_res['G↓H'].str.contains("\(0\)", na=False)]['Hisse'].tolist()
    f_mid = df_res[df_res['F↑BB Orta'].str.contains("\(0\)", na=False)]['Hisse'].tolist()
    f_upper = df_res[df_res['F↑BB Üst'].str.contains("\(0\)", na=False)]['Hisse'].tolist()

    # --- MESAJ OLUŞTURMA ---
    msg = "📅 *GÜNLÜK KESİŞİM RAPORU*\n----------------------------\n"
    msg += "🟢 *GÜNLÜK ↑ HAFTALIK (ARS):*\n" + (", ".join(g_up) if g_up else "➖ Sinyal Yok") + "\n\n"
    msg += "🔴 *GÜNLÜK ↓ HAFTALIK (ARS):*\n" + (", ".join(g_down) if g_down else "➖ Sinyal Yok") + "\n\n"
    msg += "🔵 *FİYAT ↑ BB ORTA (200):*\n" + (", ".join(f_mid) if f_mid else "➖ Sinyal Yok") + "\n\n"
    msg += "🔥 *FİYAT ↑ BB ÜST:* \n" + (", ".join(f_upper) if f_upper else "➖ Sinyal Yok")

    # --- GÖNDERİM ---
    token = os.getenv('BOT_TOKEN')
    chat_id = os.getenv('MY_CHAT_ID')
    if token and chat_id:
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN)
        print("Rapor Telegram'a gönderildi!")

if __name__ == "__main__":
    asyncio.run(main())
