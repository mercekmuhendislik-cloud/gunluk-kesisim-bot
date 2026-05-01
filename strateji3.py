import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import os
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

warnings.filterwarnings('ignore')

# --- FONKSİYONLAR ---
def calculate_t3(src, length, vf, multiplier):
    def ema(s, l): return s.ewm(span=l, adjust=False).mean()
    e1 = ema(src, length); e2 = ema(e1, length); e3 = ema(e2, length)
    e4 = ema(e3, length); e5 = ema(e4, length); e6 = ema(e5, length)
    vf3, vf2 = vf**3, vf**2
    if multiplier == 3:
        c1, c2, c3, c4 = -vf3, 3*vf2 + 3*vf3, -6*vf2 - 3*vf - 3*vf3, 1 + 3*vf + vf3 + 3*vf2
    else:
        c1, c2, c3, c4 = -vf3, 4*vf2 + 4*vf3, -8*vf2 - 4*vf - 4*vf3, 1 + 4*vf + vf3 + 4*vf2
    return c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3

def calculate_ars_series(df):
    q1, q2 = 3, 1.23
    hlc3 = (df['High'] + df['Low'] + df['Close']) / 3
    q4 = hlc3.ewm(span=q1, adjust=False).mean()
    q5 = np.zeros(len(q4))
    q5[0] = q4.iloc[0]
    for i in range(1, len(q4)):
        p = q5[i-1]; c = q4.iloc[i]
        if c * (1 - q2/100) > p: q5[i] = c * (1 - q2/100)
        elif c * (1 + q2/100) < p: q5[i] = c * (1 + q2/100)
        else: q5[i] = p
    return pd.Series(q5, index=df.index)

def create_link(hisse):
    return f"[{hisse}](https://www.tradingview.com/chart/?symbol=BIST:{hisse})"

