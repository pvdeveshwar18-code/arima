import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import pytz
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import concurrent.futures
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import xml.etree.ElementTree as ET
import urllib.request

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(page_title="XERCES // QUANT ENGINE", page_icon="⚡", layout="wide")

IST = pytz.timezone("Asia/Kolkata")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Space+Mono&family=Inter:wght@300;400;500;600&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:radial-gradient(circle at 50% 0%,#0a192f 0%,#020813 100%) !important;color:#e2e8f0 !important;}
section[data-testid="stSidebar"]{background-color:rgba(3,11,24,0.95) !important;border-right:1px solid rgba(0,200,255,0.15) !important;}
.xerces-title{font-family:'Orbitron',sans-serif;font-weight:900;font-size:2.2rem;background:linear-gradient(90deg,#00c8ff,#00e87a);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:3px;margin:0;}
.telemetry-tag{font-family:'Space Mono',monospace;color:#4a7090;font-size:11px;letter-spacing:1px;}
.section-header{font-family:'Orbitron',sans-serif;color:#00c8ff;font-size:12px;letter-spacing:1px;margin-top:12px;margin-bottom:8px;}
.glass-card{background:rgba(7,18,32,0.65);border:1px solid rgba(0,200,255,0.15);border-radius:6px;padding:12px 16px;margin-bottom:10px;backdrop-filter:blur(4px);}
.glass-label{font-family:'Space Mono',monospace;color:#6a90aa;font-size:10px;margin:0;text-transform:uppercase;letter-spacing:1px;}
.glass-value{font-family:'Orbitron',sans-serif;font-size:1.35rem;font-weight:700;margin-top:2px;}
div[data-baseweb="tab-list"]{gap:4px;}
button[data-baseweb="tab"]{font-family:'Space Mono',monospace !important;border-radius:4px !important;background:rgba(10,25,40,0.4) !important;color:#5a80a0 !important;border:1px solid rgba(0,200,255,0.05) !important;padding:0.4rem 0.9rem !important;}
button[data-baseweb="tab"][aria-selected="true"]{border-color:#00c8ff !important;color:#00c8ff !important;background:rgba(13,32,53,0.75) !important;}
.signal-buy{color:#00e87a;font-family:'Orbitron',sans-serif;font-weight:700;font-size:1.4rem;}
.signal-sell{color:#ff3355;font-family:'Orbitron',sans-serif;font-weight:700;font-size:1.4rem;}
.signal-hold{color:#ffcc00;font-family:'Orbitron',sans-serif;font-weight:700;font-size:1.4rem;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# COMPLETE NSE STOCK UNIVERSE — 500+ STOCKS
# ══════════════════════════════════════════════════════════════
SECTORS = {
    "🏦 Banking & Finance": [
        ("HDFC Bank","HDFCBANK"),("ICICI Bank","ICICIBANK"),("SBI","SBIN"),("Kotak Mahindra Bank","KOTAKBANK"),
        ("Axis Bank","AXISBANK"),("IndusInd Bank","INDUSINDBK"),("Bank of Baroda","BANKBARODA"),
        ("PNB","PNB"),("Canara Bank","CANBK"),("Union Bank","UNIONBANK"),("Bank of India","BANKINDIA"),
        ("Indian Bank","INDIANB"),("UCO Bank","UCOBANK"),("Central Bank","CENTRALBK"),("IOB","IOB"),
        ("Federal Bank","FEDERALBNK"),("RBL Bank","RBLBANK"),("Yes Bank","YESBANK"),
        ("IDFC First Bank","IDFCFIRSTB"),("Bandhan Bank","BANDHANBNK"),("AU Small Finance Bank","AUBANK"),
        ("Equitas Small Finance","EQUITASBNK"),("Ujjivan Small Finance","UJJIVANSFB"),
        ("City Union Bank","CUB"),("Karur Vysya Bank","KARURVYSYA"),("South Indian Bank","SOUTHBANK"),
        ("Dhanlaxmi Bank","DHANBANK"),("Karnataka Bank","KTKBANK"),("Lakshmi Vilas Bank","LVBANK"),
        ("Bajaj Finance","BAJFINANCE"),("Bajaj Finserv","BAJAJFINSV"),("Cholamandalam Finance","CHOLAFIN"),
        ("Muthoot Finance","MUTHOOTFIN"),("Manappuram Finance","MANAPPURAM"),("L&T Finance","LTF"),
        ("Shriram Finance","SHRIRAMFIN"),("Piramal Enterprises","PEL"),("HDFC AMC","HDFCAMC"),
        ("Nippon India AMC","NAM-INDIA"),("UTI AMC","UTIAMC"),("Aditya Birla AMC","ABSLAMC"),
        ("SBI Cards","SBICARD"),("SBI Life Insurance","SBILIFE"),("HDFC Life","HDFCLIFE"),
        ("LIC India","LICI"),("Star Health Insurance","STARHEALTH"),("New India Assurance","NIACL"),
        ("General Insurance Corp","GICRE"),("ICICI Prudential Life","ICICIPRULI"),
        ("ICICI Lombard","ICICIGI"),("Max Financial","MFSL"),("Five Star Business","FIVESTAR"),
    ],
    "💻 IT & Technology": [
        ("TCS","TCS"),("Infosys","INFY"),("HCL Technologies","HCLTECH"),("Wipro","WIPRO"),
        ("Tech Mahindra","TECHM"),("LTIMindtree","LTIM"),("Mphasis","MPHASIS"),("Coforge","COFORGE"),
        ("Persistent Systems","PERSISTENT"),("L&T Technology","LTTS"),("Tata Elxsi","TATAELXSI"),
        ("KPIT Technologies","KPITTECH"),("Zensar Technologies","ZENSARTECH"),("Mastek","MASTEK"),
        ("Hexaware","HEXAWARE"),("Birlasoft","BSOFT"),("Intellect Design","INTELLECT"),
        ("Cyient","CYIENT"),("NIIT Technologies","NIITMTS"),("Sonata Software","SONATSOFTW"),
        ("Happiest Minds","HAPPSTMNDS"),("Tanla Platforms","TANLA"),("Firstsource Solutions","FSL"),
        ("Newgen Software","NEWGEN"),("Ramco Systems","RAMCOSYS"),("Saksoft","SAKSOFT"),
        ("Nucleus Software","NUCLEUSSOFT"),("KFIN Technologies","KFINTECH"),("Angel One","ANGELONE"),
        ("Route Mobile","ROUTE"),("Nazara Technologies","NAZARA"),("Netweb Technologies","NETWEB"),
    ],
    "🏭 Industrials & Capital Goods": [
        ("Larsen & Toubro","LT"),("Siemens India","SIEMENS"),("ABB India","ABB"),("Bharat Electronics","BEL"),
        ("HAL","HAL"),("BEML","BEML"),("Thermax","THERMAX"),("Cummins India","CUMMINSIND"),
        ("Bharat Forge","BHARATFORG"),("Ramkrishna Forgings","RKFORGE"),("Escorts Kubota","ESCORTS"),
        ("GNFC","GNFC"),("Carborundum Universal","CARBORUNIV"),("AIA Engineering","AIAENG"),
        ("Timken India","TIMKEN"),("Schaeffler India","SCHAEFFLER"),("SKF India","SKFINDIA"),
        ("Grindwell Norton","GRINDWELL"),("Elgi Equipments","ELGIEQUIP"),("Kirloskar Brothers","KIRLOSBROS"),
        ("Kirloskar Electric","KIRLOSELE"),("KSB","KSB"),("Ingersoll Rand","INGERRAND"),
        ("Atlas Copco","ATLASCOP"),("Kennametal","KENNAMET"),("Voltamp Transformers","VOLTAMP"),
        ("Transformers & Rectifiers","TRIL"),("Sterling Wilson","SWSOLAR"),("Va Tech Wabag","WABAG"),
        ("NBCC","NBCC"),("NCC","NCC"),("KEC International","KEC"),("Kalpataru Projects","KPIL"),
        ("G R Infraprojects","GRINFRA"),("ITD Cementation","ITDCEM"),("PNC Infratech","PNCINFRA"),
        ("H.G. Infra","HGINFRA"),("Ashoka Buildcon","ASHOKA"),("IRB Infrastructure","IRB"),
    ],
    "⚡ Energy & Power": [
        ("Reliance Industries","RELIANCE"),("ONGC","ONGC"),("BPCL","BPCL"),("IOC","IOC"),
        ("HPCL","HPCL"),("GAIL India","GAIL"),("Petronet LNG","PETRONET"),("Castrol India","CASTROLIND"),
        ("NTPC","NTPC"),("Power Grid Corp","POWERGRID"),("Tata Power","TATAPOWER"),
        ("Adani Green","ADANIGREEN"),("Adani Enterprises","ADANIENT"),("JSW Energy","JSWENERGY"),
        ("Torrent Power","TORNTPOWER"),("NHPC","NHPC"),("SJVN","SJVN"),("CESC","CESC"),
        ("Inox Wind","INOXWIND"),("Suzlon Energy","SUZLON"),("Orient Green Power","ORIENTGREEN"),
        ("IREDA","IREDA"),("PFC","PFC"),("REC","RECLTD"),("IGL","IGL"),
        ("Gujarat Gas","GUJGASLTD"),("Adani Total Gas","ATGL"),("Mahanagar Gas","MGL"),
        ("Reliance Power","RPOWER"),("Jaiprakash Power","JPPOWER"),("GIPCL","GIPCL"),
        ("CPCL","CPCL"),("Mangalore Refinery","MRPL"),("Chennai Petroleum","CHENNPETRO"),
    ],
    "🚗 Auto & Auto Ancillaries": [
        ("Maruti Suzuki","MARUTI"),("Tata Motors","TATAMOTORS"),("M&M","M&M"),
        ("Bajaj Auto","BAJAJ-AUTO"),("Hero MotoCorp","HEROMOTOCO"),("Eicher Motors","EICHERMOT"),
        ("TVS Motor","TVSMOTOR"),("Ashok Leyland","ASHOKLEY"),
        ("Force Motors","FORCEMOT"),("SML Isuzu","SMLISUZU"),
        ("Apollo Tyres","APOLLOTYRE"),("MRF","MRF"),("CEAT","CEATLTD"),
        ("Balkrishna Industries","BALKRISIND"),("Bosch India","BOSCHLTD"),("Motherson Sumi","MOTHERSON"),
        ("Minda Industries","MINDAIND"),("Minda Corp","MINDACORP"),("Suprajit Engineering","SUPRAJIT"),
        ("Endurance Technologies","ENDURANCE"),("Gabriel India","GABRIEL"),("Jamna Auto","JAMNAAUTO"),
        ("Wabco India","WABCOINDIA"),("ZF Commercial","ZFCVINDIA"),("Sona BLW Precision","SONACOMS"),
        ("Uno Minda","UNOMINDA"),("Samvardhana Motherson","MOTHERSON"),("Fiem Industries","FIEMIND"),
        ("Sandhar Technologies","SANDHAR"),("Craftsman Automation","CRAFTSMAN"),("Ramkrishna Forgings","RKFORGE"),
        ("Bharat Forge","BHARATFORG"),("Hi-Tech Pipes","HITECH"),("Schaeffler India","SCHAEFFLER"),
    ],
    "💊 Pharma & Healthcare": [
        ("Sun Pharma","SUNPHARMA"),("Dr. Reddy's","DRREDDY"),("Cipla","CIPLA"),("Lupin","LUPIN"),
        ("Biocon","BIOCON"),("Alkem Labs","ALKEM"),("Torrent Pharma","TORNTPHARM"),
        ("Abbott India","ABBOTINDIA"),("Pfizer India","PFIZER"),("Sanofi India","SANOFI"),
        ("Divi's Laboratories","DIVISLAB.NS"),("Aurobindo Pharma","AUROPHARMA"),("Zydus Lifesciences","ZYDUSLIFE"),
        ("Ipca Laboratories","IPCALAB"),("Natco Pharma","NATCOPHARM"),("Glenmark Pharma","GLENMARK"),
        ("Mankind Pharma","MANKIND"),("Ajanta Pharma","AJANTPHARM"),("JB Chemicals","JBCHEPHARM"),
        ("FDC Limited","FDC"),("Piramal Pharma","PPLPHARMA"),("Suven Pharma","SUVENPHAR"),
        ("Laurus Labs","LAURUSLABS"),("Granules India","GRANULES"),("Aarti Drugs","AARTIDRUGS"),
        ("Bliss GVS Pharma","BLISSGVS"),("Caplin Point","CAPLIPOINT"),("Shilpa Medicare","SHILPAMED"),
        ("Apollo Hospitals","APOLLOHOSP"),("Max Healthcare","MAXHEALTH"),("Fortis Healthcare","FORTIS"),
        ("Narayana Hrudayalaya","NH"),("Medanta","MEDANTA"),("HCG Oncology","HCG"),
        ("Vijaya Diagnostic","VIJAYA"),("Krsnaa Diagnostics","KRSNAA"),("Metropolis Healthcare","METROPOLIS"),
        ("Dr. Lal Path Labs","LALPATHLAB"),("Thyrocare","THYROCARE"),
    ],
    "🏗️ Metals & Mining": [
        ("Tata Steel","TATASTEEL"),("JSW Steel","JSWSTEEL"),("Hindalco","HINDALCO"),
        ("Vedanta","VEDL"),("Hindustan Zinc","HINDZINC"),("National Aluminium","NATIONALUM"),
        ("SAIL","SAIL"),("Coal India","COALINDIA"),("NMDC","NMDC"),("Jindal Steel","JINDALSTEL"),
        ("APL Apollo Tubes","APLAPOLLO"),("Ratnamani Metals","RATNAMANI"),
        ("Maharashtra Seamless","MAHSEAMLES"),("Welspun Corp","WELCORP"),("Shyam Metalics","SHYAMMETL"),
        ("Godawari Power","GPIL"),("GMDC","GMDC"),("Manganese Ore","MOIL"),
        ("Hindustan Copper","HINDCOPPER"),("Tinplate Company","TINPLATE"),("Emami Paper","EMAMIPAP"),
        ("Kellton Tech","KELLTONTEC"),
    ],
    "🧱 Cement & Construction": [
        ("UltraTech Cement","ULTRACEMCO"),("Shree Cement","SHREECEM"),("Ambuja Cements","AMBUJACEM"),
        ("ACC","ACC"),("JK Cement","JKCEMENT"),("Dalmia Bharat","DALBHARAT"),
        ("Ramco Cements","RAMCOCEM"),("Heidelberg Cement","HEIDELBERG"),("JK Lakshmi Cement","JKLAKSHMI"),
        ("Birla Corporation","BIRLACORPN"),("Orient Cement","ORIENTCEM"),("India Cements","INDIACEM"),
        ("Deccan Cements","DECCANCE"),("Sagar Cements","SAGCEM"),("Star Cement","STARCEMENT"),
        ("NCL Industries","NCLIND"),("Mangalam Cement","MANGCMNT"),("Prism Johnson","PRSMJOHNSN"),
        ("HIL Limited","HIL"),("Somany Ceramics","SOMANYCERA"),("Asian Granito","ASIANTILES"),
        ("Kajaria Ceramics","KAJARIACER"),("CERA Sanitary","CERA"),("Astral","ASTRAL"),
        ("Supreme Industries","SUPREMEIND"),("Finolex Industries","FINPIPE"),
    ],
    "🛒 FMCG & Consumer": [
        ("Hindustan Unilever","HINDUNILVR"),("ITC","ITC"),("Nestle India","NESTLEIND"),
        ("Britannia","BRITANNIA"),("Dabur India","DABUR"),("Godrej Consumer","GODREJCP"),
        ("Marico","MARICO"),("Emami","EMAMILTD"),("Bajaj Consumer","BAJAJCON"),
        ("Tata Consumer","TATACONSUM"),("Varun Beverages","VBL"),("Radico Khaitan","RADICO"),
        ("United Spirits","MCDOWELL-N"),("United Breweries","UBL"),("Jubilant FoodWorks","JUBLFOOD"),
        ("Westlife Foodworld","WESTLIFE"),("Burger King India","BURGERKING"),
        ("Devyani International","DEVYANI"),("Sapphire Foods","SAPPHIRE"),
        ("Mrs Bectors Food","BECTORFOOD"),("Heritage Foods","HERITGFOOD"),("Hatsun Agro","HATSUN"),
        ("Tasty Bite Eatables","TASTYBITE"),("Prataap Snacks","PRATAAP"),("DFM Foods","DFMFOODS"),
        ("Bikaji Foods","BIKAJI"),("Saffola (Marico)","MARICO"),("P&G Hygiene","PGHH"),
        ("Colgate Palmolive","COLPAL"),("Kansai Nerolac","KANSAINER"),("Asian Paints","ASIANPAINT"),
        ("Berger Paints","BERGEPAINT"),("Indigo Paints","INDIGOPNTS"),("Pidilite","PIDILITIND"),
    ],
    "🛍️ Retail & E-Commerce": [
        ("Zomato","ZOMATO"),("Eternal (Zomato)","ETERNAL"),("Swiggy","SWIGGY"),("Paytm","PAYTM"),
        ("Nykaa","NYKAA"),("PB Fintech","POLICYBZR"),("Delhivery","DELHIVERY"),
        ("Info Edge (Naukri)","NAUKRI"),("IndiaMart","INDIAMART"),("Just Dial","JUSTDIAL"),
        ("Matrimony.com","MATRIMONY"),("CarTrade Tech","CARTRADE"),
        ("Tata Digital (BigBasket)","TATACOMM"),("Shoppers Stop","SHOPERSTOP"),
        ("Avenue Supermarts (DMart)","DMART"),("Trent","TRENT"),("V-Mart Retail","VMART"),
        ("Vishal Mega Mart","VISHALMEGA"),("Bata India","BATAINDIA"),("Relaxo Footwear","RELAXO"),
        ("Campus Activewear","CAMPUS"),("Metro Brands","METROBRAND"),
    ],
    "✈️ Infrastructure & Logistics": [
        ("Adani Ports","ADANIPORTS"),("GMR Airports","GMRINFRA"),("InterGlobe Aviation (IndiGo)","INDIGO"),
        ("SpiceJet","SPICEJET"),("Blue Dart","BLUEDART"),("Container Corp","CONCOR"),
        ("Gateway Distriparks","GDL"),("Mahindra Logistics","MAHLOG"),("Delhivery","DELHIVERY"),
        ("IRCTC","IRCTC"),("RITES","RITES"),("IRFC","IRFC"),("Rail Vikas Nigam","RVNL"),
        ("Indian Railway Finance","IRFC"),("Titagarh Rail","TITAGARH"),
        ("Texmaco Rail","TEXRAILWAG"),("Jupiter Wagons","JWL"),
        ("Delhi Airport Metro","DELHIVERY"),("Adani Wilmar","AWL"),
    ],
    "🔬 Chemicals & Fertilizers": [
        ("UPL","UPL"),("PI Industries","PIIND"),("Coromandel Int.","COROMANDEL"),
        ("Bayer CropScience","BAYERCROP"),("Sumitomo Chemical","SUMICHEM"),("Rallis India","RALLIS"),
        ("Insecticides India","INSECTICID"),("Excel Industries","EXCELINDUS"),
        ("Deepak Nitrite","DEEPAKNTR"),("Aarti Industries","AARTIIND"),("Navin Fluorine","NAVINFLUOR"),
        ("SRF Limited","SRF"),("Vinati Organics","VINATIORGA"),("Galaxy Surfactants","GALAXYSURF"),
        ("Fine Organics","FINEORG"),("Balaji Amines","BALAMINES"),("Alkyl Amines","ALKYLAMINE"),
        ("Neogen Chemicals","NEOGEN"),("Clean Science","CLEAN"),("Anupam Rasayan","ANURAS"),
        ("Tata Chemicals","TATACHEM"),("GHCL","GHCL"),("Gujarat Fluorochemicals","FLUOROCHEM"),
        ("Himadri Speciality","HSCL"),("Sudarshan Chemical","SUDARSCHEM"),
        ("NOCIL","NOCIL"),("Dharamsi Morarji","DHANVARSH"),("Chambal Fertilisers","CHAMBLFERT"),
        ("NFL","NFL"),("GSFC","GSFC"),("RCF","RCF"),("FACT","FACT"),
    ],
    "🏠 Real Estate": [
        ("Godrej Properties","GODREJPROP"),("DLF","DLF"),("Prestige Estates","PRESTIGE"),
        ("Brigade Enterprises","BRIGADE"),("Sobha","SOBHA"),("Oberoi Realty","OBEROIRLTY"),
        ("Macrotech (Lodha)","LODHA"),("Mahindra Lifespace","MAHLIFE"),("Kolte Patil","KOLTEPATIL"),
        ("Puravankara","PURVA"),("DB Realty","DBREALTY"),("Indiabulls Real Estate","IBREALEST"),
        ("Embassy REIT","EMBASSY"),("Mindspace REIT","MINDSPACE"),("Brookfield REIT","BIRET"),
        ("Nexus Select Trust","NEXUSSELCT"),
    ],
    "📡 Telecom & Media": [
        ("Bharti Airtel","BHARTIARTL"),("Vodafone Idea","IDEA"),("MTNL","MTNL"),
        ("Tata Communications","TATACOMM"),("Route Mobile","ROUTE"),("Tanla Platforms","TANLA"),
        ("Dish TV","DISHTV"),("Zee Entertainment","ZEEL"),("Sun TV Network","SUNTV"),
        ("PVR Inox","PVRINOX"),("Saregama India","SAREGAMA"),("Nazara Technologies","NAZARA"),
        ("Network18 Media","NETWORK18"),("TV18 Broadcast","TV18BRDCST"),
        ("Hathway Cable","HATHWAY"),("Den Networks","DEN"),
    ],
    "🧵 Textiles & Apparel": [
        ("Titan Company","TITAN"),("Kalyan Jewellers","KALYANKJIL"),("Senco Gold","SENCO"),
        ("Thangamayil Jewellery","THANGAMAYL"),("PC Jeweller","PCJEWELLER"),
        ("Trident","TRIDENT"),("Welspun India","WELSPUNIND"),("Raymond","RAYMOND"),
        ("Arvind","ARVIND"),("Vardhman Textiles","VTL"),("KPR Mill","KPRMILL"),
        ("Siyaram Silk Mills","SIYARAM"),("Nitin Spinners","NITINSPIN"),
        ("Indo Count Industries","ICIL"),("Alok Industries","ALOKINDS"),
        ("Gokaldas Exports","GOKEX"),("TCNS Clothing","TCNSBRANDS"),("Page Industries","PAGEIND"),
        ("Lux Industries","LUXIND"),("Dollar Industries","DOLLAR"),
    ],
    "🔌 Electronics & Capital Equipment": [
        ("Dixon Technologies","DIXON"),("Amber Enterprises","AMBER"),("Voltas","VOLTAS"),
        ("Blue Star","BLUESTARCO"),("Havells India","HAVELLS"),("Polycab India","POLYCAB"),
        ("KEI Industries","KEI"),("Finolex Cables","FINCABLES"),("V-Guard","VGUARD"),
        ("Crompton Greaves","CROMPTON"),("Orient Electric","ORIENTELEC"),("Bajaj Electricals","BAJAJELEC"),
        ("Whirlpool India","WHIRLPOOL"),("Lloyd Electric","LLOYDSME"),
        ("Kaynes Technology","KAYNES"),("Syrma SGS","SYRMA"),("Elin Electronics","ELIN"),
        ("Avalon Technologies","AVALON"),("CDSL","CDSL"),("BSE Ltd","BSE"),("MCX India","MCX"),
    ],
    "🌾 Agriculture & Food": [
        ("ITC (Agri)","ITC"),("Kaveri Seed","KSCL"),("Monsanto India","MONSANTO"),
        ("Dhanuka Agritech","DHANUKA"),("Meghmani Organics","MEGH"),
        ("Venky's India","VENKEYS"),("Suguna Foods","SUGUNA"),("Avanti Feeds","AVANTIFEED"),
        ("Waterbase","WATERBASE"),("Apex Frozen Foods","APEX"),("SKM Egg","SKMEGG"),
        ("Heritage Foods","HERITGFOOD"),("Prabhat Dairy","PRABHAT"),
        ("Tasty Bite","TASTYBITE"),("CCL Products","CCL"),("Agro Tech Foods","AGROTECH"),
        ("Ruchi Soya","PATANJALI"),("Adani Wilmar","AWL"),
    ],
}

# Flat list for fast lookup
ALL_STOCKS = {}
for sector, stocks in SECTORS.items():
    for name, sym in stocks:
        ALL_STOCKS[f"{name} ({sym})"] = f"{sym}.NS"

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def load_ohlcv(ticker, period="2y"):
    try:
        df = yf.download(ticker, period=period, interval="1d", auto_adjust=True, progress=False)
        if df is None or df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.reset_index()
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception:
        return None

def add_indicators(df):
    out = df.copy()
    if len(out) < 20:
        return out
    c = out["Close"].astype(float)
    out["Return"]       = c.pct_change()
    out["SMA_20"]       = c.rolling(20).mean()
    out["SMA_50"]       = c.rolling(50).mean()
    out["SMA_200"]      = c.rolling(200).mean()
    out["EMA_12"]       = c.ewm(span=12, adjust=False).mean()
    out["EMA_26"]       = c.ewm(span=26, adjust=False).mean()
    out["MACD"]         = out["EMA_12"] - out["EMA_26"]
    out["MACD_Signal"]  = out["MACD"].ewm(span=9, adjust=False).mean()
    out["MACD_Hist"]    = out["MACD"] - out["MACD_Signal"]
    out["BB_Mid"]       = c.rolling(20).mean()
    out["BB_Std"]       = c.rolling(20).std()
    out["BB_Upper"]     = out["BB_Mid"] + 2 * out["BB_Std"]
    out["BB_Lower"]     = out["BB_Mid"] - 2 * out["BB_Std"]
    out["Volatility_20"] = out["Return"].rolling(20).std() * np.sqrt(252)
    delta = c.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    out["RSI_14"] = 100 - (100 / (1 + gain / (loss + 1e-9)))
    # True ATR
    if "High" in out.columns and "Low" in out.columns:
        hi = out["High"].astype(float)
        lo = out["Low"].astype(float)
        hl = hi - lo
        hc = (hi - c.shift()).abs()
        lc = (lo - c.shift()).abs()
        out["ATR_14"] = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(14).mean()
    else:
        out["ATR_14"] = c.rolling(14).std()
    return out

def get_signal(df):
    if len(df) < 51:
        return "HOLD"
    last = df.iloc[-1]
    prev = df.iloc[-2]
    needed = ["SMA_20","SMA_50","RSI_14","MACD","MACD_Signal"]
    if any(pd.isna(last[x]) for x in needed):
        return "HOLD"
    macd_cross_up   = (last["MACD"] > last["MACD_Signal"]) and (prev["MACD"] <= prev["MACD_Signal"])
    macd_cross_down = (last["MACD"] < last["MACD_Signal"]) and (prev["MACD"] >= prev["MACD_Signal"])
    trend_up   = last["SMA_20"] > last["SMA_50"]
    trend_down = last["SMA_20"] < last["SMA_50"]
    above_200  = pd.notna(last.get("SMA_200")) and float(last["Close"]) > float(last["SMA_200"])
    rsi = float(last["RSI_14"])
    if trend_up and above_200 and rsi < 70 and (macd_cross_up or rsi < 45):
        return "BUY"
    if trend_down and (rsi > 70 or macd_cross_down):
        return "SELL"
    return "HOLD"

@st.cache_data(show_spinner=False)
def arima_forecast(series, steps=260):
    """Fit ARIMA on log-price, forecast steps ahead, return price forecasts + CI."""
    log_s = np.log(series.astype(float).dropna())
    d = 0 if adfuller(log_s)[1] < 0.05 else 1
    best_aic, best_model, best_order = np.inf, None, (1,d,1)
    for p in range(0, 4):
        for q in range(0, 4):
            try:
                m = ARIMA(log_s, order=(p,d,q)).fit()
                if m.aic < best_aic:
                    best_aic, best_model, best_order = m.aic, m, (p,d,q)
            except Exception:
                continue
    if best_model is None:
        best_model = ARIMA(log_s, order=(1,1,1)).fit()
        best_order = (1,1,1)
    fc  = best_model.get_forecast(steps=steps)
    mu  = fc.predicted_mean
    ci  = fc.conf_int(alpha=0.10)
    return np.exp(mu), np.exp(ci.iloc[:,0]), np.exp(ci.iloc[:,1]), best_order, round(best_aic,1)

@st.cache_data(show_spinner=False)
def es_forecast(series, steps=260):
    """Fit Holt-Winters Exponential Smoothing on log-price or price, forecast steps ahead."""
    try:
        s = series.astype(float).dropna()
        model = ExponentialSmoothing(s, trend="add", seasonal=None).fit()
        fc = model.forecast(steps=steps)
        return fc
    except Exception:
        s = series.astype(float).dropna()
        drift = (s.iloc[-1] - s.iloc[0]) / len(s)
        return pd.Series([s.iloc[-1] + drift * i for i in range(1, steps + 1)])

def ist_now():
    return datetime.datetime.now(IST)

def market_status():
    now = ist_now()
    wd  = now.weekday()
    if wd >= 5:
        return "🔴 NSE CLOSED", "#ff3355"
    open_t  = now.replace(hour=9, minute=15, second=0, microsecond=0)
    close_t = now.replace(hour=15, minute=30, second=0, microsecond=0)
    if open_t <= now <= close_t:
        return "🟢 NSE OPEN", "#00e87a"
    return "🔴 NSE CLOSED", "#ff3355"

@st.cache_data(ttl=1800, show_spinner=False)
def load_indices_data():
    tickers = ["^NSEI", "^NSEBANK", "^BSESN", "^CRSMID", "^CNXSC", "^INDIAVIX"]
    try:
        df_all = yf.download(tickers, period="1y", interval="1d", group_by="ticker", progress=False)
        return df_all
    except Exception:
        return None

@st.cache_data(ttl=900, show_spinner=False)
def fetch_ticker_news(ticker):
    url = f"https://feeds.finance.yahoo.com/rss.2.0/headline?s={ticker}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        news_items = []
        for item in root.findall(".//item"):
            title = item.find("title").text if item.find("title") is not None else ""
            link = item.find("link").text if item.find("link") is not None else ""
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            news_items.append({"title": title, "link": link, "date": pub_date})
        return news_items
    except Exception:
        return []

BULLISH_WORDS = {"surge", "grow", "growth", "jump", "rise", "gain", "profit", "record", "high", "success", "optimistic", "bullish", "beat", "positive", "expand", "outperform", "buy", "rally"}
BEARISH_WORDS = {"slump", "fall", "decline", "drop", "loss", "plunge", "negative", "bearish", "miss", "pessimistic", "dip", "underperform", "sell", "debt", "crisis", "warn", "crash"}

def analyze_sentiment(news_items):
    if not news_items:
        return 0.0, "NEUTRAL"
    total_score = 0
    for item in news_items:
        title_lower = item["title"].lower()
        score = 0
        for w in BULLISH_WORDS:
            if w in title_lower:
                score += 1
        for w in BEARISH_WORDS:
            if w in title_lower:
                score -= 1
        total_score += score
    
    avg_score = total_score / len(news_items)
    if avg_score > 0.15:
        category = "BULLISH"
    elif avg_score < -0.15:
        category = "BEARISH"
    else:
        category = "NEUTRAL"
    return avg_score, category

# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
col_title, col_clock = st.columns([2, 1])
with col_title:
    st.markdown('<h1 class="xerces-title">XERCES // QUANT ENGINE</h1>', unsafe_allow_html=True)
    st.markdown('<p class="telemetry-tag">[ NSE/BSE UNIVERSE: 500+ STOCKS // ARIMA + TECHNICAL ANALYSIS ENGINE ]</p>', unsafe_allow_html=True)
with col_clock:
    now_ist = ist_now()
    ms, mc  = market_status()
    st.markdown(f"""
    <div style="text-align:right;font-family:'Space Mono',monospace;font-size:11px;color:#6a90aa;
                background:rgba(7,18,32,0.5);padding:8px;border-radius:4px;border:1px solid rgba(0,200,255,0.08);">
        <div>CLOCK: <span style="color:#ffcc00;font-weight:bold;">{now_ist.strftime('%H:%M:%S')} IST</span></div>
        <div>DATE: <span style="color:#00c8ff;">{now_ist.strftime('%Y-%m-%d')}</span></div>
        <div style="margin-top:3px;color:{mc};font-weight:bold;">{ms}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<hr style='border-color:rgba(0,200,255,0.12);margin:0.65rem 0;'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TOP SEARCH BAR (TRADINGVIEW STYLE TEXT INPUT)
# ══════════════════════════════════════════════════════════════
st.markdown("<div style='background:rgba(7,18,32,0.45);border:1px solid rgba(0,200,255,0.12);padding:12px 18px;border-radius:6px;margin-bottom:15px;backdrop-filter:blur(4px);'>", unsafe_allow_html=True)
c1, c2 = st.columns([5, 1])
with c1:
    search_ticker = st.text_input(
        "Search Ticker",
        value="",
        placeholder="Search stock name or symbol (e.g. Reliance, TCS, AAPL, BTC-USD)...",
        label_visibility="collapsed"
    )
with c2:
    if search_ticker:
        if st.button("Clear Search", use_container_width=True):
            st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# Ticker Resolution Logic
selected_ticker = ""
selected_name = ""
is_dashboard = True

search_ticker = search_ticker.strip()
if search_ticker:
    match_ticker = None
    match_name = None
    
    # 1. Exact or partial match in ALL_STOCKS keys (e.g. "Reliance Industries (RELIANCE)")
    for label, ticker in ALL_STOCKS.items():
        if search_ticker.lower() in label.lower():
            match_ticker = ticker
            match_name = label.split(" (")[0]
            break
            
    # 2. If no match in keys, check if it's a direct symbol match in values
    if not match_ticker:
        for label, ticker in ALL_STOCKS.items():
            sym_only = ticker.replace(".NS", "")
            if search_ticker.upper() == sym_only or search_ticker.upper() == ticker:
                match_ticker = ticker
                match_name = label.split(" (")[0]
                break
                
    if match_ticker:
        selected_ticker = match_ticker
        selected_name = match_name
        is_dashboard = False
    else:
        # No match -> treat as custom ticker directly
        selected_ticker = search_ticker.upper()
        selected_name = selected_ticker
        is_dashboard = False
else:
    selected_ticker = "^NSEI"
    selected_name = "NIFTY 50"
    is_dashboard = True

if is_dashboard:
    # ══════════════════════════════════════════════════════════════
    # MARKET DASHBOARD (LANDING PAGE)
    # ══════════════════════════════════════════════════════════════
    st.markdown('<h2 class="xerces-title" style="font-size:1.6rem;margin-bottom:15px;">📊 INDIAN MARKET OVERVIEW</h2>', unsafe_allow_html=True)
    
    df_indices = load_indices_data()
    if df_indices is not None:
        r1_cols = st.columns(3)
        r2_cols = st.columns(3)
        
        indices_row1 = [
            ("NIFTY 50", "^NSEI", "#00e87a"),
            ("BANK NIFTY", "^NSEBANK", "#00c8ff"),
            ("SENSEX", "^BSESN", "#ffcc00")
        ]
        
        indices_row2 = [
            ("NIFTY MIDCAP 100", "^CRSMID", "#ff6b35"),
            ("NIFTY SMALLCAP 100", "^CNXSC", "#7c6ef8"),
            ("INDIA VIX", "^INDIAVIX", "#ff3355")
        ]
        
        # Render Row 1
        for col, (name, sym, color) in zip(r1_cols, indices_row1):
            try:
                if isinstance(df_indices.columns, pd.MultiIndex):
                    idx_df = df_indices[sym].dropna().reset_index()
                else:
                    idx_df = df_indices.dropna().reset_index()
                
                last_row = idx_df.iloc[-1]
                prev_row = idx_df.iloc[-2]
                close_v = float(last_row["Close"])
                chg_pct = (close_v - float(prev_row["Close"])) / float(prev_row["Close"]) * 100
                chg_color = "#00e87a" if chg_pct >= 0 else "#ff3355"
                arrow = "▲" if chg_pct >= 0 else "▼"
                
                col.markdown(f"""
                <div class="glass-card">
                    <p class="glass-label" style="color:{color};font-weight:bold;">{name}</p>
                    <div class="glass-value" style="font-size:1.2rem;">{close_v:,.2f}</div>
                    <p style="font-size:11px;color:{chg_color};margin:2px 0 0 0;font-weight:600;">
                        {arrow} {abs(chg_pct):.2f}%
                    </p>
                </div>""", unsafe_allow_html=True)
            except Exception:
                col.warning(f"Error loading {name}")
                
        # Render Row 2
        for col, (name, sym, color) in zip(r2_cols, indices_row2):
            try:
                if isinstance(df_indices.columns, pd.MultiIndex):
                    idx_df = df_indices[sym].dropna().reset_index()
                else:
                    idx_df = df_indices.dropna().reset_index()
                
                last_row = idx_df.iloc[-1]
                prev_row = idx_df.iloc[-2]
                close_v = float(last_row["Close"])
                chg_pct = (close_v - float(prev_row["Close"])) / float(prev_row["Close"]) * 100
                
                if sym == "^INDIAVIX":
                    chg_color = "#ff3355" if chg_pct >= 0 else "#00e87a"
                else:
                    chg_color = "#00e87a" if chg_pct >= 0 else "#ff3355"
                    
                arrow = "▲" if chg_pct >= 0 else "▼"
                
                col.markdown(f"""
                <div class="glass-card">
                    <p class="glass-label" style="color:{color};font-weight:bold;">{name}</p>
                    <div class="glass-value" style="font-size:1.2rem;">{close_v:,.2f}</div>
                    <p style="font-size:11px;color:{chg_color};margin:2px 0 0 0;font-weight:600;">
                        {arrow} {abs(chg_pct):.2f}%
                    </p>
                </div>""", unsafe_allow_html=True)
            except Exception:
                col.warning(f"Error loading {name}")
                
        st.markdown('<p class="section-header">[ 📈 NIFTY 50 INDEX TREND ]</p>', unsafe_allow_html=True)
        try:
            n50_df = df_indices["^NSEI"].dropna().reset_index()
            fig_n50 = go.Figure()
            fig_n50.add_trace(go.Scatter(x=n50_df["Date"], y=n50_df["Close"], name="Nifty 50 Close", line=dict(color="#00e87a", width=2)))
            fig_n50.update_layout(
                height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ddeeff", family="Space Mono", size=10),
                xaxis=dict(gridcolor="rgba(0,200,255,0.05)"),
                yaxis=dict(gridcolor="rgba(0,200,255,0.05)", tickprefix="₹"),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_n50, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading Nifty 50 Chart: {e}")
            
        st.markdown("""
        <div class="glass-card" style="margin-top:15px;">
            <p class="section-header" style="margin-top:0;">💡 Broad Market Overview</p>
            <p style="font-size:12px;color:#a0aec0;line-height:1.6;margin:0;">
                Welcome to <b>XERCES // QUANT ENGINE</b>. Use the TradingView-style search bar at the top to select an individual stock ticker and load our advanced quantitative and machine learning modules, including ARIMA + Holt-Winters price forecasting, crossover backtesters, and portfolio optimizer.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("Failed to load market index data. Check internet connection.")
    st.stop()

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<p class='telemetry-tag' style='color:#00c8ff;font-weight:700;margin-bottom:5px;'>[ 🛡️ RISK CONTROLS ]</p>", unsafe_allow_html=True)
    allocated_capital = st.number_input("Capital Pool (₹)", min_value=1000, value=100000, step=5000)
    risk_per_trade    = st.slider("Risk per Trade (%)", 0.5, 5.0, 1.5, step=0.1)
    risk_reward       = st.slider("Risk:Reward (1:X)", 1.5, 4.0, 2.0, step=0.5)

    st.markdown("---")
    st.markdown("<p class='telemetry-tag' style='color:#00c8ff;font-weight:700;margin-bottom:5px;'>[ ⚙️ CHART SETTINGS ]</p>", unsafe_allow_html=True)
    show_bb   = st.checkbox("Bollinger Bands", value=True)
    show_sma  = st.checkbox("SMA 20/50/200", value=True)
    show_vol  = st.checkbox("Volume bars", value=True)

    st.markdown("---")
    st.markdown("<p class='telemetry-tag' style='color:#00c8ff;font-weight:700;margin-bottom:5px;'>[ 📈 BACKTEST STRATEGY ]</p>", unsafe_allow_html=True)
    backtest_strategy = st.selectbox("Strategy Template", ["SMA Crossover", "RSI Mean Reversion", "Bollinger Bands Breakout"])

    st.markdown("---")
    st.caption("⚠️ Not SEBI registered. Statistical analysis only — not financial advice. Data from Yahoo Finance.")

# ══════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════
with st.spinner(f"Loading {selected_name} data..."):
    raw_df = load_ohlcv(selected_ticker, period="5y")

if raw_df is None or len(raw_df) < 60:
    st.error(f"Could not load data for {selected_ticker}. Try another stock.")
    st.stop()

df = add_indicators(raw_df)
last      = df.iloc[-1]
prev      = df.iloc[-2]
close     = float(last["Close"])
signal    = get_signal(df)
atr_val   = float(last["ATR_14"]) if pd.notna(last.get("ATR_14")) else close * 0.02
sl_price  = close - atr_val * 1.5
tp_price  = close + atr_val * 1.5 * risk_reward
cap_risk  = allocated_capital * (risk_per_trade / 100)
qty       = max(1, int(cap_risk / (atr_val * 1.5)))
chg1d     = (close - float(prev["Close"])) / float(prev["Close"]) * 100
hi52      = float(df["Close"].iloc[-252:].max()) if len(df) >= 252 else float(df["Close"].max())
lo52      = float(df["Close"].iloc[-252:].min()) if len(df) >= 252 else float(df["Close"].min())
rsi_val   = float(last["RSI_14"]) if pd.notna(last.get("RSI_14")) else 50.0

# ══════════════════════════════════════════════════════════════
# RUN SHARED STRATEGY BACKTEST (Next-day Open Execution)
# ══════════════════════════════════════════════════════════════
bt_df = df.copy().reset_index(drop=True)
bt_df["Signal_BT"] = 0

if backtest_strategy == "SMA Crossover":
    valid_idx = bt_df["SMA_20"].notna() & bt_df["SMA_50"].notna()
    bt_df.loc[valid_idx & (bt_df["SMA_20"] > bt_df["SMA_50"]), "Signal_BT"] = 1

elif backtest_strategy == "RSI Mean Reversion":
    rsi_vals = bt_df["RSI_14"].values
    sig = 0
    signals = []
    for r in rsi_vals:
        if pd.isna(r):
            signals.append(0)
            continue
        if r < 30:
            sig = 1
        elif r > 70:
            sig = 0
        signals.append(sig)
    bt_df["Signal_BT"] = signals

elif backtest_strategy == "Bollinger Bands Breakout":
    close_vals = bt_df["Close"].astype(float).values
    upper_vals = bt_df["BB_Upper"].astype(float).values
    lower_vals = bt_df["BB_Lower"].astype(float).values
    sig = 0
    signals = []
    for c, u, l in zip(close_vals, upper_vals, lower_vals):
        if pd.isna(u) or pd.isna(l) or pd.isna(c):
            signals.append(0)
            continue
        if c > u:
            sig = 1
        elif c < l:
            sig = 0
        signals.append(sig)
    bt_df["Signal_BT"] = signals

bt_df = bt_df.dropna(subset=["Close", "Open", "Date"]).copy().reset_index(drop=True)
bt_df["Position"] = bt_df["Signal_BT"].diff()

trades = []
buy_signals_x = []
buy_signals_y = []
sell_signals_x = []
sell_signals_y = []

in_trade = False
entry_price = 0.0
entry_date  = None

n_rows = len(bt_df)
for idx in range(n_rows):
    row = bt_df.iloc[idx]
    pos_change = row["Position"]
    
    # Buy signal -> enter on Open of next trading day
    if pos_change == 1 and not in_trade:
        if idx + 1 < n_rows:
            next_row = bt_df.iloc[idx + 1]
            in_trade    = True
            entry_price = float(next_row["Open"])
            entry_date  = next_row["Date"]
            buy_signals_x.append(next_row["Date"])
            buy_signals_y.append(next_row["Open"])
            
    # Sell signal -> exit on Open of next trading day
    elif pos_change == -1 and in_trade:
        if idx + 1 < n_rows:
            next_row = bt_df.iloc[idx + 1]
            in_trade = False
            exit_p   = float(next_row["Open"])
            pnl_pct  = (exit_p - entry_price) / entry_price * 100
            trades.append({
                "Entry Date": str(entry_date)[:10], 
                "Exit Date": str(next_row["Date"])[:10],
                "Entry ₹": round(entry_price,2), 
                "Exit ₹": round(exit_p,2),
                "P&L %": round(pnl_pct,2), 
                "Result": "✅ WIN" if pnl_pct > 0 else "❌ LOSS"
            })
            sell_signals_x.append(next_row["Date"])
            sell_signals_y.append(next_row["Open"])

# ══════════════════════════════════════════════════════════════
# KPI ROW
# ══════════════════════════════════════════════════════════════
k1,k2,k3,k4,k5,k6 = st.columns(6)
sig_color = {"BUY":"#00e87a","SELL":"#ff3355","HOLD":"#ffcc00"}[signal]
chg_color = "#00e87a" if chg1d >= 0 else "#ff3355"

for col, lbl, val in zip(
    [k1,k2,k3,k4,k5,k6],
    ["Last Close","1-Day Change","52W High","52W Low","RSI (14)","Signal"],
    [f"₹{close:,.2f}", f"{'▲' if chg1d>=0 else '▼'} {abs(chg1d):.2f}%",
     f"₹{hi52:,.2f}", f"₹{lo52:,.2f}", f"{rsi_val:.1f}", signal]
):
    color = sig_color if lbl=="Signal" else (chg_color if "Change" in lbl else "#ddeeff")
    col.markdown(f'<div class="glass-card"><p class="glass-label">{lbl}</p>'
                 f'<div class="glass-value" style="color:{color};">{val}</div></div>',
                 unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════
tab_chart, tab_arima, tab_backtest, tab_scan, tab_risk, tab_news, tab_port, tab_help = st.tabs([
    "📊 TECHNICAL CHART",
    "🔮 ARIMA FORECAST",
    "📈 BACKTEST ENGINE",
    "📡 MARKET SCANNER",
    "🛡️ RISK CALCULATOR",
    "📰 NEWS & SENTIMENT",
    "💼 PORTFOLIO OPTIMIZER",
    "❓ MANUAL"
])

# ──────────────────────────────────────────────────────────────
# TAB 1: TECHNICAL CHART
# ──────────────────────────────────────────────────────────────
with tab_chart:
    rows = 4 if show_vol else 3
    row_h = [0.55, 0.20, 0.15] if not show_vol else [0.48, 0.18, 0.18, 0.16]
    specs = [[{"secondary_y": False}]] * rows
    subplot_titles = ["Price + Indicators", "RSI (14)", "MACD"] + (["Volume"] if show_vol else [])
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=row_h,
                        vertical_spacing=0.03, subplot_titles=subplot_titles, specs=specs)

    # ── Price & overlays ──
    fig.add_trace(go.Candlestick(
        x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name="OHLC", increasing_line_color="#00e87a", decreasing_line_color="#ff3355",
        increasing_fillcolor="rgba(0,232,122,0.3)", decreasing_fillcolor="rgba(255,51,85,0.3)"
    ), row=1, col=1)

    if show_sma:
        for col_name, color, dash in [("SMA_20","#00c8ff","dot"),("SMA_50","#ffcc00","dash"),("SMA_200","#ff6b35","solid")]:
            if col_name in df.columns:
                fig.add_trace(go.Scatter(x=df["Date"], y=df[col_name], name=col_name.replace("_"," "),
                    line=dict(color=color, width=1.2, dash=dash), opacity=0.85), row=1, col=1)

    if show_bb and "BB_Upper" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_Upper"], name="BB Upper",
            line=dict(color="rgba(124,78,255,0.5)", width=1, dash="dot")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_Lower"], name="BB Lower",
            line=dict(color="rgba(124,78,255,0.5)", width=1, dash="dot"),
            fill="tonexty", fillcolor="rgba(124,78,255,0.05)"), row=1, col=1)

    # ── Risk Sizing horizontal lines ──
    fig.add_hline(y=close, line_dash="solid", line_color="rgba(221,238,255,0.6)", annotation_text="Last Close", row=1, col=1)
    fig.add_hline(y=sl_price, line_dash="dash", line_color="rgba(255,51,85,0.7)", annotation_text="Stop Loss", row=1, col=1)
    fig.add_hline(y=tp_price, line_dash="dash", line_color="rgba(0,232,122,0.7)", annotation_text="Target", row=1, col=1)

    # ── Trade Markers ──
    if buy_signals_x:
        fig.add_trace(go.Scatter(
            x=buy_signals_x, y=buy_signals_y,
            mode="markers", name="Buy Entry (Backtest)",
            marker=dict(symbol="triangle-up", size=10, color="#00e87a", line=dict(width=1, color="#020813")),
            showlegend=True
        ), row=1, col=1)
    if sell_signals_x:
        fig.add_trace(go.Scatter(
            x=sell_signals_x, y=sell_signals_y,
            mode="markers", name="Sell Exit (Backtest)",
            marker=dict(symbol="triangle-down", size=10, color="#ff3355", line=dict(width=1, color="#020813")),
            showlegend=True
        ), row=1, col=1)

    # ── RSI ──
    fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI_14"], name="RSI 14",
        line=dict(color="#00c8ff", width=1.5)), row=2, col=1)
    for lvl, col_r in [(70,"rgba(255,51,85,0.4)"),(30,"rgba(0,232,122,0.4)"),(50,"rgba(255,255,255,0.1)")]:
        fig.add_hline(y=lvl, line_dash="dot", line_color=col_r, row=2, col=1)

    # ── MACD ──
    colors_macd = ["#00e87a" if v >= 0 else "#ff3355" for v in df["MACD_Hist"].fillna(0)]
    fig.add_trace(go.Bar(x=df["Date"], y=df["MACD_Hist"], name="MACD Hist", marker_color=colors_macd, opacity=0.7), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["MACD"], name="MACD", line=dict(color="#00c8ff", width=1.2)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["MACD_Signal"], name="Signal", line=dict(color="#ffcc00", width=1.2, dash="dot")), row=3, col=1)

    # ── Volume ──
    if show_vol and "Volume" in df.columns:
        vol_colors = ["rgba(0,232,122,0.5)" if r["Close"] >= r["Open"] else "rgba(255,51,85,0.5)" for _, r in df.iterrows()]
        fig.add_trace(go.Bar(x=df["Date"], y=df["Volume"], name="Volume", marker_color=vol_colors), row=4, col=1)

    fig.update_layout(
        height=750, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ddeeff", family="Space Mono", size=10),
        xaxis_rangeslider_visible=False, showlegend=True,
        legend=dict(bgcolor="rgba(7,18,32,0.5)", bordercolor="rgba(0,200,255,0.2)", borderwidth=1, font=dict(size=9)),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    for i in range(1, rows+1):
        fig.update_xaxes(gridcolor="rgba(0,200,255,0.05)", row=i, col=1)
        fig.update_yaxes(gridcolor="rgba(0,200,255,0.05)", row=i, col=1)

    # Range selector
    fig.update_xaxes(
        rangeselector=dict(
            buttons=[
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(count=2, label="2Y", step="year", stepmode="backward"),
                dict(step="all", label="5Y"),
            ],
            bgcolor="rgba(7,18,32,0.7)", activecolor="#00c8ff",
            font=dict(color="#ddeeff", size=9)
        ), row=1, col=1
    )
    st.plotly_chart(fig, use_container_width=True)

    # Signal interpretation
    left_s, right_s = st.columns([1,2])
    with left_s:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <p class="glass-label">Current Signal</p>
            <div class="signal-{'buy' if signal=='BUY' else 'sell' if signal=='SELL' else 'hold'}">{signal}</div>
            <p style="font-size:10px;color:#6a90aa;margin-top:6px;">
            SMA20 {'>' if float(last.get('SMA_20',0) or 0) > float(last.get('SMA_50',0) or 0) else '<'} SMA50 &nbsp;|&nbsp; RSI {rsi_val:.0f}
            </p>
        </div>""", unsafe_allow_html=True)
    with right_s:
        macd_v = float(last.get("MACD",0) or 0)
        macd_s = float(last.get("MACD_Signal",0) or 0)
        bb_pos = ""
        if pd.notna(last.get("BB_Upper")) and pd.notna(last.get("BB_Lower")):
            bb_range = float(last["BB_Upper"]) - float(last["BB_Lower"])
            bb_pct   = (close - float(last["BB_Lower"])) / bb_range * 100 if bb_range > 0 else 50
            bb_pos   = f"{bb_pct:.0f}% within bands"
        st.markdown(f"""
        <div class="glass-card">
            <p class="glass-label">Indicator Readings</p>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:6px;font-size:11px;font-family:'Space Mono',monospace;">
                <div>RSI: <span style="color:{'#ff3355' if rsi_val>70 else '#00e87a' if rsi_val<30 else '#00c8ff'}">{rsi_val:.1f}</span></div>
                <div>MACD: <span style="color:{'#00e87a' if macd_v>macd_s else '#ff3355'}">{macd_v:.2f}</span></div>
                <div>ATR(14): <span style="color:#ffcc00;">₹{atr_val:.2f}</span></div>
                <div>BB Position: <span style="color:#7c4dff;">{bb_pos}</span></div>
                <div>SMA200: <span style="color:#ff6b35;">₹{float(last.get('SMA_200',0) or 0):,.0f}</span></div>
                <div>Volatility: <span style="color:#ddeeff;">{float(last.get('Volatility_20',0) or 0):.1%}</span></div>
            </div>
        </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TAB 2: ARIMA FORECAST
# ──────────────────────────────────────────────────────────────
with tab_arima:
    st.markdown(f'<p class="section-header">[ 🔮 ARIMA PRICE FORECAST — {selected_name} → JUNE 2027 ]</p>', unsafe_allow_html=True)

    with st.spinner("Fitting ARIMA model via AIC grid search (30–60 sec)..."):
        try:
            price_series = df["Close"].astype(float).dropna()
            last_date    = pd.to_datetime(df["Date"].iloc[-1])
            target_end   = pd.Timestamp("2027-06-30")
            fc_dates     = pd.bdate_range(start=last_date + pd.Timedelta(days=1), end=target_end)
            steps        = len(fc_dates)

            if steps <= 0:
                st.warning("Data already extends past June 2027.")
            else:
                fc_mean, fc_lo, fc_hi, arima_order, aic_val = arima_forecast(price_series, steps=steps)
                fc_series = pd.Series(fc_mean.values, index=fc_dates)
                ci_lo     = pd.Series(fc_lo.values,   index=fc_dates)
                ci_hi     = pd.Series(fc_hi.values,   index=fc_dates)

                target_price = float(fc_series.iloc[-1])
                upside       = (target_price - close) / close * 100

                es_series = es_forecast(price_series, steps=steps)
                es_series.index = fc_dates
                target_es = float(es_series.iloc[-1])
                es_upside = (target_es - close) / close * 100

                # KPI row
                fa1, fa2, fa3, fa4 = st.columns(4)
                for col, lbl, val, color in zip(
                    [fa1,fa2,fa3,fa4],
                    ["Current Price","ARIMA Target (Jun'27)","Holt-Winters Target","ARIMA Model"],
                    [f"₹{close:,.2f}", f"₹{target_price:,.2f} ({'▲' if upside>=0 else '▼'}{abs(upside):.1f}%)",
                     f"₹{target_es:,.2f} ({'▲' if es_upside>=0 else '▼'}{abs(es_upside):.1f}%)", f"ARIMA{arima_order}"],
                    ["#ddeeff","#fbbf24","#00c8ff","#ff6b35"]
                ):
                    col.markdown(f'<div class="glass-card"><p class="glass-label">{lbl}</p>'
                                 f'<div class="glass-value" style="color:{color};">{val}</div></div>',
                                 unsafe_allow_html=True)

                # Forecast chart
                fig2 = go.Figure()
                hist_plot = price_series.iloc[-504:]  # 2yr history
                hist_dates = pd.to_datetime(df["Date"].iloc[-504:])
                fig2.add_trace(go.Scatter(x=hist_dates, y=hist_plot.values, name="Historical (2yr)",
                    line=dict(color="#7c6ef8", width=1.8)))
                fig2.add_trace(go.Scatter(x=fc_series.index, y=fc_series.values, name="ARIMA Forecast",
                    line=dict(color="#f97316", width=2, dash="dash")))
                fig2.add_trace(go.Scatter(x=es_series.index, y=es_series.values, name="Holt-Winters Forecast",
                    line=dict(color="#00c8ff", width=1.5, dash="dashdot")))
                fig2.add_trace(go.Scatter(
                    x=list(ci_hi.index) + list(ci_lo.index[::-1]),
                    y=list(ci_hi.values) + list(ci_lo.values[::-1]),
                    fill="toself", fillcolor="rgba(249,115,22,0.08)",
                    line=dict(color="rgba(0,0,0,0)"), name="ARIMA 90% CI", showlegend=True))
                fig2.add_vline(x=str(last_date), line_dash="dot", line_color="rgba(100,100,100,0.5)")
                fig2.add_annotation(x=str(target_end), y=target_price,
                    text=f"Jun '27<br>₹{target_price:,.0f}",
                    showarrow=True, arrowhead=2, arrowcolor="#fbbf24",
                    font=dict(color="#fbbf24", size=10), bgcolor="rgba(7,18,32,0.8)",
                    bordercolor="#fbbf24", borderwidth=1)
                fig2.update_layout(
                    height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#ddeeff", family="Space Mono", size=10),
                    legend=dict(bgcolor="rgba(7,18,32,0.5)", bordercolor="rgba(0,200,255,0.2)", borderwidth=1),
                    margin=dict(l=10,r=10,t=20,b=10),
                    xaxis=dict(gridcolor="rgba(0,200,255,0.05)"),
                    yaxis=dict(gridcolor="rgba(0,200,255,0.05)", tickprefix="₹"),
                )
                st.plotly_chart(fig2, use_container_width=True)

                # Monthly forecast table
                st.markdown('<p class="section-header">[ 📅 MONTH-BY-MONTH PRICE TARGETS ]</p>', unsafe_allow_html=True)
                fc_df2 = pd.DataFrame({"Forecast": fc_series, "CI_Lo": ci_lo, "CI_Hi": ci_hi})
                fc_df2["Month"] = fc_df2.index.to_period("M")
                monthly = fc_df2.groupby("Month").agg(
                    Forecast=("Forecast","last"), CI_Lo=("CI_Lo","last"), CI_Hi=("CI_Hi","last")
                ).reset_index()
                monthly["Month_str"]  = monthly["Month"].dt.strftime("%b %Y")
                monthly["MoM_pct"]    = monthly["Forecast"].pct_change() * 100
                monthly.loc[0,"MoM_pct"] = (monthly.loc[0,"Forecast"] - close) / close * 100

                for i in range(0, len(monthly), 6):
                    chunk = monthly.iloc[i:i+6]
                    cols  = st.columns(len(chunk))
                    for col, (_, row) in zip(cols, chunk.iterrows()):
                        chg   = row["MoM_pct"]
                        arrow = "▲" if chg >= 0 else "▼"
                        clr   = "#00e87a" if chg >= 0 else "#ff3355"
                        col.markdown(f"""
<div style="background:rgba(7,18,32,0.65);border:1px solid rgba(0,200,255,0.15);border-radius:6px;
     padding:10px 8px;text-align:center;margin-bottom:6px;">
  <div style="font-size:10px;font-family:'Space Mono',monospace;color:#6a90aa;text-transform:uppercase;">{row['Month_str']}</div>
  <div style="font-family:'Orbitron',sans-serif;font-size:1rem;font-weight:700;color:#fbbf24;margin:4px 0;">₹{row['Forecast']:,.1f}</div>
  <div style="font-size:10px;color:{clr};font-weight:600;">{arrow} {abs(chg):.1f}%</div>
  <div style="font-size:9px;color:#374151;margin-top:3px;">₹{row['CI_Lo']:,.0f}–₹{row['CI_Hi']:,.0f}</div>
</div>""", unsafe_allow_html=True)

                # Download
                tbl = monthly[["Month_str","Forecast","CI_Lo","CI_Hi","MoM_pct"]].round(2)
                tbl.columns = ["Month","Forecast ₹","Lower Bound ₹","Upper Bound ₹","MoM Change %"]
                st.download_button("⬇️ Download Forecast CSV",
                                   tbl.to_csv(index=False).encode(),
                                   f"{selected_name}_ARIMA_forecast.csv","text/csv")

                with st.expander("🔬 Model diagnostics"):
                    pv = adfuller(np.log(price_series.dropna()))[1]
                    st.markdown(f"""
| Parameter | Value |
|---|---|
| Ticker | {selected_ticker} |
| ARIMA Order | {arima_order} |
| AIC | {aic_val} |
| Log-price ADF p-value | {pv:.4f} {"✅ Stationary" if pv < 0.05 else "⚠️ Differenced"} |
| Training observations | {len(price_series):,} |
| Forecast steps | {steps} trading days |
| Data range | {df['Date'].iloc[0].strftime('%d %b %Y') if hasattr(df['Date'].iloc[0],'strftime') else str(df['Date'].iloc[0])} → {str(df['Date'].iloc[-1])[:10]} |
""")
        except Exception as e:
            st.error(f"ARIMA error: {e}")

# ──────────────────────────────────────────────────────────────
# TAB 3: BACKTEST ENGINE
# ──────────────────────────────────────────────────────────────
with tab_backtest:
    st.markdown(f'<p class="section-header">[ 📈 {backtest_strategy.upper()} BACKTEST — {selected_name} ]</p>', unsafe_allow_html=True)
    st.caption(f"ℹ️ Execution model: Next-day Open execution (eliminates look-ahead bias). Running strategy: **{backtest_strategy}**")

    if trades:
        trades_df  = pd.DataFrame(trades)
        wins       = (trades_df["P&L %"] > 0).sum()
        total      = len(trades_df)
        win_rate   = wins / total * 100
        
        # Profit Factor
        gross_profit = trades_df[trades_df["P&L %"] > 0]["P&L %"].sum()
        gross_loss = abs(trades_df[trades_df["P&L %"] < 0]["P&L %"].sum())
        if gross_loss > 0:
            profit_factor = gross_profit / gross_loss
            profit_factor_str = f"{profit_factor:.2f}"
        else:
            profit_factor_str = "∞" if gross_profit > 0 else "0.00"
            profit_factor = 999.0 if gross_profit > 0 else 0.0

        # Equity curve calculations
        bt_df["Strategy_Return"] = bt_df["Signal_BT"].shift(1) * bt_df["Close"].astype(float).pct_change()
        bt_df["Equity"]          = (1 + bt_df["Strategy_Return"].fillna(0)).cumprod()
        bt_df["Buy_Hold"]        = bt_df["Close"].astype(float) / float(bt_df["Close"].iloc[0]) * 100
        bt_df["Equity_Scaled"]   = bt_df["Equity"] * 100

        # Max Drawdown
        bt_df["Peak"]            = bt_df["Equity"].cummax()
        bt_df["Drawdown"]        = (bt_df["Equity"] - bt_df["Peak"]) / bt_df["Peak"]
        max_dd                   = abs(float(bt_df["Drawdown"].min() * 100))

        # Sharpe Ratio
        returns = bt_df["Strategy_Return"].fillna(0)
        mean_ret = returns.mean()
        std_ret = returns.std()
        sharpe = (mean_ret / std_ret) * np.sqrt(252) if std_ret > 0 else 0.0

        b1,b2,b3,b4,b5 = st.columns(5)
        for col, lbl, val, clr in zip([b1,b2,b3,b4,b5],
            ["Win Rate","Profit Factor","Max Drawdown","Sharpe Ratio","Total Trades"],
            [f"{win_rate:.1f}%", profit_factor_str, f"-{max_dd:.1f}%", f"{sharpe:.2f}", str(total)],
            ["#00e87a","#00e87a" if profit_factor >= 1.5 else "#ffcc00" if profit_factor >= 1.0 else "#ff3355","#ff3355","#00c8ff","#ddeeff"]):
            col.markdown(f'<div class="glass-card"><p class="glass-label">{lbl}</p>'
                         f'<div class="glass-value" style="color:{clr};">{val}</div></div>', unsafe_allow_html=True)

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=bt_df["Date"], y=bt_df["Equity_Scaled"], name="Strategy", line=dict(color="#00e87a",width=2)))
        fig3.add_trace(go.Scatter(x=bt_df["Date"], y=bt_df["Buy_Hold"], name="Buy & Hold", line=dict(color="#7c6ef8",width=1.5,dash="dot")))
        fig3.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ddeeff",family="Space Mono",size=10),
            xaxis=dict(gridcolor="rgba(0,200,255,0.05)"), yaxis=dict(gridcolor="rgba(0,200,255,0.05)"),
            margin=dict(l=10,r=10,t=20,b=10),
            legend=dict(bgcolor="rgba(7,18,32,0.5)",bordercolor="rgba(0,200,255,0.2)",borderwidth=1))
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('<p class="section-header">[ TRADE LOG ]</p>', unsafe_allow_html=True)
        st.dataframe(trades_df.tail(30), use_container_width=True, hide_index=True)
    else:
        st.info("Not enough trade signals generated in the data period. Try a stock with more history or adjust settings.")

# ──────────────────────────────────────────────────────────────
# TAB 4: MARKET SCANNER
# ──────────────────────────────────────────────────────────────
with tab_scan:
    st.markdown('<p class="section-header">[ 📡 MULTI-STOCK BULK SCANNER ]</p>', unsafe_allow_html=True)

    scan_sectors = st.multiselect("Scan sectors", list(SECTORS.keys()),
                                   default=["🏦 Banking & Finance","💻 IT & Technology"])
    max_stocks   = st.slider("Max stocks to scan", 10, 100, 30, step=5)

    def scan_single_stock(name, ticker_s):
        try:
            sd = load_ohlcv(ticker_s, period="1y")
            if sd is None or len(sd) < 60:
                return None
            sd = add_indicators(sd)
            last_s = sd.iloc[-1]
            prev_s = sd.iloc[-2]
            sig_s  = get_signal(sd)
            cp     = float(last_s["Close"])
            chg_s  = (cp - float(prev_s["Close"])) / float(prev_s["Close"]) * 100
            atr_s  = float(last_s["ATR_14"]) if pd.notna(last_s.get("ATR_14")) else cp*0.02
            sl_s   = cp - atr_s*1.5
            tp_s   = cp + atr_s*1.5*risk_reward
            cr_s   = allocated_capital*(risk_per_trade/100)
            qty_s  = max(1, int(cr_s/(atr_s*1.5)))
            return {
                "Stock": name, "Ticker": ticker_s.replace(".NS",""),
                "Price ₹": f"{cp:,.2f}", "1D Chg%": f"{chg_s:+.2f}",
                "RSI": f"{float(last_s['RSI_14']):.1f}" if pd.notna(last_s.get('RSI_14')) else "—",
                "Signal": sig_s,
                "Stop Loss ₹": f"{sl_s:,.2f}", "Target ₹": f"{tp_s:,.2f}",
                "Qty": qty_s,
                "_sig": sig_s, "_chg": chg_s
            }
        except Exception:
            return None

    if st.button("⚡ RUN SCAN", use_container_width=True):
        scan_pool = []
        for sec in scan_sectors:
            scan_pool += [(n, f"{s}.NS") for n, s in SECTORS[sec]]
        scan_pool = scan_pool[:max_stocks]

        results   = []
        prog      = st.progress(0, text="Scanning...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_stock = {executor.submit(scan_single_stock, name, ticker_s): (name, ticker_s) for name, ticker_s in scan_pool}
            for idx, future in enumerate(concurrent.futures.as_completed(future_to_stock)):
                name, ticker_s = future_to_stock[future]
                try:
                    res = future.result()
                    if res is not None:
                        results.append(res)
                except Exception:
                    pass
                prog.progress((idx+1)/len(scan_pool), text=f"Scanned {name} ({idx+1}/{len(scan_pool)})")

        if results:
            st.session_state["scan_results"] = results
            prog.empty()

    if "scan_results" in st.session_state and st.session_state["scan_results"]:
        res    = st.session_state["scan_results"]
        filt   = st.radio("Filter", ["All","🟢 BUY","🔴 SELL","⚪ HOLD"], horizontal=True)
        res_df = pd.DataFrame(res)
        if filt == "🟢 BUY":   res_df = res_df[res_df["_sig"]=="BUY"]
        elif filt == "🔴 SELL": res_df = res_df[res_df["_sig"]=="SELL"]
        elif filt == "⚪ HOLD": res_df = res_df[res_df["_sig"]=="HOLD"]
        disp = res_df.drop(columns=["_sig","_chg"])
        st.dataframe(disp, use_container_width=True, hide_index=True)
        st.caption(f"{len(disp)} stocks | BUY: {(res_df['_sig']=='BUY').sum()} | SELL: {(res_df['_sig']=='SELL').sum()} | HOLD: {(res_df['_sig']=='HOLD').sum()}")
    else:
        st.info("Click '⚡ RUN SCAN' to populate the scanner.")

# ──────────────────────────────────────────────────────────────
# TAB 5: RISK CALCULATOR
# ──────────────────────────────────────────────────────────────
with tab_risk:
    st.markdown(f'<p class="section-header">[ 🛡️ POSITION SIZING & RISK MATRIX — {selected_name} ]</p>', unsafe_allow_html=True)
    r1, r2 = st.columns(2)
    with r1:
        entry_px  = st.number_input("Entry Price ₹", value=round(close,2), step=1.0)
        stop_px   = st.number_input("Stop Loss ₹", value=round(sl_price,2), step=1.0)
        target_px = st.number_input("Take Profit ₹", value=round(tp_price,2), step=1.0)
    with r2:
        cap2    = st.number_input("Capital ₹", value=float(allocated_capital), step=1000.0)
        risk_pct2 = st.slider("Risk %", 0.5, 10.0, float(risk_per_trade), step=0.5)

    if entry_px > stop_px > 0:
        risk_per_share = entry_px - stop_px
        reward_share   = target_px - entry_px
        rr             = reward_share / risk_per_share if risk_per_share > 0 else 0
        cap_at_risk    = cap2 * (risk_pct2 / 100)
        qty_calc       = max(1, int(cap_at_risk / risk_per_share))
        total_val      = qty_calc * entry_px
        max_loss_rs    = qty_calc * risk_per_share
        max_gain_rs    = qty_calc * reward_share

        rc1,rc2,rc3,rc4 = st.columns(4)
        for col, lbl, val, clr in zip([rc1,rc2,rc3,rc4],
            ["Qty to Buy","Total Value","Max Loss","Max Gain"],
            [str(qty_calc), f"₹{total_val:,.0f}", f"₹{max_loss_rs:,.0f}", f"₹{max_gain_rs:,.0f}"],
            ["#00c8ff","#ddeeff","#ff3355","#00e87a"]):
            col.markdown(f'<div class="glass-card"><p class="glass-label">{lbl}</p>'
                         f'<div class="glass-value" style="color:{clr};">{val}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="glass-card" style="text-align:center;"><p class="glass-label">Risk:Reward Ratio</p>'
                    f'<div class="glass-value" style="color:{"#00e87a" if rr>=2 else "#ffcc00" if rr>=1 else "#ff3355"};">1 : {rr:.2f}</div></div>',
                    unsafe_allow_html=True)
    else:
        st.warning("Stop loss must be below entry price.")

# ──────────────────────────────────────────────────────────────
# TAB 6: NEWS & SENTIMENT SCANNER
# ──────────────────────────────────────────────────────────────
with tab_news:
    st.markdown(f'<p class="section-header">[ 📰 NEWS & SENTIMENT SCANNER — {selected_name} ]</p>', unsafe_allow_html=True)
    
    with st.spinner("Fetching latest news articles from Yahoo Finance..."):
        news_items = fetch_ticker_news(selected_ticker)
        
    if news_items:
        sentiment_val, sentiment_cat = analyze_sentiment(news_items)
        
        # Display sentiment metrics
        ns1, ns2 = st.columns([1, 2])
        with ns1:
            sent_color = {"BULLISH": "#00e87a", "BEARISH": "#ff3355", "NEUTRAL": "#ffcc00"}[sentiment_cat]
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;padding:25px 15px;">
                <p class="glass-label">Aggregated News Sentiment</p>
                <div style="font-family:'Orbitron',sans-serif;font-size:2rem;font-weight:900;color:{sent_color};margin:10px 0;">{sentiment_cat}</div>
                <p style="font-size:11px;color:#6a90aa;margin:0;">Score: {sentiment_val:+.2f} (Range -1 to +1)</p>
            </div>""", unsafe_allow_html=True)
        with ns2:
            st.markdown(f"""
            <div class="glass-card" style="padding:15px;">
                <p class="glass-label" style="margin-bottom:8px;">Sentiment Interpretation</p>
                <p style="font-size:12px;color:#a0aec0;line-height:1.6;margin:0;">
                    Our engine scanned the last {len(news_items)} news headlines related to <b>{selected_name}</b> and scored them based on keyword density. 
                    A score above +0.15 is considered <b>Bullish</b>, below -0.15 is <b>Bearish</b>, and in between is <b>Neutral</b>. Use this to gauge short-term sentiment.
                </p>
            </div>""", unsafe_allow_html=True)
            
        st.markdown('<p class="section-header">[ RECENT NEWS HEADLINES ]</p>', unsafe_allow_html=True)
        for item in news_items:
            date_str = item["date"]
            st.markdown(f"""
            <div class="glass-card" style="padding:10px 14px;margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <a href="{item['link']}" target="_blank" style="color:#00c8ff;text-decoration:none;font-weight:600;font-size:13px;font-family:'Inter',sans-serif;">
                        {item['title']}
                    </a>
                    <span style="font-size:10px;color:#4a7090;font-family:'Space Mono',monospace;">{date_str[:16]}</span>
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info(f"No recent news articles found for ticker {selected_ticker}.")

# ──────────────────────────────────────────────────────────────
# TAB 7: PORTFOLIO OPTIMIZER
# ──────────────────────────────────────────────────────────────
with tab_port:
    st.markdown(f'<p class="section-header">[ 💼 QUANT PORTFOLIO OPTIMIZER ]</p>', unsafe_allow_html=True)
    st.caption("ℹ️ Multi-Asset allocation optimizer based on Modern Portfolio Theory (MPT) and daily asset returns.")
    
    selected_keys = st.multiselect("Select Assets for Portfolio", list(ALL_STOCKS.keys()), 
                                   default=[k for k in ALL_STOCKS.keys() if "Reliance" in k or "TCS (" in k or "HDFC Bank" in k or "Infosys" in k][:4])
    
    if len(selected_keys) < 2:
        st.warning("Please select at least 2 assets to optimize a portfolio.")
    else:
        tickers_opt = [ALL_STOCKS[k] for k in selected_keys]
        names_opt = [k.split(" (")[0] for k in selected_keys]
        
        with st.spinner("Downloading historical returns and running Monte Carlo optimizer..."):
            try:
                df_port = yf.download(tickers_opt, period="2y", interval="1d", auto_adjust=True, progress=False)
                if df_port is not None and not df_port.empty:
                    if isinstance(df_port.columns, pd.MultiIndex):
                        close_df = df_port["Close"]
                    else:
                        close_df = df_port
                        
                    returns_df = close_df.pct_change().dropna()
                    
                    num_assets = len(tickers_opt)
                    mean_returns = returns_df.mean()
                    cov_matrix = returns_df.cov()
                    
                    num_portfolios = 2000
                    results = np.zeros((3, num_portfolios))
                    weights_record = []
                    
                    for i in range(num_portfolios):
                        w = np.random.random(num_assets)
                        w /= np.sum(w)
                        p_ret = np.sum(mean_returns * w) * 252
                        p_vol = np.sqrt(np.dot(w.T, np.dot(cov_matrix * 252, w)))
                        p_sharpe = p_ret / p_vol if p_vol > 0 else 0
                        
                        results[0,i] = p_vol
                        results[1,i] = p_ret
                        results[2,i] = p_sharpe
                        weights_record.append(w)
                        
                    max_sharpe_idx = np.argmax(results[2])
                    opt_w = weights_record[max_sharpe_idx]
                    opt_vol = results[0, max_sharpe_idx]
                    opt_ret = results[1, max_sharpe_idx]
                    opt_sharpe = results[2, max_sharpe_idx]
                    
                    min_vol_idx = np.argmin(results[0])
                    min_w = weights_record[min_vol_idx]
                    min_vol = results[0, min_vol_idx]
                    min_ret = results[1, min_vol_idx]
                    min_sharpe = results[2, min_vol_idx]
                    
                    objective = st.radio("Optimization Target", ["Maximize Sharpe Ratio (Target: High Efficiency)", "Minimize Volatility (Target: Low Risk)"], horizontal=True)
                    
                    selected_w = opt_w if "Sharpe" in objective else min_w
                    sel_vol = opt_vol if "Sharpe" in objective else min_vol
                    sel_ret = opt_ret if "Sharpe" in objective else min_ret
                    sel_sharpe = opt_sharpe if "Sharpe" in objective else min_sharpe
                    
                    pm1, pm2, pm3 = st.columns(3)
                    pm1.markdown(f'<div class="glass-card"><p class="glass-label">Expected Annual Return</p>'
                                 f'<div class="glass-value" style="color:#00e87a;">{sel_ret:.1%}</div></div>', unsafe_allow_html=True)
                    pm2.markdown(f'<div class="glass-card"><p class="glass-label">Annualized Volatility</p>'
                                 f'<div class="glass-value" style="color:#ff3355;">{sel_vol:.1%}</div></div>', unsafe_allow_html=True)
                    pm3.markdown(f'<div class="glass-card"><p class="glass-label">Sharpe Ratio</p>'
                                 f'<div class="glass-value" style="color:#00c8ff;">{sel_sharpe:.2f}</div></div>', unsafe_allow_html=True)
                    
                    pc1, pc2 = st.columns(2)
                    with pc1:
                        st.markdown('<p class="section-header">[ 📊 OPTIMAL WEIGHTS ALLOCATION ]</p>', unsafe_allow_html=True)
                        fig_pie = go.Figure(data=[go.Pie(labels=names_opt, values=selected_w, hole=.4,
                                                         marker=dict(colors=["#00c8ff", "#00e87a", "#ffcc00", "#ff6b35", "#7c6ef8"]))])
                        fig_pie.update_layout(
                            height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            font=dict(color="#ddeeff", family="Space Mono", size=10),
                            margin=dict(l=10, r=10, t=10, b=10)
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                        
                    with pc2:
                        st.markdown('<p class="section-header">[ 📈 EFFICIENT FRONTIER SIMULATION ]</p>', unsafe_allow_html=True)
                        fig_scatter = go.Figure()
                        fig_scatter.add_trace(go.Scatter(
                            x=results[0], y=results[1], mode="markers",
                            marker=dict(color=results[2], colorscale="Viridis", showscale=True, colorbar=dict(title="Sharpe", thickness=15)),
                            name="Simulated Portfolios"
                        ))
                        fig_scatter.add_trace(go.Scatter(
                            x=[sel_vol], y=[sel_ret], mode="markers",
                            marker=dict(color="#ff3355", size=12, symbol="star", line=dict(width=1, color="white")),
                            name="Selected Optimal"
                        ))
                        fig_scatter.update_layout(
                            height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            font=dict(color="#ddeeff", family="Space Mono", size=10),
                            xaxis=dict(title="Annualized Volatility", gridcolor="rgba(0,200,255,0.05)"),
                            yaxis=dict(title="Expected Return", gridcolor="rgba(0,200,255,0.05)"),
                            margin=dict(l=10, r=10, t=10, b=10),
                            legend=dict(bgcolor="rgba(7,18,32,0.5)", font=dict(size=8))
                        )
                        st.plotly_chart(fig_scatter, use_container_width=True)
                else:
                    st.error("Failed to load historical returns for selected stocks.")
            except Exception as e:
                st.error(f"Portfolio Optimization Error: {e}")

# ──────────────────────────────────────────────────────────────
# TAB 8: HELP
# ──────────────────────────────────────────────────────────────
with tab_help:
    st.markdown("""
<div class="glass-card">
<p class="section-header">[ INDICATOR REFERENCE ]</p>
<div style="font-family:'Space Mono',monospace;font-size:11px;color:#8ab0cc;line-height:1.9;">
<b style="color:#00c8ff;">RSI (14)</b> — Relative Strength Index. &lt;30 = oversold (potential buy zone). &gt;70 = overbought (potential sell zone).<br>
<b style="color:#00c8ff;">MACD</b> — Moving Average Convergence Divergence. MACD crossing above signal = bullish. Below = bearish.<br>
<b style="color:#00c8ff;">SMA 20/50/200</b> — Simple Moving Averages. SMA20 &gt; SMA50 = uptrend. Price &gt; SMA200 = bull market.<br>
<b style="color:#00c8ff;">Bollinger Bands</b> — Price touching upper band = overbought. Lower band = oversold.<br>
<b style="color:#00c8ff;">ATR (14)</b> — Average True Range. Measures daily volatility in ₹ terms. Used for stop-loss sizing.<br>
<b style="color:#00c8ff;">ARIMA</b> — Auto-Regressive Integrated Moving Average. Statistical time-series forecasting model. Trained on 5-year log prices.<br>
<br>
<b style="color:#ffcc00;">SIGNAL LOGIC:</b> BUY = SMA20&gt;SMA50 + Price&gt;SMA200 + RSI&lt;70 + MACD cross up. SELL = SMA20&lt;SMA50 or RSI&gt;70 + MACD cross down.<br>
<br>
<b style="color:#ff3355;">⚠️ DISCLAIMER:</b> XERCES is a statistical analysis tool. Not SEBI registered. Not financial advice. Always do your own research. Past performance does not guarantee future results.
</div>
</div>
""", unsafe_allow_html=True)
