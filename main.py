import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import os
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

warnings.filterwarnings('ignore')

# --- 1. TEKNİK HESAPLAMA FONKSİYONLARI ---
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
            return f"{round(f.iloc[i], 2)} (0)" if i == len(f)-1 else f"{round(f.iloc[i], 2)} ({len(f)-1-i})"
    return "-"

# --- 2. ANA TARAMA VE MESAJ GÖNDERME ---
async def tarama_ve_gonder():
    # Hisse listesi (Kodun kalbi burada)
    bist_raw = "ACSEL, ADEL, ADESE, AGHOL, AGESA, AGROT, AHGAZ, AKBNK, AKCNS, AKSA, AKSEN, ALARK, ALBRK, ALFAS, ALKIM, ANGEN, ARCLK, ARDYZ, ASELS, ASTOR, AYDEM, AYGAZ, BAGFS, BANVT, BERA, BIMAS, BIOEN, BOBET, BRSAN, BRYAT, BUCIM, CANTE, CCOLA, CIMSA, CWENE, DOAS, DOHOL, EGEEN, EKGYO, ENJSA, ENKAI, EREGL, EUHOL, EUPWR, FROTO, GARAN, GESAN, GLYHO, GOLTS, GOZDE, GSDHO, GUBRF, HALKB, HEKTS, HUBVC, IEYHO, IHLGM, IHLAS, INGRM, INVEO, ISCTR, ISGYO, ISMEN, JANTS, KARDMD, KAREL, KARSN, KAYSE, KCAER, KCHOL, KLKIM, KONTR, KONYA, KORDS, KOZAA, KOZAL, KRDMD, LOGO, MAVI, MEDTR, MGROS, MIATK, MPARK, NATEN, NETAS, ODAS, OTKAR, OYAKC, PASEU, PGSUS, PETKM, QUAGR, REEDR, SAHOL, SASA, SAYAS, SDTTR, SISE, SKBNK, SOKM, TARKM, TAVHL, TCELL, THYAO, TKFEN, TKNSA, TOASO, TSKB, TSPOR, TTKOM, TTRAK, TUKAS, TUPRS, TURSG, ULKER, VAKBN, VESBE, VESTL, YEOTK, YKBNK, ZOREN"
    tickers = [t.strip() + ".IS" for t in bist_raw.split(",")]

    print("Veriler indiriliyor...")
    data = yf.download(tickers, period="2y", interval="1d", auto_adjust=True, progress=False, group_by='ticker')
    
    results = []
    for ticker in tickers:
        try:
            df = data[ticker].dropna()
            if len(df) < 100: continue
            
            # ARS Hesaplamaları
            df['hlc3'] = (df['High'] + df['Low'] + df['Close']) / 3
            ars_d = calculate_ars(df['hlc3'])
            df_w = df.resample('W').agg({'High':'max', 'Low':'min', 'Close':'last'}).dropna()
            ars_w = calculate_ars((df_w['High'] + df_w['Low'] + df_w['Close']) / 3).reindex(df.index, method='ffill')
            
            # Bollinger ve Kesişimler
            bb_mid = df['Close'].rolling(window=200).mean()
            bb_upper = bb_mid + (df['Close'].rolling(window=200).std() * 2)
            
            results.append({
                "Hisse": ticker.replace(".IS", ""),
                "G_H": find_cross_up(ars_d, ars_w),
                "BB_Orta": find_cross_up(df['Close'], bb_mid),
                "BB_Ust": find_cross_up(df['Close'], bb_upper)
            })
        except: continue

    df_res = pd.DataFrame(results)

    # Sinyal Filtreleme (Sadece bugün (0) olanlar)
    g_up = df_res[df_res['G_H'].str.contains("\(0\)", na=False)]['Hisse'].tolist()
    bb_m = df_res[df_res['BB_Orta'].str.contains("\(0\)", na=False)]['Hisse'].tolist()
    bb_u = df_res[df_res['BB_Ust'].str.contains("\(0\)", na=False)]['Hisse'].tolist()

    # Mesaj Oluşturma
    msg = "📅 *GÜNLÜK KESİŞİM RAPORU*\n----------------------------\n"
    msg += f"🟢 *ARS G↑H:* {', '.join(g_up) if g_up else '➖'}\n"
    msg += f"🔵 *FİYAT ↑ BB ORTA:* {', '.join(bb_m) if bb_m else '➖'}\n"
    msg += f"🔥 *FİYAT ↑ BB ÜST:* {', '.join(bb_u) if bb_u else '➖'}"

    # Gönderim
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    await bot.send_message(chat_id=os.getenv('MY_CHAT_ID'), text=msg, parse_mode=ParseMode.MARKDOWN)

if __name__ == "__main__":
    asyncio.run(tarama_ve_gonder())