async def main():
    bist_raw = "ACSEL,ADEL,ADESE,ADLVY,ADGYO,AFYON,AGHOL,AGESA,AGROT,AHSGY,AHGAZ,AKSFA,AKFK,AKMEN,AKCVR,AKBNK,AKCKM,AKCNS,AKDFA,AKYHO,AKENR,AKFGY,AKFIS,AKFYE,ATEKS,AKSGY,AKMGY,AKSA,AKSEN,AKGRT,AKSUE,AKTVK,ALCAR,ALGYO,ALARK,ALBRK,ALCTL,ALFAS,ALKIM,ALKA,AYCES,ALTNY,ALKLC,ALVES,ANSGR,AEFES,ANHYT,ASUZU,ANGEN,ANELE,ARCLK,ARDYZ,ARENA,ARFYE,ARMGD,ARSAN,ARSVY,ARTMS,ARZUM,ASGYO,ASELS,ASTOR,ATAGY,ATAVK,ATAKP,AGYO,ATLFA,ATSYH,ATLAS,ATATP,AVOD,AVGYO,AVTUR,AVHOL,AVPGY,AYDEM,AYEN,AYES,AYGAZ,AZTEK,BAGFS,BAHKM,BAKAB,BALAT,BALSU,BNTAS,BANVT,BARMA,BSRFK,BASGZ,BASCM,BEGYO,BTCIM,BSOKE,BYDNR,BAYRK,BERA,BRKT,BRKSN,BESLR,BJKAS,BEYAZ,BIENY,BIGTK,BLCYT,BLKOM,BIMAS,BINBN,BIOEN,BRKVY,BRKO,BIGEN,BRLSM,BRMEN,BIZIM,BLUME,BMSTL,BMSCH,BOBET,BORSK,BORLS,BRSAN,BRYAT,BFREN,BOSSA,BRISA,BULGS,BURCE,BURVA,BUCIM,BVSAN,BIGCH,CRFSA,CASA,CEMZY,CEOEM,CCOLA,CONSE,COSMO,CRDFA,CVKMD,CWENE,CGCAM,CAGFA,CMSAN,CANTE,CATES,CLEBI,CELHA,CLKMT,CEMAS,CEMTS,CMBTN,CMENT,CIMSA,CUSAN,DAGI,DAPGM,DARDL,DGATE,DCTTR,DGRVK,DMSAS,DENGE,DZGYO,DERIM,DERHL,DESA,DESPC,DEVA,DNISI,DIRIT,DITAS,DKVRL,DMRGD,DOCO,DOFER,DOHOL,DTRND,DGNMO,DOGVY,ARASE,DOGUB,DGGYO,DOAS,DOKTA,DURDO,DURKN,DUNYH,DNYVA,DYOBY,EBEBK,ECOGR,ECZYT,EDATA,EDIP,EFOR,EGEEN,EGGUB,EGPRO,EGSER,EPLAS,EGEGY,ECILC,EKER,EKIZ,EKOFA,EKOS,EKOVR,EKSUN,ELITE,EMKEL,EMNIS,EMIRV,EKGYO,EMVAR,ENJSA,ENERY,ENKAI,ENSRI,ERBOS,ERCB,EREGL,KIMMR,ERSU,ESCAR,ESCOM,ESEN,ETILR,EUKYO,EUYO,ETYAT,EUHOL,TEZOL,EUREN,EUPWR,EYGYO,FADE,FAIRF,FMIZP,FENER,FLAP,FONET,FROTO,FORMT,FRMPL,FORTE,FRIGO,FZLGY,GWIND,GSRAY,GARFA,GARFL,GRNYO,SNKRN,GEDIK,GEDZA,GLCVY,GENIL,GENTS,GEREL,GZNMI,GIPTA,GMTAS,GESAN,GLYHO,GOODY,GOKNR,GOLTS,GOZDE,GRTHO,GSDDE,GSDHO,GUBRF,GLRYH,GLRMK,GUNDG,GRSEL,SAHOL,HALKF,HLGYO,HLVKS,HRKET,HATEK,HATSN,HDFFL,HDFGS,HEDEF,HEKTS,HKTM,HTTBT,HOROZ,HUBVC,HUNER,HUZFA,HURGZ,ENTRA,ICBCT,ICUGS,INGRM,INVEO,INVES,ISKPL,IEYHO,IDGYO,IHEVA,IHLGM,IHGZT,IHAAS,IHLAS,IHYAY,IMASM,INALR,INDES,INFO,INTEK,INTEM,ISDMR,ISFAK,ISFIN,ISGYO,ISGSY,ISMEN,ISYAT,ISBIR,ISSEN,IZINV,IZENR,IZMDC,IZFAS,JANTS,KFEIN,KLKIM,KLSER,KAPLM,KRDMA,KRDMB,KRDMD,KAREL,KARSN,KRTEK,KARTN,KTLEV,KATMR,KAYSE,KENT,KRVGD,KERVN,KZBGY,KLGYO,KLRHO,KMPUR,KLMSN,KCAER,KCHOL,KOCMT,KLSYN,KNFRT,KONTR,KONYA,KONKA,KGYO,KORDS,KRPLS,KORTS,KOTON,KOPOL,KRGYO,KRSTL,KRONT,KSTUR,KUVVA,KUYAS,KBORU,KZGYO,KUTPO,KTSKR,LIDER,LIDFA,LILAK,LMKDC,LINK,LOGO,LKMNH,LRSHO,LUKSK,LYDHO,LYDYE,MACKO,MAKIM,MAKTK,MANAS,MAGEN,MARKA,MAALT,MRSHL,MRGYO,MARTI,MTRKS,MAVI,MZHLD,MEDTR,MEGMT,MEGAP,MEKAG,MNDRS,MEPET,MERCN,MERIT,MERKO,METRO,MTRYO,MEYSU,MHRGY,MIATK,MGROS,MSGYO,MPARK,MMCAS,MOBTL,MOGAN,MNDTR,MOPAS,EGEPO,NATEN,NTGAZ,NTHOL,NETAS,NIBAS,NUHCM,NUGYO,OBAMS,OBASE,ODAS,ODINE,OFSYM,ONCSM,ONRYT,ORCAY,ORGE,ORMA,OSMEN,OSTIM,OTKAR,OTTO,OYAKC,OYAYO,OYLUM,OZKGY,OZATD,OZGYO,OZRDN,OZSUB,OZYSR,PAMEL,PNLSN,PAGYO,PAPIL,PRFFK,PRDGS,PRKME,PARSN,PASEU,PSGYO,PAHOL,PATEK,PCILT,PGSUS,PEKGY,PENGD,PENTA,PSDTC,PETKM,PKENT,PETUN,PINSU,PNSUT,PKART,PLTUR,POLHO,POLTK,PRZMA,QFINF,QUAGR,RNPOL,RALYH,RAYSG,REEDR,RYGYO,RYSAS,RODRG,ROYAL,RGYAS,RTALB,RUBNS,SAFKR,SANEL,SNICA,SANFM,SANKO,SAMAT,SARKY,SARTN,SASA,SAYAS,SDTTR,SEGMN,SEKUR,SELEC,SELVA,SERNT,SRVGY,SEYKM,SILVR,SNGYO,SMRTG,SMART,SODSN,SOKE,SKTAS,SONME,SNPAM,SUMAS,SUNTK,SURGY,SUWEN,SEKFK,SEGYO,SKBNK,SOKM,TABGD,TNZTP,TARKM,TATGD,TATEN,TAVHL,TEKTU,TKFEN,TKNSA,TMPOL,TRHOL,TGSAS,TOASO,TRGYO,TRMET,TLMAN,TSPOR,TDGYO,TSGYO,TUCLK,TUKAS,TRCAS,TUREX,MARBL,TRILC,TCELL,TRKNT,TMSN,TUPRS,THYAO,PRKAB,TTKOM,TTRAK,TBORG,TURGG,GARAN,HALKB,ISCTR,TSKB,TURSG,SISE,VAKBN,UFUK,ULAS,ULUFA,ULUSE,ULUUN,USAK,ULKER,UNLU,VAKFN,VKGYO,VKFYO,VAKKO,VANGD,VBTYZ,VRGYO,VERUS,VERTU,VESBE,VESTL,VKING,YKBNK,YAPRK,YATAS,YYLGD,YAYLA,YGGYO,YEOTK,YGYO,YYAPI,YESIL,YBTAS,YIGIT,YONGA,YKSLN,YUNSA,ZGYO,ZEDUR,ZRGYO,ZOREN,BINHO"
    selected_stocks = [k.strip().upper() + ".IS" for k in bist_raw.split(",") if k.strip()]
    
    data = yf.download(selected_stocks, period="5y", interval="1d", group_by='ticker', progress=False)
    results = []

    for ticker in selected_stocks:
        try:
            df = data[ticker].dropna()
            if len(df) < 250: continue
            
            # Göstergeler
            ars_d = calculate_ars_series(df)
            df_w = df.resample('W').agg({'High':'max','Low':'min','Close':'last'}).dropna()
            ars_w = calculate_ars_series(df_w).reindex(df.index, method='ffill')
            df_m = df.resample('ME').agg({'High':'max','Low':'min','Close':'last'}).dropna()
            ars_m = calculate_ars_series(df_m).reindex(df.index, method='ffill')
            
            src_t3 = (df['High'] + df['Low'] + 2*df['Close']) / 4
            t_sari = calculate_t3(src_t3, 37, 0.90, 4).iloc[-1]
            
            # KOŞULLAR
            last_close = df['Close'].iloc[-1]
            if last_close <= t_sari or last_close <= ars_d.iloc[-1]: continue
            
            # Sadece BUGÜN kesişenler (Son bar)
            cross_w = (ars_d.iloc[-2] <= ars_w.iloc[-2] and ars_d.iloc[-1] > ars_w.iloc[-1])
            cross_m = (ars_d.iloc[-2] <= ars_m.iloc[-2] and ars_d.iloc[-1] > ars_m.iloc[-1])
            
            if cross_w or cross_m:
                onay = []
                if cross_w: onay.append("Haftalık ✓")
                if cross_m: onay.append("Aylık ✓")
                results.append(f"{create_link(ticker.replace('.IS',''))} ({' + '.join(onay)})")
        except: continue

    msg = "🎯 *MULTI-TIMEFRAME (YENİ KESİŞİM)*\n"
    msg += "----------------------------\n"
    msg += f"🔥 *Bugün Kesişenler:*\n{', '.join(results) if results else '➖ (Bugün yeni kesişim yok)'}\n\n"
    msg += "📝 *Kısaca:* Günlük ARS'nin Haftalık veya Aylık ARS'yi bugün yukarı kestiği taze setup.\n"
    msg += "⚠️ *YASAL UYARI:* Bilgi amaçlıdır, yatırım tavsiyesi değildir."

    bot = Bot(token=os.getenv('BOT_TOKEN'))
    await bot.send_message(chat_id=os.getenv('MY_CHAT_ID'), text=msg, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

if __name__ == "__main__":
    asyncio.run(main())
