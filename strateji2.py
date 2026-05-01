import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import os
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

warnings.filterwarnings('ignore')

def calculate_ars(src_series):
    ema1 = src_series.ewm(span=3, adjust=False).mean()
    band = 1.23 / 100
    ars_values = np.zeros(len(ema1))
    ars_values[0] = ema1.iloc[0]
    for i in range(1, len(ema1)):
        p = ars_values[i-1]; c = ema1.iloc[i]
        if (c * (1 - band)) > p: ars_values[i] = c * (1 - band)
        elif (c * (1 + band)) < p: ars_values[i] = c * (1 + band)
        else: ars_values[i] = p
    return pd.Series(ars_values, index=src_series.index)

def create_link(hisse):
    return f"[{hisse}](https://www.tradingview.com/chart/?symbol=BIST:{hisse})"

async def main():
    bist_raw = "ACSEL, ADEL, ADESE, ADLVY, ADGYO, AFYON, AGHOL, AGESA, AGROT, AHSGY, AHGAZ, AKSFA, AKFK, AKMEN, AKCVR, AKBNK, AKCKM, AKCNS, AKDFA, AKYHO, AKENR, AKFGY, AKFIS, AKFYE, ATEKS, AKSGY, AKMGY, AKSA, AKSEN, AKGRT, AKSUE, AKTVK, ALCAR, ALGYO, ALARK, ALBRK, ALCTL, ALFAS, ALKIM, ALKA, AYCES, ALTNY, ALKLC, ALVES, ANSGR, AEFES, ANHYT, ASUZU, ANGEN, ANELE, ARCLK, ARDYZ, ARENA, ARFYE, ARMGD, ARSAN, ARSVY, ARTMS, ARZUM, ASGYO, ASELS, ASTOR, ATAGY, ATAVK, ATAKP, AGYO, ATLFA, ATSYH, ATLAS, ATATP, AVOD, AVGYO, AVTUR, AVHOL, AVPGY, AYDEM, AYEN, AYES, AYGAZ, AZTEK, BAGFS, BAHKM, BAKAB, BALAT, BALSU, BNTAS, BANVT, BARMA, BSRFK, BASGZ, BASCM, BEGYO, BTCIM, BSOKE, BYDNR, BAYRK, BERA, BRKT, BRKSN, BESLR, BJKAS, BEYAZ, BIENY, BIGTK, BLCYT, BLKOM, BIMAS, BINBN, BIOEN, BRKVY, BRKO, BIGEN, BRLSM, BRMEN, BIZIM, BLUME, BMSTL, BMSCH, BOBET, BORSK, BORLS, BRSAN, BRYAT, BFREN, BOSSA, BRISA, BULGS, BURCE, BURVA, BUCIM, BVSAN, BIGCH, CRFSA, CASA, CEMZY, CEOEM, CCOLA, CONSE, COSMO, CRDFA, CVKMD, CWENE, CGCAM, CAGFA, CMSAN, CANTE, CATES, CLEBI, CELHA, CLKMT, CEMAS, CEMTS, CMBTN, CMENT, CIMSA, CUSAN, DAGI, DAPGM, DARDL, DGATE, DCTTR, DGRVK, DMSAS, DENGE, DZGYO, DERIM, DERHL, DESA, DESPC, DEVA, DNISI, DIRIT, DITAS, DKVRL, DMRGD, DOCO, DOFER, DOHOL, DTRND, DGNMO, DOGVY, ARASE, DOGUB, DGGYO, DOAS, DOKTA, DURDO, DURKN, DUNYH, DNYVA, DYOBY, EBEBK, ECOGR, ECZYT, EDATA, EDIP, EFOR, EGEEN, EGGUB, EGPRO, EGSER, EPLAS, EGEGY, ECILC, EKER, EKIZ, EKOFA, EKOS, EKOVR, EKSUN, ELITE, EMKEL, EMNIS, EMIRV, EKGYO, EMVAR, ENJSA, ENERY, ENKAI, ENSRI, ERBOS, ERCB, EREGL, KIMMR, ERSU, ESCAR, ESCOM, ESEN, ETILR, EUKYO, EUYO, ETYAT, EUHOL, TEZOL, EUREN, EUPWR, EYGYO, FADE, FAIRF, FMIZP, FENER, FLAP, FONET, FROTO, FORMT, FRMPL, FORTE, FRIGO, FZLGY, GWIND, GSRAY, GARFA, GARFL, GRNYO, SNKRN, GEDIK, GEDZA, GLCVY, GENIL, GENTS, GEREL, GZNMI, GIPTA, GMTAS, GESAN, GLYHO, GOODY, GOKNR, GOLTS, GOZDE, GRTHO, GSDDE, GSDHO, GUBRF, GLRYH, GLRMK, GUNDG, GRSEL, SAHOL, HALKF, HLGYO, HLVKS, HRKET, HATEK, HATSN, HDFFL, HDFGS, HEDEF, HEKTS, HKTM, HTTBT, HOROZ, HUBVC, HUNER, HUZFA, HURGZ, ENTRA, ICBCT, ICUGS, INGRM, INVEO, INVES, ISKPL, IEYHO, IDGYO, IHEVA, IHLGM, IHGZT, IHAAS, IHLAS, IHYAY, IMASM, INALR, INDES, INFO, INTEK, INTEM, ISDMR, ISFAK, ISFIN, ISGYO, ISGSY, ISMEN, ISYAT, ISBIR, ISSEN, IZINV, IZENR, IZMDC, IZFAS, JANTS, KFEIN, KLKIM, KLSER, KAPLM, KRDMA, KRDMB, KRDMD, KAREL, KARSN, KRTEK, KARTN, KTLEV, KATMR, KAYSE, KENT, KRVGD, KERVN, KZBGY, KLGYO, KLRHO, KMPUR, KLMSN, KCAER, KCHOL, KOCMT, KLSYN, KNFRT, KONTR, KONYA, KONKA, KGYO, KORDS, KRPLS, KORTS, KOTON, KOPOL, KRGYO, KRSTL, KRONT, KSTUR, KUVVA, KUYAS, KBORU, KZGYO, KUTPO, KTSKR, LIDER, LIDFA, LILAK, LMKDC, LINK, LOGO, LKMNH, LRSHO, LUKSK, LYDHO, LYDYE, MACKO, MAKIM, MAKTK, MANAS, MAGEN, MARKA, MAALT, MRSHL, MRGYO, MARTI, mtrks, MAVI, MZHLD, MEDTR, MEGMT, MEGAP, MEKAG, MNDRS, MEPET, MERCN, MERIT, MERKO, METRO, MTRYO, MEYSU, MHRGY, MIATK, MGROS, MSGYO, MPARK, MMCAS, MOBTL, MOGAN, MNDTR, MOPAS, EGEPO, NATEN, NTGAZ, NTHOL, NETAS, NIBAS, NUHCM, NUGYO, OBAMS, OBASE, ODAS, ODINE, OFSYM, ONCSM, ONRYT, ORCAY, ORGE, ORMA, OSMEN, OSTIM, OTKAR, OTTO, OYAKC, OYAYO, OYLUM, OZKGY, OZATD, OZGYO, OZRDN, OZSUB, OZYSR, PAMEL, PNLSN, PAGYO, PAPIL, PRFFK, PRDGS, PRKME, PARSN, PASEU, PSGYO, PAHOL, PATEK, PCILT, PGSUS, PEKGY, PENGD, PENTA, PSDTC, PETKM, PKENT, PETUN, PINSU, PNSUT, PKART, PLTUR, POLHO, POLTK, PRZMA, QFINF, QUAGR, RNPOL, RALYH, RAYSG, REEDR, RYGYO, RYSAS, RODRG, ROYAL, RGYAS, RTALB, RUBNS, SAFKR, SANEL, SNICA, SANFM, SANKO, SAMAT, SARKY, SARTN, SASA, SAYAS, SDTTR, SEGMN, SEKUR, SELEC, SELVA, SERNT, SRVGY, SEYKM, SILVR, SNGYO, SMRTG, SMART, SODSN, SOKE, SKTAS, SONME, SNPAM, SUMAS, SUNTK, SURGY, SUWEN, SEKFK, SEGYO, SKBNK, SOKM, TABGD, TNZTP, TARKM, TATGD, TATEN, TAVHL, TEKTU, TKFEN, TKNSA, TMPOL, TRHOL, TGSAS, TOASO, TRGYO, TRMET, TLMAN, TSPOR, TDGYO, TSGYO, TUCLK, TUKAS, TRCAS, TUREX, MARBL, TRILC, TCELL, TRKNT, TMSN, TUPRS, THYAO, PRKAB, TTKOM, TTRAK, TBORG, TURGG, GARAN, HALKB, ISCTR, TSKB, TURSG, SISE, VAKBN, UFUK, ULAS, ULUFA, ULUSE, ULUUN, USAK, ULKER, UNLU, VAKFN, VKGYO, VKFYO, VAKKO, VANGD, VBTYZ, VRGYO, VERUS, VERTU, VESBE, VESTL, VKING, YKBNK, YAPRK, YATAS, YYLGD, YAYLA, YGGYO, YEOTK, YGYO, YYAPI, YESIL, YBTAS, YIGIT, YONGA, YKSLN, YUNSA, ZGYO, ZEDUR, ZRGYO, ZOREN, BINHO"
    all_stocks = [k.strip() + ".IS" for k in bist_raw.replace("\n", "").split(",") if k.strip()]
    
    data = yf.download(all_stocks, period="1y", interval="1d", auto_adjust=True, progress=False, group_by='ticker')
    found_stocks = []

    for ticker in all_stocks:
        try:
            df = data[ticker].dropna()
            if len(df) < 60: continue
            df['hlc3'] = (df['High'] + df['Low'] + df['Close']) / 3
            ars_series = calculate_ars(df['hlc3'])
            last_close = df['Close'].iloc[-1]
            last_ars = ars_series.iloc[-1]

            if last_close > last_ars:
                lookback = df.tail(60)
                ars_lookback = ars_series.tail(60)
                under_ars_found = False
                break_price = 0
                min_price_after_break = float('inf')

                for i in range(len(lookback)-2, -1, -1):
                    price = lookback['Close'].iloc[i]; ars_val = ars_lookback.iloc[i]
                    if price < ars_val:
                        under_ars_found = True
                        if lookback['Low'].iloc[i] < min_price_after_break: min_price_after_break = lookback['Low'].iloc[i]
                    if under_ars_found and price >= ars_val:
                        break_price = price
                        break

                if under_ars_found and break_price > 0:
                    drop = ((min_price_after_break / break_price) - 1) * 100
                    bar_count = -1
                    for j in range(1, 6):
                        if df['Close'].iloc[-j] > ars_series.iloc[-j] and df['Close'].iloc[-j-1] <= ars_series.iloc[-j-1]:
                            bar_count = j - 1
                            break
                    if drop <= -20 and bar_count != -1:
                        found_stocks.append(create_link(ticker.replace(".IS","")))
        except: continue

    msg = "💎 *PRKAB TİPİ DÖNÜŞ TARAMASI*\n"
    msg += "----------------------------\n"
    msg += f"🚀 *Sinyal Verenler:*\n{', '.join(found_stocks) if found_stocks else '➖ (Bugün sinyal yok)'}\n\n"
    msg += "📝 *Kısaca:* Kırılım → sert düşüş → yeniden toparlanma formasyonu.\n"
    msg += "⚠️ *YASAL UYARI:* Bilgi amaçlıdır, yatırım tavsiyesi değildir."

    bot = Bot(token=os.getenv('BOT_TOKEN'))
    await bot.send_message(chat_id=os.getenv('MY_CHAT_ID'), text=msg, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

if __name__ == "__main__":
    asyncio.run(main())
