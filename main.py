import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import os
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

warnings.filterwarnings('ignore')

# --- TEKNİK FONKSİYONLAR ---
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
    f = fast.tail(5); s = slow.tail(5)
    if len(f) < 5 or len(s) < 5: return "-"
    if f.iloc[-2] <= s.iloc[-2] and f.iloc[-1] > s.iloc[-1]:
        return f"{round(f.iloc[-1], 2)} (0)"
    return "-"

def find_cross_down(fast, slow):
    f = fast.tail(5); s = slow.tail(5)
    if len(f) < 5 or len(s) < 5: return "-"
    if f.iloc[-2] >= s.iloc[-2] and f.iloc[-1] < s.iloc[-1]:
        return f"{round(f.iloc[-1], 2)} (0)"
    return "-"

async def main():
    # 600+ Hisse Listesi
    bist_raw = "ACSEL,ADEL,ADESE,ADGYO,AFYON,AGHOL,AGESA,AGROT,AHGAZ,AKBNK,AKCNS,AKENR,AKFGY,AKFYE,AKGRT,AKMGY,AKSA,AKSEN,ALARK,ALBRK,ALCAR,ALCTL,ALFas,ALKA,ALKIM,ALTNY,ALVES,ANELE,ANGEN,ANHYT,ANSGR,ARCLK,ARDYZ,ARENA,ARSAN,ASELS,ASTOR,ASUZU,ATATP,ATEKS,AVHOL,AVOD,AVPGY,AYDEM,AYEN,AYGAZ,AZTEK,BAGFS,BANVT,BARMA,BASGZ,BAYRK,BEGYO,BERA,BEYAZ,BIENY,BIGCH,BIMAS,BIOEN,BIZIM,BMSCH,BMSTL,BNTAS,BOBET,BORLS,BORSK,BOSSA,BRISA,BRKO,BRKSN,BRMEN,BRSAN,BRYAT,BSOKE,BTCIM,BUCIM,BURCE,BURVA,BVSAN,CANTE,CATES,CCOLA,CELHA,CEMAS,CEMTS,CIMSA,CLEBI,CONSE,COSMO,CVKMD,CWENE,DAGI,DAPGM,DARDL,DCTTR,DENGE,DERHL,DERIM,DESA,DESPC,DEVA,DGNMO,DIRIT,DITAS,DMSAS,DNISI,DOAS,DOCO,DOFER,DOHOL,DOKTA,DURDO,DYOBY,EBEBK,ECILC,ECZYT,EDATA,EDIP,EFORV,EGEEN,EGGUB,EGPRO,EGSER,EKGYO,EKOS,EKSUN,ELITE,EMKEL,ENERY,ENJSA,ENKAI,ENSRI,EPLAS,ERBos,ERCB,EREGL,ERSU,ESCAR,ESCOM,ESEN,EUPWR,EUREN,EYGYO,FADE,FENER,FLAP,FMIZP,FONET,FORMT,FORTE,FROTO,FZLGY,GARAN,GARFA,GEDIK,GEDZA,GENIL,GENTS,GEREL,GESAN,GIPTA,GLCVY,GLRYH,GLYHO,GOKNR,GOLTS,GOODY,GOZDE,GRSEL,GSDHO,GUBRF,GWIND,GZNMI,HALKB,HATEK,HATSN,HDFGS,HEDEF,HEKTS,HKTM,HLGYO,HTTBT,HUNER,HURGZ,ICBCT,IDGYO,IEYHO,IHAAS,IHLGM,IHLAS,IHYAY,IMASM,INDES,INFO,INGRM,INVEO,INVES,ISCTR,ISFIN,ISGYO,ISGSY,ISMEN,ISSEN,ISYAT,IZENR,IZINV,IZMDC,JANTS,KAPLM,KAREL,KARSN,KARTN,KARYE,KATMR,KAYSE,KCAER,KCHOL,KFEIN,KGYO,KIMMR,KLGYO,KLKIM,KLMSN,KLRHO,KLSER,KMPUR,KNFRT,KOCMT,KONKA,KONTR,KONYA,KORDS,KOZAA,KOZAL,KRDMA,KRDMB,KRDMD,KRGYO,KRONT,KRPLS,KRSTL,KRTEK,KSTUR,KTSKR,KUTPO,KUVVA,KUYAS,KZBGY,KZGYO,LIDER,LIDFA,LINK,LMKDC,LOGO,LUKSK,MACKO,MAGEN,MAKIM,MAKTK,MANAS,MARBL,MARKA,MARTI,MAVI,MEDTR,MEGAP,MEKAG,MEPET,MERCN,MERKO,METRO,METUR,MGROS,MIATK,MIPAZ,MMCAS,MNDRS,MOGAN,MPARK,MRGYO,MRSHL,MSGYO,MTRKS,MTRYO,MZHLD,NATEN,NETAS,NIBAS,NOHOL,NTGAZ,NUGYO,NUHCM,OBASE,OBAMS,ODAS,ODINE,OFSYM,ONCSM,ORCAY,ORGE,ORMA,OSMEN,OSTIM,OTKAR,OTTO,OYAKC,OYAYO,OYLUM,OZATD,OZGYO,OZKGY,OZRDN,OZSUB,OZYSR,PAGYO,PAMEL,PAPIL,PARSN,PASEU,PATEK,PCILT,PEGYO,PEKGY,PENGD,PENTA,PETKM,PETUN,PGSUS,PINSU,PKART,PKENT,PLTUR,PNLSN,PNSUT,POLHO,POLTK,PRDGS,PRKAB,PRKME,PRZMA,PSGYO,QUAGR,RALYH,RAYSG,REEDR,RNPOL,RODRG,ROYAL,RTALB,RUBNS,RYGYO,RYSAS,SAFKR,SAHOL,SAMAT,SANEL,SANFM,SANKO,SARKY,SASA,SAYAS,SDTTR,SEGMN,SEGYO,SEKUR,SELEC,SELVA,SEYKM,SILVR,SISE,SKBNK,SKTAS,SMART,SMRTG,SNGYO,SNICA,SNKRN,SNPAM,SODSN,SOKM,SONME,SRVGY,SUMAS,SUNTK,SURGY,SUWEN,TABGD,TARKM,TATEN,TATGD,TAVHL,TBORG,TCELL,TDGYO,TEKTU,TERA,TETMT,TEZOL,THYAO,TKFEN,TKNSA,TLMAN,TMPOL,TMSN,TNZTP,TOASO,TRCAS,TRGYO,TRILC,TSKB,TSPOR,TTKOM,TTRAK,TUCLK,TUKAS,TUPRS,TURGG,TURSG,UFUK,ULAS,ULKER,ULUFA,ULUSE,ULUUN,UNLU,USAK,VAKBN,VAKFN,VAKKO,VANGD,VBTYZ,VERTU,VERUS,VESBE,VESTL,VKGYO,VKING,YEOTK,YESIL,YGGYO,YGYO,YIGIT,YKBNK,YKSLN,YONGA,YUNSA,YYAPI,YYLGD,ZEDUR,ZGYO,ZOREN,ZRGYO"
    tickers = [t.strip() + ".IS" for t in bist_raw.split(",")]

    print(f"{len(tickers)} hisse indiriliyor...")
    data = yf.download(tickers, period="2y", interval="1d", auto_adjust=True, progress=False, group_by='ticker')
    
    res = []
    for t in tickers:
        try:
            df = data[t].dropna()
            if len(df) < 100: continue
            df['hlc3'] = (df['High'] + df['Low'] + df['Close']) / 3
            ars_d = calculate_ars(df['hlc3'])
            df_w = df.resample('W').agg({'High':'max', 'Low':'min', 'Close':'last'}).dropna()
            ars_w = calculate_ars((df_w['High'] + df_w['Low'] + df_w['Close']) / 3).reindex(df.index, method='ffill')
            bb_mid = df['Close'].rolling(window=200).mean()
            
            res.append({
                "H": t.replace(".IS",""),
                "G_H_UP": find_cross_up(ars_d, ars_w),
                "G_H_DOWN": find_cross_down(ars_d, ars_w),
                "F_BB": find_cross_up(df['Close'], bb_mid)
            })
        except: continue

    df_res = pd.DataFrame(res)
    g_up = df_res[df_res['G_H_UP'].str.contains("\(0\)", na=False)]['H'].tolist()
    g_down = df_res[df_res['G_H_DOWN'].str.contains("\(0\)", na=False)]['H'].tolist()
    f_bb = df_res[df_res['F_BB'].str.contains("\(0\)", na=False)]['H'].tolist()

    msg = "📅 *GÜNLÜK KESİŞİM RAPORU (TAM LİSTE)*\n"
    msg += "----------------------------\n"
    msg += f"🟢 *ARS G↑H (Bugün):*\n`{', '.join(g_up) if g_up else '➖'}`\n\n"
    msg += f"🔴 *ARS G↓H (Bugün):*\n`{', '.join(g_down) if g_down else '➖'}`\n\n"
    msg += f"🔵 *FİYAT ↑ BB ORTA (200):*\n`{', '.join(f_bb) if f_bb else '➖'}`"

    bot = Bot(token=os.getenv('BOT_TOKEN'))
    await bot.send_message(chat_id=os.getenv('MY_CHAT_ID'), text=msg, parse_mode=ParseMode.MARKDOWN)

if __name__ == "__main__":
    asyncio.run(main())
