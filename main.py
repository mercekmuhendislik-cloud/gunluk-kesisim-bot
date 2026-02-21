import yfinance as yf
import pandas as pd
import numpy as np
import os
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

# GitHub Secrets'tan bilgileri çekiyoruz
TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('MY_CHAT_ID')

# Senin ARS ve Analiz fonksiyonların buraya gelecek (Yukarıda verdiğin fonksiyonlar)
# ... (calculate_ars, find_cross_up vb. fonksiyonlarını buraya ekle) ...

async def rapor_gonder():
    # Burada senin analiz döngün çalışacak ve df_res oluşacak
    # (Yukarıda paylaştığın analiz kodunun tamamını buraya entegre et)
    
    # Sinyal Gruplama
    g_up_h = df_res[df_res['G↑H'].str.contains("\(0\)", na=False)]['Hisse'].tolist()
    g_down_h = df_res[df_res['G↓H'].str.contains("\(0\)", na=False)]['Hisse'].tolist()
    f_up_bb_mid = df_res[df_res['F↑BB Orta'].str.contains("\(0\)", na=False)]['Hisse'].tolist()
    f_up_bb_upper = df_res[df_res['F↑BB Üst'].str.contains("\(0\)", na=False)]['Hisse'].tolist()

    msg = "📅 *GÜNLÜK KESİŞİM RAPORU*\n"
    msg += "----------------------------\n\n"
    msg += "🟢 *GÜNLÜK ↑ HAFTALIK*\n" + (", ".join(g_up_h) if g_up_h else "➖") + "\n\n"
    msg += "🔴 *GÜNLÜK ↓ HAFTALIK*\n" + (", ".join(g_down_h) if g_down_h else "➖") + "\n\n"
    msg += "🔵 *FİYAT ↑ BB ORTA*\n" + (", ".join(f_up_bb_mid) if f_up_bb_mid else "➖") + "\n\n"
    msg += "🔥 *FİYAT ↑ BB ÜST*\n" + (", ".join(f_up_bb_upper) if f_up_bb_upper else "➖")

    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode=ParseMode.MARKDOWN)

if __name__ == "__main__":
    asyncio.run(rapor_gonder())
