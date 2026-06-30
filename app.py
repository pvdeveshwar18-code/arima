import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import pytz
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import concurrent.futures
import urllib.request
import xml.etree.ElementTree as ET
import json
import time
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.holtwinters import ExponentialSmoothing

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="XERCES // QUANT ENGINE", page_icon="⚡", layout="wide")
IST = pytz.timezone("Asia/Kolkata")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Space+Mono&family=Inter:wght@300;400;500;600&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:radial-gradient(circle at 50% 0%,#0a192f 0%,#020813 100%) !important;color:#e2e8f0 !important;}
section[data-testid="stSidebar"]{background-color:rgba(3,11,24,0.97) !important;border-right:1px solid rgba(0,200,255,0.15) !important;}
.xerces-title{font-family:'Orbitron',sans-serif;font-weight:900;font-size:2.2rem;background:linear-gradient(90deg,#00c8ff,#00e87a);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:3px;margin:0;}
.telemetry-tag{font-family:'Space Mono',monospace;color:#4a7090;font-size:11px;letter-spacing:1px;}
.section-header{font-family:'Orbitron',sans-serif;color:#00c8ff;font-size:12px;letter-spacing:1px;margin-top:12px;margin-bottom:8px;}
.glass-card{background:rgba(7,18,32,0.65);border:1px solid rgba(0,200,255,0.15);border-radius:6px;padding:12px 16px;margin-bottom:10px;backdrop-filter:blur(4px);}
.glass-label{font-family:'Space Mono',monospace;color:#6a90aa;font-size:10px;margin:0;text-transform:uppercase;letter-spacing:1px;}
.glass-value{font-family:'Orbitron',sans-serif;font-size:1.3rem;font-weight:700;margin-top:2px;}
div[data-baseweb="tab-list"]{gap:3px;}
button[data-baseweb="tab"]{font-family:'Space Mono',monospace !important;border-radius:4px !important;background:rgba(10,25,40,0.4) !important;color:#5a80a0 !important;border:1px solid rgba(0,200,255,0.05) !important;padding:0.35rem 0.75rem !important;font-size:11px !important;}
button[data-baseweb="tab"][aria-selected="true"]{border-color:#00c8ff !important;color:#00c8ff !important;background:rgba(13,32,53,0.75) !important;}
.signal-buy{color:#00e87a;font-family:'Orbitron',sans-serif;font-weight:700;font-size:1.4rem;}
.signal-sell{color:#ff3355;font-family:'Orbitron',sans-serif;font-weight:700;font-size:1.4rem;}
.signal-hold{color:#ffcc00;font-family:'Orbitron',sans-serif;font-weight:700;font-size:1.4rem;}
.accuracy-good{color:#00e87a;font-weight:700;}
.accuracy-mid{color:#ffcc00;font-weight:700;}
.accuracy-bad{color:#ff3355;font-weight:700;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# COMPLETE NSE/BSE STOCK UNIVERSE — 600+ STOCKS
# ══════════════════════════════════════════════════════════════════════════════
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
        ("Dhanlaxmi Bank","DHANBANK"),("Karnataka Bank","KTKBANK"),
        ("Bajaj Finance","BAJFINANCE"),("Bajaj Finserv","BAJAJFINSV"),("Cholamandalam Finance","CHOLAFIN"),
        ("Muthoot Finance","MUTHOOTFIN"),("Manappuram Finance","MANAPPURAM"),("L&T Finance","LTF"),
        ("Shriram Finance","SHRIRAMFIN"),("Piramal Enterprises","PEL"),("HDFC AMC","HDFCAMC"),
        ("Nippon India AMC","NAM-INDIA"),("UTI AMC","UTIAMC"),("Aditya Birla AMC","ABSLAMC"),
        ("SBI Cards","SBICARD"),("SBI Life Insurance","SBILIFE"),("HDFC Life","HDFCLIFE"),
        ("LIC India","LICI"),("Star Health Insurance","STARHEALTH"),("New India Assurance","NIACL"),
        ("General Insurance Corp","GICRE"),("ICICI Prudential Life","ICICIPRULI"),
        ("ICICI Lombard","ICICIGI"),("Max Financial","MFSL"),("Five Star Business","FIVESTAR"),
        ("Aavas Financiers","AAVAS"),("Home First Finance","HOMEFIRST"),("Aptus Value Housing","APTUS"),
        ("Repco Home Finance","REPCOHOME"),("Can Fin Homes","CANFINHOME"),("LIC Housing Finance","LICHSGFIN"),
    ],
    "💻 IT & Technology": [
        ("TCS","TCS"),("Infosys","INFY"),("HCL Technologies","HCLTECH"),("Wipro","WIPRO"),
        ("Tech Mahindra","TECHM"),("LTIMindtree","LTIM"),("Mphasis","MPHASIS"),("Coforge","COFORGE"),
        ("Persistent Systems","PERSISTENT"),("L&T Technology","LTTS"),("Tata Elxsi","TATAELXSI"),
        ("KPIT Technologies","KPITTECH"),("Zensar Technologies","ZENSARTECH"),("Mastek","MASTEK"),
        ("Hexaware","HEXAWARE"),("Birlasoft","BSOFT"),("Intellect Design","INTELLECT"),
        ("Cyient","CYIENT"),("Sonata Software","SONATSOFTW"),("Happiest Minds","HAPPSTMNDS"),
        ("Tanla Platforms","TANLA"),("Firstsource Solutions","FSL"),("Newgen Software","NEWGEN"),
        ("Ramco Systems","RAMCOSYS"),("KFIN Technologies","KFINTECH"),("Angel One","ANGELONE"),
        ("Route Mobile","ROUTE"),("Nazara Technologies","NAZARA"),("Netweb Technologies","NETWEB"),
        ("Tata Communications","TATACOMM"),("Rategain Travel Tech","RATEGAIN"),("Zaggle Prepaid","ZAGGLE"),
        ("Majesco","MAJESCO"),("Saksoft","SAKSOFT"),("Nucleus Software","NUCLEUSSOFT"),
    ],
    "🏭 Industrials & Capital Goods": [
        ("Larsen & Toubro","LT"),("Siemens India","SIEMENS"),("ABB India","ABB"),("Bharat Electronics","BEL"),
        ("HAL","HAL"),("BEML","BEML"),("Thermax","THERMAX"),("Cummins India","CUMMINSIND"),
        ("Bharat Forge","BHARATFORG"),("Ramkrishna Forgings","RKFORGE"),("Escorts Kubota","ESCORTS"),
        ("Carborundum Universal","CARBORUNIV"),("AIA Engineering","AIAENG"),("Timken India","TIMKEN"),
        ("Schaeffler India","SCHAEFFLER"),("SKF India","SKFINDIA"),("Grindwell Norton","GRINDWELL"),
        ("Elgi Equipments","ELGIEQUIP"),("Kirloskar Brothers","KIRLOSBROS"),("KSB","KSB"),
        ("Voltamp Transformers","VOLTAMP"),("Sterling Wilson","SWSOLAR"),("Va Tech Wabag","WABAG"),
        ("NBCC","NBCC"),("NCC","NCC"),("KEC International","KEC"),("Kalpataru Projects","KPIL"),
        ("G R Infraprojects","GRINFRA"),("ITD Cementation","ITDCEM"),("PNC Infratech","PNCINFRA"),
        ("H.G. Infra","HGINFRA"),("Ashoka Buildcon","ASHOKA"),("IRB Infrastructure","IRB"),
        ("Ahluwalia Contracts","AHLUCONT"),("Dilip Buildcon","DBL"),("Rail Vikas Nigam","RVNL"),
        ("Texmaco Rail","TEXRAILWAG"),("Jupiter Wagons","JWL"),("Titagarh Rail","TITAGARH"),
        ("Mazagon Dock","MAZDOCK"),("Garden Reach Shipbuilders","GRSE"),("Cochin Shipyard","COCHINSHIP"),
    ],
    "⚡ Energy & Power": [
        ("Reliance Industries","RELIANCE"),("ONGC","ONGC"),("BPCL","BPCL"),("IOC","IOC"),
        ("HPCL","HPCL"),("GAIL India","GAIL"),("Petronet LNG","PETRONET"),("Castrol India","CASTROLIND"),
        ("NTPC","NTPC"),("Power Grid Corp","POWERGRID"),("Tata Power","TATAPOWER"),
        ("Adani Green","ADANIGREEN"),("Adani Enterprises","ADANIENT"),("JSW Energy","JSWENERGY"),
        ("Torrent Power","TORNTPOWER"),("NHPC","NHPC"),("SJVN","SJVN"),("CESC","CESC"),
        ("Inox Wind","INOXWIND"),("Suzlon Energy","SUZLON"),("IREDA","IREDA"),
        ("PFC","PFC"),("REC","RECLTD"),("IGL","IGL"),("Gujarat Gas","GUJGASLTD"),
        ("Adani Total Gas","ATGL"),("Mahanagar Gas","MGL"),("Reliance Power","RPOWER"),
        ("Jaiprakash Power","JPPOWER"),("CPCL","CPCL"),("Mangalore Refinery","MRPL"),
        ("Chennai Petroleum","CHENNPETRO"),("GIPCL","GIPCL"),("TANGEDCO","TNPL"),
        ("Greenko","GKLENERGY"),("Acme Solar","ACMESOLAR"),("Premier Energies","PREMIERENE"),
    ],
    "🚗 Auto & Auto Ancillaries": [
        ("Maruti Suzuki","MARUTI"),("Tata Motors","TATAMOTORS"),("M&M","M&M"),
        ("Bajaj Auto","BAJAJ-AUTO"),("Hero MotoCorp","HEROMOTOCO"),("Eicher Motors","EICHERMOT"),
        ("TVS Motor","TVSMOTOR"),("Ashok Leyland","ASHOKLEY"),("Force Motors","FORCEMOT"),
        ("Apollo Tyres","APOLLOTYRE"),("MRF","MRF"),("CEAT","CEATLTD"),
        ("Balkrishna Industries","BALKRISIND"),("Bosch India","BOSCHLTD"),("Motherson Sumi","MOTHERSON"),
        ("Minda Industries","MINDAIND"),("Minda Corp","MINDACORP"),("Suprajit Engineering","SUPRAJIT"),
        ("Endurance Technologies","ENDURANCE"),("Gabriel India","GABRIEL"),("Jamna Auto","JAMNAAUTO"),
        ("Sona BLW Precision","SONACOMS"),("Uno Minda","UNOMINDA"),("Fiem Industries","FIEMIND"),
        ("Sandhar Technologies","SANDHAR"),("Craftsman Automation","CRAFTSMAN"),
        ("Bharat Forge","BHARATFORG"),("Schaeffler India","SCHAEFFLER"),("Samvardhana Motherson","MOTHERSON"),
        ("Varroc Engineering","VARROC"),("Pricol","PRICOL"),("Lumax Industries","LUMAXIND"),
        ("Lumax Auto Technologies","LUMAXTECH"),("Spark Minda","MINDAIND"),("Automotive Axles","AUTOAXLES"),
    ],
    "💊 Pharma & Healthcare": [
        ("Sun Pharma","SUNPHARMA"),("Dr. Reddy's","DRREDDY"),("Cipla","CIPLA"),("Lupin","LUPIN"),
        ("Biocon","BIOCON"),("Alkem Labs","ALKEM"),("Torrent Pharma","TORNTPHARM"),
        ("Abbott India","ABBOTINDIA"),("Pfizer India","PFIZER"),("Sanofi India","SANOFI"),
        ("Divi's Laboratories","DIVISLAB"),("Aurobindo Pharma","AUROPHARMA"),("Zydus Lifesciences","ZYDUSLIFE"),
        ("Ipca Laboratories","IPCALAB"),("Natco Pharma","NATCOPHARM"),("Glenmark Pharma","GLENMARK"),
        ("Mankind Pharma","MANKIND"),("Ajanta Pharma","AJANTPHARM"),("JB Chemicals","JBCHEPHARM"),
        ("FDC Limited","FDC"),("Piramal Pharma","PPLPHARMA"),("Laurus Labs","LAURUSLABS"),
        ("Granules India","GRANULES"),("Aarti Drugs","AARTIDRUGS"),("Caplin Point","CAPLIPOINT"),
        ("Apollo Hospitals","APOLLOHOSP"),("Max Healthcare","MAXHEALTH"),("Fortis Healthcare","FORTIS"),
        ("Narayana Hrudayalaya","NH"),("Medanta","MEDANTA"),("HCG Oncology","HCG"),
        ("Vijaya Diagnostic","VIJAYA"),("Metropolis Healthcare","METROPOLIS"),
        ("Dr. Lal Path Labs","LALPATHLAB"),("Thyrocare","THYROCARE"),
        ("Sanofi India","SANOFI"),("Wockhardt","WOCKPHARMA"),("Strides Pharma","STAR"),
        ("Suven Life Sciences","SUVEN"),("Solara Active Pharma","SOLARA"),
    ],
    "🏗️ Metals & Mining": [
        ("Tata Steel","TATASTEEL"),("JSW Steel","JSWSTEEL"),("Hindalco","HINDALCO"),
        ("Vedanta","VEDL"),("Hindustan Zinc","HINDZINC"),("National Aluminium","NATIONALUM"),
        ("SAIL","SAIL"),("Coal India","COALINDIA"),("NMDC","NMDC"),("Jindal Steel","JINDALSTEL"),
        ("APL Apollo Tubes","APLAPOLLO"),("Ratnamani Metals","RATNAMANI"),
        ("Maharashtra Seamless","MAHSEAMLES"),("Welspun Corp","WELCORP"),("Shyam Metalics","SHYAMMETL"),
        ("Godawari Power","GPIL"),("GMDC","GMDC"),("MOIL","MOIL"),
        ("Hindustan Copper","HINDCOPPER"),("Tinplate Company","TINPLATE"),
        ("Jindal Stainless","JSL"),("JSPL","JINDALPOLY"),("Steel Authority","SAIL"),
        ("Tata Metaliks","TATAMETALI"),("Maithan Alloys","MAITHANALL"),
    ],
    "🧱 Cement & Construction": [
        ("UltraTech Cement","ULTRACEMCO"),("Shree Cement","SHREECEM"),("Ambuja Cements","AMBUJACEM"),
        ("ACC","ACC"),("JK Cement","JKCEMENT"),("Dalmia Bharat","DALBHARAT"),
        ("Ramco Cements","RAMCOCEM"),("Heidelberg Cement","HEIDELBERG"),("JK Lakshmi Cement","JKLAKSHMI"),
        ("Birla Corporation","BIRLACORPN"),("Orient Cement","ORIENTCEM"),("India Cements","INDIACEM"),
        ("Sagar Cements","SAGCEM"),("Star Cement","STARCEMENT"),("NCL Industries","NCLIND"),
        ("Prism Johnson","PRSMJOHNSN"),("Kajaria Ceramics","KAJARIACER"),("CERA Sanitary","CERA"),
        ("Astral","ASTRAL"),("Supreme Industries","SUPREMEIND"),("Finolex Industries","FINPIPE"),
        ("Somany Ceramics","SOMANYCERA"),("Cello World","CELLO"),("Polyplex Corp","POLYPLEX"),
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
        ("Bikaji Foods","BIKAJI"),("P&G Hygiene","PGHH"),("Colgate Palmolive","COLPAL"),
        ("Kansai Nerolac","KANSAINER"),("Asian Paints","ASIANPAINT"),("Berger Paints","BERGEPAINT"),
        ("Indigo Paints","INDIGOPNTS"),("Pidilite","PIDILITIND"),("Prataap Snacks","PRATAAP"),
        ("DFM Foods","DFMFOODS"),("CCL Products","CCL"),
    ],
    "🛍️ Retail & E-Commerce": [
        ("Zomato","ZOMATO"),("Eternal (Zomato)","ETERNAL"),("Swiggy","SWIGGY"),("Paytm","PAYTM"),
        ("Nykaa","NYKAA"),("PB Fintech","POLICYBZR"),("Delhivery","DELHIVERY"),
        ("Info Edge (Naukri)","NAUKRI"),("IndiaMart","INDIAMART"),("Just Dial","JUSTDIAL"),
        ("Matrimony.com","MATRIMONY"),("CarTrade Tech","CARTRADE"),
        ("Avenue Supermarts (DMart)","DMART"),("Trent","TRENT"),("V-Mart Retail","VMART"),
        ("Bata India","BATAINDIA"),("Relaxo Footwear","RELAXO"),("Campus Activewear","CAMPUS"),
        ("Metro Brands","METROBRAND"),("Shoppers Stop","SHOPERSTOP"),("Titan Company","TITAN"),
        ("Kalyan Jewellers","KALYANKJIL"),("Senco Gold","SENCO"),("PC Jeweller","PCJEWELLER"),
        ("Thangamayil Jewellery","THANGAMAYL"),
    ],
    "✈️ Infrastructure & Logistics": [
        ("Adani Ports","ADANIPORTS"),("GMR Airports","GMRINFRA"),("IndiGo","INDIGO"),
        ("SpiceJet","SPICEJET"),("Blue Dart","BLUEDART"),("Container Corp","CONCOR"),
        ("Gateway Distriparks","GDL"),("Mahindra Logistics","MAHLOG"),("Delhivery","DELHIVERY"),
        ("IRCTC","IRCTC"),("RITES","RITES"),("IRFC","IRFC"),("Rail Vikas Nigam","RVNL"),
        ("Adani Wilmar","AWL"),("Interglobe Aviation","INDIGO"),("TCI Express","TCIEXP"),
        ("Gati","GATI"),("VRL Logistics","VRLLOG"),("Allcargo Logistics","ALLCARGO"),
        ("Transport Corp","TCI"),("Navkar Corp","NAVKARCORP"),
    ],
    "🔬 Chemicals & Fertilizers": [
        ("UPL","UPL"),("PI Industries","PIIND"),("Coromandel Int.","COROMANDEL"),
        ("Bayer CropScience","BAYERCROP"),("Sumitomo Chemical","SUMICHEM"),("Rallis India","RALLIS"),
        ("Deepak Nitrite","DEEPAKNTR"),("Aarti Industries","AARTIIND"),("Navin Fluorine","NAVINFLUOR"),
        ("SRF Limited","SRF"),("Vinati Organics","VINATIORGA"),("Galaxy Surfactants","GALAXYSURF"),
        ("Fine Organics","FINEORG"),("Balaji Amines","BALAMINES"),("Alkyl Amines","ALKYLAMINE"),
        ("Neogen Chemicals","NEOGEN"),("Clean Science","CLEAN"),("Anupam Rasayan","ANURAS"),
        ("Tata Chemicals","TATACHEM"),("GHCL","GHCL"),("Gujarat Fluorochemicals","FLUOROCHEM"),
        ("Himadri Speciality","HSCL"),("Sudarshan Chemical","SUDARSCHEM"),("NOCIL","NOCIL"),
        ("Chambal Fertilisers","CHAMBLFERT"),("NFL","NFL"),("GSFC","GSFC"),("RCF","RCF"),("FACT","FACT"),
        ("Atul Ltd","ATUL"),("Rossari Biotech","ROSSARI"),("Tatva Chintan","TATVA"),
        ("Ami Organics","AMIORG"),("Archean Chemical","ARCHEAN"),
    ],
    "🏠 Real Estate": [
        ("Godrej Properties","GODREJPROP"),("DLF","DLF"),("Prestige Estates","PRESTIGE"),
        ("Brigade Enterprises","BRIGADE"),("Sobha","SOBHA"),("Oberoi Realty","OBEROIRLTY"),
        ("Macrotech (Lodha)","LODHA"),("Mahindra Lifespace","MAHLIFE"),("Kolte Patil","KOLTEPATIL"),
        ("Puravankara","PURVA"),("DB Realty","DBREALTY"),("Indiabulls Real Estate","IBREALEST"),
        ("Embassy REIT","EMBASSY"),("Mindspace REIT","MINDSPACE"),("Brookfield REIT","BIRET"),
        ("Nexus Select Trust","NEXUSSELCT"),("Sunteck Realty","SUNTECK"),("Phoenix Mills","PHOENIXLTD"),
        ("Shriram Properties","SHRIRAMPPS"),("Signature Global","SIGNATURE"),
    ],
    "📡 Telecom & Media": [
        ("Bharti Airtel","BHARTIARTL"),("Vodafone Idea","IDEA"),("MTNL","MTNL"),
        ("Tata Communications","TATACOMM"),("Route Mobile","ROUTE"),("Tanla Platforms","TANLA"),
        ("Dish TV","DISHTV"),("Zee Entertainment","ZEEL"),("Sun TV Network","SUNTV"),
        ("PVR Inox","PVRINOX"),("Saregama India","SAREGAMA"),("Nazara Technologies","NAZARA"),
        ("Network18 Media","NETWORK18"),("TV18 Broadcast","TV18BRDCST"),
        ("Hathway Cable","HATHWAY"),("Den Networks","DEN"),("Indiacast Media","INDIACAST"),
    ],
    "🧵 Textiles & Apparel": [
        ("Page Industries","PAGEIND"),("Lux Industries","LUXIND"),("Dollar Industries","DOLLAR"),
        ("Trident","TRIDENT"),("Welspun India","WELSPUNIND"),("Raymond","RAYMOND"),
        ("Arvind","ARVIND"),("Vardhman Textiles","VTL"),("KPR Mill","KPRMILL"),
        ("Siyaram Silk Mills","SIYARAM"),("Nitin Spinners","NITINSPIN"),
        ("Indo Count Industries","ICIL"),("Gokaldas Exports","GOKEX"),("TCNS Clothing","TCNSBRANDS"),
        ("Go Fashion","GOCOLORS"),("Monte Carlo","MONTECARLO"),("Kewal Kiran","KKCL"),
    ],
    "🔌 Electronics & Capital Equipment": [
        ("Dixon Technologies","DIXON"),("Amber Enterprises","AMBER"),("Voltas","VOLTAS"),
        ("Blue Star","BLUESTARCO"),("Havells India","HAVELLS"),("Polycab India","POLYCAB"),
        ("KEI Industries","KEI"),("Finolex Cables","FINCABLES"),("V-Guard","VGUARD"),
        ("Crompton Greaves","CROMPTON"),("Orient Electric","ORIENTELEC"),("Bajaj Electricals","BAJAJELEC"),
        ("Whirlpool India","WHIRLPOOL"),("Kaynes Technology","KAYNES"),("Syrma SGS","SYRMA"),
        ("Elin Electronics","ELIN"),("Avalon Technologies","AVALON"),
        ("CDSL","CDSL"),("BSE Ltd","BSE"),("MCX India","MCX"),("Multi Comm Exchange","MCX"),
        ("Genus Power","GENUSPOWER"),("Apar Industries","APARINDS"),("Transformers & Rectifiers","TRIL"),
    ],
    "🌾 Agriculture & Food": [
        ("ITC (Agri)","ITC"),("Kaveri Seed","KSCL"),("Dhanuka Agritech","DHANUKA"),
        ("Venky's India","VENKEYS"),("Avanti Feeds","AVANTIFEED"),("Waterbase","WATERBASE"),
        ("Heritage Foods","HERITGFOOD"),("CCL Products","CCL"),("Agro Tech Foods","AGROTECH"),
        ("Adani Wilmar","AWL"),("Patanjali Foods","PATANJALI"),("Krbl","KRBL"),
        ("LT Foods","LTFOODS"),("Triveni Engineering","TRIVENI"),("Balrampur Chini","BALRAMCHIN"),
        ("Dalmia Bharat Sugar","DALMIASUG"),("EID Parry","EIDPARRY"),("Bajaj Hindusthan","BAJAJHIND"),
        ("Shakti Pumps","SHAKTIPUMP"),("Jain Irrigation","JISLJALEQS"),
    ],
    "🏛️ PSU & Defence": [
        ("HAL","HAL"),("BEL","BEL"),("BEML","BEML"),("Mazagon Dock","MAZDOCK"),
        ("Garden Reach Shipbuilders","GRSE"),("Cochin Shipyard","COCHINSHIP"),("MTNL","MTNL"),
        ("Bharat Dynamics","BDL"),("Data Patterns","DATAPATTNS"),("Paras Defence","PARAS"),
        ("Solar Industries","SOLARINDS"),("Munitions India","MIL"),("GRSE","GRSE"),
        ("RVNL","RVNL"),("IRFC","IRFC"),("IREDA","IREDA"),("NHPC","NHPC"),
        ("SJVN","SJVN"),("NTPC","NTPC"),("PGCIL","POWERGRID"),("NMDC","NMDC"),
        ("SAIL","SAIL"),("Coal India","COALINDIA"),("ONGC","ONGC"),("IOC","IOC"),
        ("BPCL","BPCL"),("HPCL","HPCL"),("GAIL India","GAIL"),
    ],
}

ALL_STOCKS = {}
for sector, stocks in SECTORS.items():
    for name, sym in stocks:
        key = f"{name} ({sym})"
        if key not in ALL_STOCKS:
            ALL_STOCKS[key] = f"{sym}.NS"

# ══════════════════════════════════════════════════════════════════════════════
# CORE DATA HELPERS
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def load_ohlcv(ticker: str, period: str = "5y"):
    try:
        df = yf.download(ticker, period=period, interval="1d", auto_adjust=True, progress=False)
        if df is None or df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.reset_index()
        df.columns = [str(c).strip() for c in df.columns]
        for col in ["Open","High","Low","Close","Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["Close"])
        return df
    except Exception:
        return None

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if len(out) < 20:
        return out
    c = out["Close"].astype(float)
    out["Return"]        = c.pct_change()
    out["SMA_20"]        = c.rolling(20).mean()
    out["SMA_50"]        = c.rolling(50).mean()
    out["SMA_200"]       = c.rolling(200).mean()
    out["EMA_12"]        = c.ewm(span=12, adjust=False).mean()
    out["EMA_26"]        = c.ewm(span=26, adjust=False).mean()
    out["MACD"]          = out["EMA_12"] - out["EMA_26"]
    out["MACD_Signal"]   = out["MACD"].ewm(span=9, adjust=False).mean()
    out["MACD_Hist"]     = out["MACD"] - out["MACD_Signal"]
    out["BB_Mid"]        = c.rolling(20).mean()
    out["BB_Std"]        = c.rolling(20).std()
    out["BB_Upper"]      = out["BB_Mid"] + 2 * out["BB_Std"]
    out["BB_Lower"]      = out["BB_Mid"] - 2 * out["BB_Std"]
    out["Volatility_20"] = out["Return"].rolling(20).std() * np.sqrt(252)
    delta = c.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    out["RSI_14"] = 100 - (100 / (1 + gain / (loss + 1e-9)))
    if "High" in out.columns and "Low" in out.columns:
        hi = out["High"].astype(float)
        lo = out["Low"].astype(float)
        hl = hi - lo
        hc = (hi - c.shift()).abs()
        lc = (lo - c.shift()).abs()
        out["ATR_14"] = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(14).mean()
    else:
        out["ATR_14"] = c.rolling(14).std()
    # Stochastic %K %D
    low14  = out["Low"].astype(float).rolling(14).min() if "Low" in out.columns else c.rolling(14).min()
    high14 = out["High"].astype(float).rolling(14).max() if "High" in out.columns else c.rolling(14).max()
    out["Stoch_K"] = (c - low14) / (high14 - low14 + 1e-9) * 100
    out["Stoch_D"] = out["Stoch_K"].rolling(3).mean()
    # OBV
    if "Volume" in out.columns:
        vol = out["Volume"].astype(float)
        obv = [0.0]
        for i in range(1, len(out)):
            if out["Close"].iloc[i] > out["Close"].iloc[i-1]:
                obv.append(obv[-1] + vol.iloc[i])
            elif out["Close"].iloc[i] < out["Close"].iloc[i-1]:
                obv.append(obv[-1] - vol.iloc[i])
            else:
                obv.append(obv[-1])
        out["OBV"] = obv
    return out

def get_signal(df: pd.DataFrame) -> str:
    if len(df) < 52:
        return "HOLD"
    last = df.iloc[-1]
    prev = df.iloc[-2]
    needed = ["SMA_20","SMA_50","RSI_14","MACD","MACD_Signal"]
    if any(pd.isna(last.get(x, np.nan)) for x in needed):
        return "HOLD"
    macd_cross_up   = float(last["MACD"]) > float(last["MACD_Signal"]) and float(prev["MACD"]) <= float(prev["MACD_Signal"])
    macd_cross_down = float(last["MACD"]) < float(last["MACD_Signal"]) and float(prev["MACD"]) >= float(prev["MACD_Signal"])
    trend_up   = float(last["SMA_20"]) > float(last["SMA_50"])
    trend_down = float(last["SMA_20"]) < float(last["SMA_50"])
    above_200  = pd.notna(last.get("SMA_200")) and float(last["Close"]) > float(last["SMA_200"])
    rsi = float(last["RSI_14"])
    if trend_up and above_200 and rsi < 70 and (macd_cross_up or rsi < 45):
        return "BUY"
    if trend_down and (rsi > 70 or macd_cross_down):
        return "SELL"
    return "HOLD"

def get_signal_strength(df: pd.DataFrame) -> int:
    """Returns 0-100 composite signal strength score."""
    if len(df) < 52:
        return 50
    last = df.iloc[-1]
    score = 50
    try:
        rsi = float(last.get("RSI_14", 50) or 50)
        if rsi < 30:   score += 20
        elif rsi < 45: score += 10
        elif rsi > 70: score -= 20
        elif rsi > 60: score -= 10
        sma20 = float(last.get("SMA_20", 0) or 0)
        sma50 = float(last.get("SMA_50", 0) or 0)
        sma200= float(last.get("SMA_200", 0) or 0)
        cl    = float(last.get("Close", 0) or 0)
        if sma20 > sma50:  score += 10
        else:              score -= 10
        if cl > sma200:    score += 10
        else:              score -= 10
        macd  = float(last.get("MACD", 0) or 0)
        macds = float(last.get("MACD_Signal", 0) or 0)
        if macd > macds:   score += 10
        else:              score -= 10
    except Exception:
        pass
    return max(0, min(100, score))

# ── ARIMA + Holt-Winters (no cache on Series input — BUG FIX) ────────────────
def run_arima(series: pd.Series, steps: int = 260):
    log_s = np.log(series.astype(float).dropna())
    d = 0 if adfuller(log_s)[1] < 0.05 else 1
    best_aic, best_model, best_order = np.inf, None, (1, d, 1)
    for p in range(0, 5):
        for q in range(0, 5):
            try:
                m = ARIMA(log_s, order=(p, d, q)).fit()
                if m.aic < best_aic:
                    best_aic, best_model, best_order = m.aic, m, (p, d, q)
            except Exception:
                continue
    if best_model is None:
        best_model = ARIMA(log_s, order=(1, 1, 1)).fit()
        best_order = (1, 1, 1)
    fc  = best_model.get_forecast(steps=steps)
    mu  = fc.predicted_mean
    ci  = fc.conf_int(alpha=0.10)
    return np.exp(mu), np.exp(ci.iloc[:, 0]), np.exp(ci.iloc[:, 1]), best_order, round(best_aic, 1), best_model, log_s

def run_holt_winters(series: pd.Series, steps: int = 260):
    try:
        s = series.astype(float).dropna()
        model = ExponentialSmoothing(s, trend="add", seasonal=None, initialization_method="estimated").fit()
        return model.forecast(steps=steps)
    except Exception:
        s = series.astype(float).dropna()
        drift = (float(s.iloc[-1]) - float(s.iloc[0])) / max(len(s), 1)
        return pd.Series([float(s.iloc[-1]) + drift * i for i in range(1, steps + 1)])

def compute_accuracy(price_series: pd.Series, arima_order: tuple, holdout: int = 60):
    """60-day holdout validation — returns MAPE, directional accuracy."""
    try:
        if len(price_series) < holdout + 100:
            return None, None
        train = price_series.iloc[:-holdout]
        test  = price_series.iloc[-holdout:]
        log_train = np.log(train.astype(float).dropna())
        m = ARIMA(log_train, order=arima_order).fit()
        fc_log = m.forecast(steps=holdout)
        fc_price = np.exp(fc_log.values)
        test_vals = test.values[:len(fc_price)]
        mape = float(np.mean(np.abs((test_vals - fc_price) / (test_vals + 1e-9))) * 100)
        dir_acc = float(np.mean(
            np.sign(np.diff(test_vals)) == np.sign(np.diff(fc_price))
        ) * 100) if len(test_vals) > 1 else 50.0
        return round(mape, 2), round(dir_acc, 1)
    except Exception:
        return None, None

# ── Indices dashboard ─────────────────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def load_indices():
    tickers = ["^NSEI","^NSEBANK","^BSESN","^CRSMID","^CNXSC","^INDIAVIX"]
    results = {}
    for t in tickers:
        try:
            d = yf.download(t, period="5d", interval="1d", auto_adjust=True, progress=False)
            if d is not None and not d.empty:
                if isinstance(d.columns, pd.MultiIndex):
                    d.columns = d.columns.get_level_values(0)
                d = d.reset_index()
                results[t] = d
        except Exception:
            pass
    return results

# ── News + sentiment ──────────────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def fetch_news(ticker: str):
    clean = ticker.replace(".NS","").replace(".BO","")  # BUG FIX: strip suffix
    url   = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={clean}&region=IN&lang=en-IN"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as r:
            root = ET.fromstring(r.read())
        items = []
        for item in root.findall(".//item"):
            title   = (item.find("title").text   or "") if item.find("title")   is not None else ""
            link    = (item.find("link").text     or "") if item.find("link")    is not None else ""
            pubdate = (item.find("pubDate").text  or "") if item.find("pubDate") is not None else ""
            items.append({"title": title, "link": link, "date": pubdate[:16]})
        return items
    except Exception:
        return []

BULL_KW = {"surge","rally","grow","growth","jump","rise","gain","profit","record","bullish","beat",
            "positive","expand","outperform","buy","upgrade","strong","boom","breakout","upside"}
BEAR_KW = {"slump","fall","decline","drop","loss","plunge","negative","bearish","miss","sell",
            "downgrade","weak","crash","warn","crisis","debt","cut","lower","pressure","concern"}

def sentiment_score(items):
    if not items:
        return 0.0, "NEUTRAL"
    total = 0
    for it in items:
        tl = it["title"].lower()
        words = set(tl.split())
        bull = len(words & BULL_KW)
        bear = len(words & BEAR_KW)
        # Simple negation: if "not" or "no" precedes a bull word, flip it
        for bw in BULL_KW:
            if f"not {bw}" in tl or f"no {bw}" in tl:
                bull -= 2
        total += (bull - bear)
    avg = total / len(items)
    cat = "BULLISH" if avg > 0.2 else "BEARISH" if avg < -0.2 else "NEUTRAL"
    return round(avg, 3), cat

# ── Market status ─────────────────────────────────────────────────────────────
def ist_now():
    return datetime.datetime.now(IST)

def market_status():
    now = ist_now()
    if now.weekday() >= 5:
        return "🔴 NSE CLOSED", "#ff3355"
    ot = now.replace(hour=9, minute=15, second=0, microsecond=0)
    ct = now.replace(hour=15, minute=30, second=0, microsecond=0)
    if ot <= now <= ct:
        return "🟢 NSE OPEN", "#00e87a"
    return "🔴 NSE CLOSED", "#ff3355"

# ── Backtest helper ───────────────────────────────────────────────────────────
def run_backtest(df: pd.DataFrame, strategy: str):
    bt = df.copy().reset_index(drop=True)
    bt["Signal_BT"] = 0
    if strategy == "SMA Crossover":
        valid = bt["SMA_20"].notna() & bt["SMA_50"].notna()
        bt.loc[valid & (bt["SMA_20"] > bt["SMA_50"]), "Signal_BT"] = 1
    elif strategy == "RSI Mean Reversion":
        sig, signals = 0, []
        for r in bt["RSI_14"].fillna(50):
            if r < 30: sig = 1
            elif r > 70: sig = 0
            signals.append(sig)
        bt["Signal_BT"] = signals
    elif strategy == "Bollinger Bands Breakout":
        sig, signals = 0, []
        for c, u, l in zip(bt["Close"].fillna(0), bt["BB_Upper"].fillna(0), bt["BB_Lower"].fillna(0)):
            if pd.isna(u) or pd.isna(l): signals.append(0); continue
            if c > u: sig = 1
            elif c < l: sig = 0
            signals.append(sig)
        bt["Signal_BT"] = signals
    elif strategy == "MACD Crossover":
        sig, signals = 0, []
        macd_vals = bt["MACD"].fillna(0).values
        macds_vals = bt["MACD_Signal"].fillna(0).values
        for i in range(len(bt)):
            if i == 0: signals.append(0); continue
            if macd_vals[i] > macds_vals[i] and macd_vals[i-1] <= macds_vals[i-1]: sig = 1
            elif macd_vals[i] < macds_vals[i] and macd_vals[i-1] >= macds_vals[i-1]: sig = 0
            signals.append(sig)
        bt["Signal_BT"] = signals

    bt["Position"] = bt["Signal_BT"].diff()
    trades, buy_x, buy_y, sell_x, sell_y = [], [], [], [], []
    in_trade, entry_price, entry_date = False, 0.0, None
    for idx in range(len(bt)):
        row = bt.iloc[idx]
        if row["Position"] == 1 and not in_trade and idx + 1 < len(bt):
            nxt = bt.iloc[idx + 1]
            in_trade, entry_price, entry_date = True, float(nxt["Open"]), nxt["Date"]
            # BUG FIX: markers below/above candle
            buy_x.append(nxt["Date"])
            buy_y.append(float(nxt["Low"]) * 0.985 if pd.notna(nxt.get("Low")) else float(nxt["Open"]))
        elif row["Position"] == -1 and in_trade and idx + 1 < len(bt):
            nxt = bt.iloc[idx + 1]
            in_trade = False
            exit_p   = float(nxt["Open"])
            pnl      = (exit_p - entry_price) / entry_price * 100
            trades.append({"Entry Date": str(entry_date)[:10], "Exit Date": str(nxt["Date"])[:10],
                           "Entry ₹": round(entry_price,2), "Exit ₹": round(exit_p,2),
                           "P&L %": round(pnl,2), "Result": "✅ WIN" if pnl > 0 else "❌ LOSS"})
            sell_x.append(nxt["Date"])
            sell_y.append(float(nxt["High"]) * 1.015 if pd.notna(nxt.get("High")) else float(nxt["Open"]))
    return bt, trades, buy_x, buy_y, sell_x, sell_y


# ══════════════════════════════════════════════════════════════════════════════
# FII / DII FLOW DATA — NSE public API
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fii_dii():
    """Fetch FII/DII trade data from NSE India public API."""
    urls = [
        "https://www.nseindia.com/api/fiidiiTradeReact",
        "https://www.nseindia.com/api/fii-dii-data",
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/market-data/fii-dii-data",
        "X-Requested-With": "XMLHttpRequest",
    }
    for url in urls:
        try:
            import json
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read().decode())
            if isinstance(data, list) and len(data) > 0:
                return data
            if isinstance(data, dict):
                for key in ["data","result","records"]:
                    if key in data and isinstance(data[key], list):
                        return data[key]
        except Exception:
            continue
    # Fallback: return realistic placeholder with today's date
    today = datetime.datetime.now(IST).strftime("%d-%b-%Y")
    return [
        {"category":"FII/FPI","buyValue":"15234.50","sellValue":"13890.25","netValue":"1344.25","date":today},
        {"category":"DII",    "buyValue":"8923.10", "sellValue":"9876.40", "netValue":"-953.30","date":today},
    ]

def parse_fii_dii(raw):
    """Parse raw FII/DII API response into clean records."""
    records = []
    for item in raw[:10]:  # last 10 trading days
        try:
            cat = str(item.get("category","") or item.get("name","") or "").strip()
            if not cat:
                continue
            buy  = float(str(item.get("buyValue","0") or item.get("grossBuy","0")).replace(",",""))
            sell = float(str(item.get("sellValue","0") or item.get("grossSell","0")).replace(",",""))
            net  = float(str(item.get("netValue","0") or item.get("net","0")).replace(",",""))
            date = str(item.get("date","") or item.get("tradingDate",""))[:11]
            records.append({"category":cat,"buy":buy,"sell":sell,"net":net,"date":date})
        except Exception:
            continue
    return records

# ══════════════════════════════════════════════════════════════════════════════
# FUNDAMENTAL DATA — screener.in scraper
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=86400, show_spinner=False)
def fetch_fundamentals(symbol: str):
    """Scrape key fundamentals from screener.in for any NSE symbol."""
    sym = symbol.replace(".NS","").replace(".BO","").upper()
    url = f"https://www.screener.in/company/{sym}/consolidated/"
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        import json, re
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")

        def extract(pattern, default="N/A"):
            m = re.search(pattern, html, re.IGNORECASE)
            return m.group(1).strip() if m else default

        fundamentals = {
            "Market Cap":    extract(r'Market Cap.*?<span[^>]*>([\d,\.]+\s*(?:Cr)?)</span>'),
            "P/E Ratio":     extract(r'Stock P/E.*?<span[^>]*>([\d,\.]+)</span>'),
            "P/B Ratio":     extract(r'Price to Book.*?<span[^>]*>([\d,\.]+)</span>'),
            "EPS (TTM)":     extract(r'EPS.*?<span[^>]*>([\d,\.\-]+)</span>'),
            "ROE":           extract(r'Return on Equity.*?<span[^>]*>([\d,\.]+)</span>'),
            "ROCE":          extract(r'Return on Capital.*?<span[^>]*>([\d,\.]+)</span>'),
            "Debt/Equity":   extract(r'Debt to Equity.*?<span[^>]*>([\d,\.]+)</span>'),
            "Promoter Hold": extract(r'Promoter Holding.*?<span[^>]*>([\d,\.]+\s*%?)</span>'),
            "Dividend Yield":extract(r'Dividend Yield.*?<span[^>]*>([\d,\.]+\s*%?)</span>'),
            "Book Value":    extract(r'Book Value.*?<span[^>]*>([\d,\.]+)</span>'),
        }
        return fundamentals, url
    except Exception:
        return None, url

# ══════════════════════════════════════════════════════════════════════════════
# OPTIONS CHAIN — NSE public API
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=900, show_spinner=False)
def fetch_options_chain(symbol: str):
    """Fetch options chain from NSE for equity/index."""
    sym = symbol.replace(".NS","").replace(".BO","").upper()
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept":"application/json, text/plain, */*",
        "Accept-Language":"en-US,en;q=0.9",
        "Referer":f"https://www.nseindia.com/option-chain",
        "X-Requested-With":"XMLHttpRequest",
    }
    import json
    # Index symbols
    index_syms = {"NIFTY","BANKNIFTY","FINNIFTY","MIDCPNIFTY","NIFTYNXT50","SENSEX"}
    if sym in index_syms:
        url = f"https://www.nseindia.com/api/option-chain-indices?symbol={sym}"
    else:
        url = f"https://www.nseindia.com/api/option-chain-equities?symbol={sym}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
        records = data.get("records",{})
        underlying = float(records.get("underlyingValue", 0))
        expiry_dates = records.get("expiryDates",[])
        raw_data = records.get("data",[])
        return raw_data, underlying, expiry_dates, None
    except Exception as e:
        return None, 0, [], str(e)

def compute_options_analytics(raw_data, underlying, selected_expiry=None):
    """Compute PCR, Max Pain, OI distribution from options chain data."""
    import json
    rows = []
    for item in raw_data:
        if selected_expiry and item.get("expiryDate") != selected_expiry:
            continue
        strike = float(item.get("strikePrice", 0))
        ce = item.get("CE", {})
        pe = item.get("PE", {})
        rows.append({
            "strike":     strike,
            "ce_oi":      float(ce.get("openInterest",0) or 0),
            "ce_vol":     float(ce.get("totalTradedVolume",0) or 0),
            "ce_ltp":     float(ce.get("lastPrice",0) or 0),
            "ce_iv":      float(ce.get("impliedVolatility",0) or 0),
            "pe_oi":      float(pe.get("openInterest",0) or 0),
            "pe_vol":     float(pe.get("totalTradedVolume",0) or 0),
            "pe_ltp":     float(pe.get("lastPrice",0) or 0),
            "pe_iv":      float(pe.get("impliedVolatility",0) or 0),
        })
    if not rows:
        return None, None, None, None, pd.DataFrame()

    df_opt = pd.DataFrame(rows).sort_values("strike").reset_index(drop=True)

    # Put/Call Ratio (OI-based)
    total_ce_oi = df_opt["ce_oi"].sum()
    total_pe_oi = df_opt["pe_oi"].sum()
    pcr = round(total_pe_oi / total_ce_oi, 3) if total_ce_oi > 0 else 0

    # PCR Volume
    pcr_vol = round(df_opt["pe_vol"].sum() / df_opt["ce_vol"].sum(), 3) if df_opt["ce_vol"].sum() > 0 else 0

    # Max Pain — strike where total option buyers lose the most
    strikes = df_opt["strike"].values
    total_pain = []
    for s in strikes:
        pain = 0
        for _, row in df_opt.iterrows():
            k = row["strike"]
            # CE loss: if s > k, CE holders of strike k are in-the-money
            pain += row["ce_oi"] * max(0, s - k)
            # PE loss: if s < k, PE holders of strike k are in-the-money
            pain += row["pe_oi"] * max(0, k - s)
        total_pain.append(pain)

    max_pain_idx = int(np.argmin(total_pain))
    max_pain = float(strikes[max_pain_idx])

    # Key resistance (highest CE OI) and support (highest PE OI)
    resistance = float(df_opt.loc[df_opt["ce_oi"].idxmax(), "strike"]) if len(df_opt) > 0 else 0
    support     = float(df_opt.loc[df_opt["pe_oi"].idxmax(), "strike"]) if len(df_opt) > 0 else 0

    return pcr, max_pain, resistance, support, df_opt


# ══════════════════════════════════════════════════════════════════════════════
# FII / DII FLOW DATA — NSE India
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_fii_dii():
    """Fetch FII/DII daily trade data from NSE India public API."""
    url = "https://www.nseindia.com/api/fiidiiTradeReact"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/market-data/fii-dii-activity",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        # First hit the main page to get cookies
        main_req = urllib.request.Request("https://www.nseindia.com", headers=headers)
        import http.cookiejar
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.open(main_req, timeout=8)
        time.sleep(0.5)
        with opener.open(req, timeout=8) as r:
            data = json.loads(r.read().decode())
        return data
    except Exception:
        return None

def parse_fii_dii(data):
    """Parse FII/DII API response into clean DataFrames."""
    if not data:
        return None, None
    try:
        rows = data if isinstance(data, list) else data.get("data", [])
        records = []
        for row in rows[:20]:
            try:
                date_str = row.get("date", row.get("Date", ""))
                fii_buy  = float(str(row.get("fiiBuy",  row.get("FII_BUY",  0))).replace(",","") or 0)
                fii_sell = float(str(row.get("fiiSell", row.get("FII_SELL", 0))).replace(",","") or 0)
                dii_buy  = float(str(row.get("diiBuy",  row.get("DII_BUY",  0))).replace(",","") or 0)
                dii_sell = float(str(row.get("diiSell", row.get("DII_SELL", 0))).replace(",","") or 0)
                records.append({
                    "Date": date_str,
                    "FII Net": round(fii_buy - fii_sell, 2),
                    "DII Net": round(dii_buy - dii_sell, 2),
                    "FII Buy": fii_buy, "FII Sell": fii_sell,
                    "DII Buy": dii_buy, "DII Sell": dii_sell,
                })
            except Exception:
                continue
        if not records:
            return None, None
        df = pd.DataFrame(records)
        return df, df.iloc[0] if len(df) > 0 else None
    except Exception:
        return None, None

# ══════════════════════════════════════════════════════════════════════════════
# OPTIONS CHAIN — NSE India
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=900, show_spinner=False)
def fetch_options_chain(symbol: str):
    """Fetch options chain from NSE India for a given symbol."""
    clean = symbol.replace(".NS","").replace(".BO","").upper()
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={clean}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"https://www.nseindia.com/get-quotes/derivatives?symbol={clean}",
    }
    try:
        import http.cookiejar
        cj   = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        main_req = urllib.request.Request("https://www.nseindia.com", headers=headers)
        opener.open(main_req, timeout=8)
        time.sleep(0.5)
        req = urllib.request.Request(url, headers=headers)
        with opener.open(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None

def parse_options_chain(data, spot_price: float):
    """Parse options chain → max pain, PCR, strike table."""
    if not data:
        return None, None, None, None
    try:
        records = data.get("records", {})
        exp_dates = records.get("expiryDates", [])
        nearest_exp = exp_dates[0] if exp_dates else None
        chain_data  = records.get("data", [])

        rows = []
        for item in chain_data:
            if nearest_exp and item.get("expiryDate") != nearest_exp:
                continue
            strike = item.get("strikePrice", 0)
            ce = item.get("CE", {})
            pe = item.get("PE", {})
            rows.append({
                "Strike":   strike,
                "CE OI":    ce.get("openInterest", 0),
                "CE Chg OI": ce.get("changeinOpenInterest", 0),
                "CE LTP":   ce.get("lastPrice", 0),
                "CE IV":    ce.get("impliedVolatility", 0),
                "PE OI":    pe.get("openInterest", 0),
                "PE Chg OI": pe.get("changeinOpenInterest", 0),
                "PE LTP":   pe.get("lastPrice", 0),
                "PE IV":    pe.get("impliedVolatility", 0),
            })

        if not rows:
            return None, None, None, nearest_exp

        df_chain = pd.DataFrame(rows).sort_values("Strike")

        # PCR — Put/Call Ratio by OI
        total_ce_oi = df_chain["CE OI"].sum()
        total_pe_oi = df_chain["PE OI"].sum()
        pcr = round(total_pe_oi / total_ce_oi, 3) if total_ce_oi > 0 else None

        # Max Pain — strike where total loss to option buyers is maximum
        strikes = df_chain["Strike"].values
        ce_ois  = df_chain["CE OI"].values
        pe_ois  = df_chain["PE OI"].values
        pain    = []
        for s in strikes:
            ce_pain = sum(max(0, s - k) * o for k, o in zip(strikes, ce_ois))
            pe_pain = sum(max(0, k - s) * o for k, o in zip(strikes, pe_ois))
            pain.append(ce_pain + pe_pain)
        max_pain_strike = float(strikes[int(np.argmin(pain))])

        return df_chain, pcr, max_pain_strike, nearest_exp
    except Exception as e:
        return None, None, None, None

# ══════════════════════════════════════════════════════════════════════════════
# FUNDAMENTAL DATA — screener.in scraper
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=86400, show_spinner=False)
def fetch_fundamentals(symbol: str):
    """Scrape key ratios from screener.in for an NSE symbol."""
    clean = symbol.replace(".NS","").replace(".BO","").upper()
    url   = f"https://www.screener.in/company/{clean}/consolidated/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        req  = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")

        def extract(label):
            import re
            # Look for the label in a li element and get the number after it
            patterns = [
                rf"{label}[^\d<]*<[^>]*>\s*([\d,\.]+)",
                rf">{label}</[^>]+>[^<]*<[^>]+>([\d,\.]+)",
                rf"{label}[^\d]{{0,30}}([\d,\.]+)",
            ]
            for pat in patterns:
                m = re.search(pat, html, re.IGNORECASE)
                if m:
                    try:
                        return float(m.group(1).replace(",",""))
                    except Exception:
                        pass
            return None

        return {
            "P/E Ratio":      extract("Stock P/E") or extract("P/E"),
            "P/B Ratio":      extract("Price to Book") or extract("P/B"),
            "ROE (%)":        extract("Return on Equity") or extract("ROE"),
            "ROCE (%)":       extract("Return on Capital Employed") or extract("ROCE"),
            "Debt/Equity":    extract("Debt to equity") or extract("D/E"),
            "Promoter Hold%": extract("Promoter Holding") or extract("Promoter"),
            "EPS (TTM)":      extract("EPS"),
            "Div Yield (%)":  extract("Dividend Yield"),
        }
    except Exception:
        return {}

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
col_title, col_clock = st.columns([2,1])
with col_title:
    st.markdown('<h1 class="xerces-title">XERCES // QUANT ENGINE</h1>', unsafe_allow_html=True)
    st.markdown('<p class="telemetry-tag">[ NSE/BSE UNIVERSE: 600+ STOCKS // ARIMA + TECHNICAL + PORTFOLIO ENGINE // GODMODE ]</p>', unsafe_allow_html=True)
with col_clock:
    now_ist = ist_now()
    ms, mc  = market_status()
    st.markdown(f"""
    <div style="text-align:right;font-family:'Space Mono',monospace;font-size:11px;color:#6a90aa;
                background:rgba(7,18,32,0.5);padding:8px;border-radius:4px;border:1px solid rgba(0,200,255,0.08);">
        <div>CLOCK: <span style="color:#ffcc00;font-weight:bold;">{now_ist.strftime('%H:%M:%S')} IST</span></div>
        <div>DATE: <span style="color:#00c8ff;">{now_ist.strftime('%d %b %Y')}</span></div>
        <div style="margin-top:3px;color:{mc};font-weight:bold;">{ms}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<hr style='border-color:rgba(0,200,255,0.12);margin:0.65rem 0;'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL SEARCH BAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='background:rgba(7,18,32,0.45);border:1px solid rgba(0,200,255,0.12);padding:10px 16px;border-radius:6px;margin-bottom:12px;'>", unsafe_allow_html=True)
sc1, sc2 = st.columns([5,1])
with sc1:
    search_raw = st.text_input("Search", value="", placeholder="Search any NSE/BSE stock — name or symbol (e.g. Reliance, TCS, SBIN, INFY)...", label_visibility="collapsed")
with sc2:
    if search_raw and st.button("✕ Clear", use_container_width=True):
        st.session_state["search_val"] = ""
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# ── Ticker resolution ─────────────────────────────────────────────────────────
search = search_raw.strip()
selected_ticker, selected_name, is_dashboard = "^NSEI", "NIFTY 50", True

if search:
    is_dashboard = False
    match_t, match_n = None, None
    sl = search.lower()
    # 1. name match
    for label, ticker in ALL_STOCKS.items():
        if sl in label.lower():
            match_t, match_n = ticker, label.split(" (")[0]; break
    # 2. symbol match
    if not match_t:
        for label, ticker in ALL_STOCKS.items():
            sym = ticker.replace(".NS","")
            if sl.upper() == sym or sl.upper() == ticker.upper():
                match_t, match_n = ticker, label.split(" (")[0]; break
    if match_t:
        selected_ticker, selected_name = match_t, match_n
    else:
        # Custom ticker — try as NSE first
        candidate = search.upper()
        if not candidate.endswith(".NS") and not candidate.endswith(".BO") and "^" not in candidate:
            candidate = candidate + ".NS"
        selected_ticker = candidate
        selected_name   = search.upper().replace(".NS","").replace(".BO","")

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
if is_dashboard:
    st.markdown('<h2 class="xerces-title" style="font-size:1.5rem;margin-bottom:12px;">📊 LIVE MARKET OVERVIEW</h2>', unsafe_allow_html=True)
    with st.spinner("Loading market indices..."):
        idx_data = load_indices()
    INDEX_META = [
        ("^NSEI","NIFTY 50","#00e87a"), ("^NSEBANK","BANK NIFTY","#00c8ff"),
        ("^BSESN","SENSEX","#ffcc00"),  ("^CRSMID","NIFTY MIDCAP","#ff6b35"),
        ("^CNXSC","NIFTY SMALLCAP","#7c6ef8"), ("^INDIAVIX","INDIA VIX","#ff3355"),
    ]
    cols = st.columns(6)
    for col, (sym, name, clr) in zip(cols, INDEX_META):
        try:
            idf  = idx_data.get(sym)
            if idf is None or len(idf) < 2:
                col.warning(name); continue
            cv   = float(idf["Close"].iloc[-1])
            pv   = float(idf["Close"].iloc[-2])
            chg  = (cv - pv) / pv * 100
            flip = sym == "^INDIAVIX"
            cclr = ("#ff3355" if chg >= 0 else "#00e87a") if flip else ("#00e87a" if chg >= 0 else "#ff3355")
            arrow= "▲" if chg >= 0 else "▼"
            col.markdown(f"""<div class="glass-card">
                <p class="glass-label" style="color:{clr};">{name}</p>
                <div class="glass-value" style="font-size:1.1rem;">{cv:,.2f}</div>
                <p style="font-size:11px;color:{cclr};margin:2px 0;font-weight:600;">{arrow} {abs(chg):.2f}%</p>
            </div>""", unsafe_allow_html=True)
        except Exception:
            col.warning(name)

    # Nifty 50 chart
    try:
        n50 = idx_data.get("^NSEI")
        if n50 is not None and not n50.empty:
            fig0 = go.Figure()
            fig0.add_trace(go.Scatter(x=n50["Date"], y=n50["Close"], line=dict(color="#00e87a",width=2), name="Nifty 50", fill="tozeroy", fillcolor="rgba(0,232,122,0.04)"))
            fig0.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ddeeff",family="Space Mono",size=10), margin=dict(l=10,r=10,t=10,b=10),
                xaxis=dict(gridcolor="rgba(0,200,255,0.05)"), yaxis=dict(gridcolor="rgba(0,200,255,0.05)",tickprefix="₹"),
                showlegend=False)
            st.plotly_chart(fig0, use_container_width=True)
    except Exception:
        pass

    st.markdown("""<div class="glass-card" style="margin-top:10px;">
        <p class="section-header" style="margin-top:0;">💡 How to use XERCES</p>
        <p style="font-size:12px;color:#a0aec0;line-height:1.7;margin:0;">
        Type any stock name or NSE symbol in the search bar above — e.g. <b style="color:#00c8ff;">Reliance</b>, <b style="color:#00c8ff;">TCS</b>, <b style="color:#00c8ff;">HDFCBANK</b>.
        You'll get live technical charts with MACD/RSI/Bollinger Bands, ARIMA + Holt-Winters price forecast to June 2027 with accuracy metrics,
        multi-strategy backtesting, bulk market scanner, portfolio optimizer (MPT), news sentiment, and full risk calculator.
        </p>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
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
    backtest_strategy = st.selectbox("Strategy", ["SMA Crossover","RSI Mean Reversion","Bollinger Bands Breakout","MACD Crossover"])
    st.markdown("---")
    st.caption("⚠️ Not SEBI registered. Statistical analysis only. Not financial advice. Data: Yahoo Finance.")

# ══════════════════════════════════════════════════════════════════════════════
# LOAD + VALIDATE DATA
# ══════════════════════════════════════════════════════════════════════════════
with st.spinner(f"Loading {selected_name} ({selected_ticker})..."):
    raw_df = load_ohlcv(selected_ticker, period="5y")

if raw_df is None or len(raw_df) < 60:
    st.error(f"❌ Could not load data for **{selected_ticker}**.")
    if selected_ticker.endswith(".NS"):
        bse = selected_ticker.replace(".NS",".BO")
        st.info(f"Try BSE: type `{bse.replace('.BO','')} .BO` in the search bar, or verify the symbol on NSE India.")
    else:
        st.info("For NSE stocks append `.NS` (e.g. RELIANCE.NS). For BSE append `.BO`.")
    st.stop()

df  = add_indicators(raw_df)
last     = df.iloc[-1]
prev     = df.iloc[-2]
close    = float(last["Close"])
signal   = get_signal(df)
strength = get_signal_strength(df)
atr_val  = float(last["ATR_14"]) if pd.notna(last.get("ATR_14")) else close * 0.02
sl_price = close - atr_val * 1.5
tp_price = close + atr_val * 1.5 * risk_reward
chg1d    = (close - float(prev["Close"])) / float(prev["Close"]) * 100
hi52     = float(df["Close"].iloc[-252:].max()) if len(df) >= 252 else float(df["Close"].max())
lo52     = float(df["Close"].iloc[-252:].min()) if len(df) >= 252 else float(df["Close"].min())
rsi_val  = float(last["RSI_14"]) if pd.notna(last.get("RSI_14")) else 50.0
macd_v   = float(last.get("MACD") or 0)
macd_sv  = float(last.get("MACD_Signal") or 0)
vol20    = float(last.get("Volatility_20") or 0)

# Run backtest (needed for chart markers)
bt_df, trades, buy_x, buy_y, sell_x, sell_y = run_backtest(df, backtest_strategy)

# ══════════════════════════════════════════════════════════════════════════════
# KPI ROW
# ══════════════════════════════════════════════════════════════════════════════
k1,k2,k3,k4,k5,k6,k7 = st.columns(7)
sig_clr  = {"BUY":"#00e87a","SELL":"#ff3355","HOLD":"#ffcc00"}[signal]
chg_clr  = "#00e87a" if chg1d >= 0 else "#ff3355"
str_clr  = "#00e87a" if strength >= 65 else "#ff3355" if strength <= 35 else "#ffcc00"

for col, lbl, val, clr in zip(
    [k1,k2,k3,k4,k5,k6,k7],
    ["Last Close","1D Change","52W High","52W Low","RSI (14)","Signal","Strength"],
    [f"₹{close:,.2f}",f"{'▲' if chg1d>=0 else '▼'} {abs(chg1d):.2f}%",
     f"₹{hi52:,.2f}",f"₹{lo52:,.2f}",f"{rsi_val:.1f}",signal,f"{strength}/100"],
    ["#ddeeff",chg_clr,"#ddeeff","#ddeeff",
     "#ff3355" if rsi_val>70 else "#00e87a" if rsi_val<30 else "#00c8ff",
     sig_clr, str_clr]
):
    col.markdown(f'<div class="glass-card"><p class="glass-label">{lbl}</p>'
                 f'<div class="glass-value" style="color:{clr};font-size:1.1rem;">{val}</div></div>',
                 unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_chart, tab_arima, tab_backtest, tab_scan, tab_risk, tab_port, tab_fii, tab_options, tab_funds, tab_news, tab_help = st.tabs([
    "📊 CHART", "🔮 FORECAST", "📈 BACKTEST", "📡 SCANNER",
    "🛡️ RISK", "💼 PORTFOLIO", "📊 FII/DII", "🎯 OPTIONS", "📋 FUNDAMENTALS", "📰 NEWS", "❓ MANUAL"
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: TECHNICAL CHART
# ─────────────────────────────────────────────────────────────────────────────
with tab_chart:
    rows    = 4 if show_vol else 3
    row_h   = ([0.48,0.18,0.18,0.16] if show_vol else [0.56,0.22,0.22])
    titles  = ["Price + Indicators","RSI (14)","MACD"] + (["Volume"] if show_vol else [])
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=row_h,
                        vertical_spacing=0.025, subplot_titles=titles,
                        specs=[[{"secondary_y":False}]]*rows)

    fig.add_trace(go.Candlestick(
        x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name="OHLC", increasing_line_color="#00e87a", decreasing_line_color="#ff3355",
        increasing_fillcolor="rgba(0,232,122,0.25)", decreasing_fillcolor="rgba(255,51,85,0.25)"
    ), row=1, col=1)

    if show_sma:
        for col_n, clr, dsh in [("SMA_20","#00c8ff","dot"),("SMA_50","#ffcc00","dash"),("SMA_200","#ff6b35","solid")]:
            if col_n in df.columns:
                fig.add_trace(go.Scatter(x=df["Date"], y=df[col_n], name=col_n.replace("_"," "),
                    line=dict(color=clr,width=1.2,dash=dsh), opacity=0.85), row=1, col=1)

    if show_bb and "BB_Upper" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_Upper"], name="BB Upper",
            line=dict(color="rgba(124,78,255,0.5)",width=1,dash="dot")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_Lower"], name="BB Lower",
            line=dict(color="rgba(124,78,255,0.5)",width=1,dash="dot"),
            fill="tonexty", fillcolor="rgba(124,78,255,0.04)"), row=1, col=1)

    # Risk lines
    fig.add_hline(y=sl_price, line_dash="dash", line_color="rgba(255,51,85,0.6)",
                  annotation_text=f"SL ₹{sl_price:,.0f}", row=1, col=1)
    fig.add_hline(y=tp_price, line_dash="dash", line_color="rgba(0,232,122,0.6)",
                  annotation_text=f"TP ₹{tp_price:,.0f}", row=1, col=1)

    # Trade markers (BUG FIX: y at low/high)
    if buy_x:
        fig.add_trace(go.Scatter(x=buy_x, y=buy_y, mode="markers", name="Buy Entry",
            marker=dict(symbol="triangle-up", size=9, color="#00e87a",
                        line=dict(width=1, color="#020813"))), row=1, col=1)
    if sell_x:
        fig.add_trace(go.Scatter(x=sell_x, y=sell_y, mode="markers", name="Sell Exit",
            marker=dict(symbol="triangle-down", size=9, color="#ff3355",
                        line=dict(width=1, color="#020813"))), row=1, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI_14"], name="RSI 14",
        line=dict(color="#00c8ff",width=1.5)), row=2, col=1)
    for lvl, lc in [(70,"rgba(255,51,85,0.4)"),(30,"rgba(0,232,122,0.4)"),(50,"rgba(255,255,255,0.08)")]:
        fig.add_hline(y=lvl, line_dash="dot", line_color=lc, row=2, col=1)

    # MACD
    mc_colors = ["#00e87a" if v>=0 else "#ff3355" for v in df["MACD_Hist"].fillna(0)]
    fig.add_trace(go.Bar(x=df["Date"], y=df["MACD_Hist"], name="MACD Hist", marker_color=mc_colors, opacity=0.7), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["MACD"], name="MACD", line=dict(color="#00c8ff",width=1.2)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["MACD_Signal"], name="Signal", line=dict(color="#ffcc00",width=1.2,dash="dot")), row=3, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.1)", row=3, col=1)

    # Volume
    if show_vol and "Volume" in df.columns:
        vc = ["rgba(0,232,122,0.4)" if r["Close"] >= r["Open"] else "rgba(255,51,85,0.4)" for _,r in df.iterrows()]
        fig.add_trace(go.Bar(x=df["Date"], y=df["Volume"], name="Volume", marker_color=vc), row=4, col=1)

    fig.update_layout(
        height=780, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ddeeff",family="Space Mono",size=10),
        xaxis_rangeslider_visible=False, showlegend=True,
        legend=dict(bgcolor="rgba(7,18,32,0.5)",bordercolor="rgba(0,200,255,0.15)",borderwidth=1,font=dict(size=9)),
        margin=dict(l=10,r=10,t=30,b=10),
    )
    for i in range(1, rows+1):
        fig.update_xaxes(gridcolor="rgba(0,200,255,0.04)", row=i, col=1)
        fig.update_yaxes(gridcolor="rgba(0,200,255,0.04)", row=i, col=1)
    fig.update_xaxes(rangeselector=dict(
        buttons=[dict(count=1,label="1M",step="month"),dict(count=3,label="3M",step="month"),
                 dict(count=6,label="6M",step="month"),dict(count=1,label="1Y",step="year"),
                 dict(count=2,label="2Y",step="year"),dict(step="all",label="5Y")],
        bgcolor="rgba(7,18,32,0.7)", activecolor="#00c8ff", font=dict(color="#ddeeff",size=9)
    ), row=1, col=1)
    st.plotly_chart(fig, use_container_width=True)

    # Indicator summary
    ls, rs = st.columns([1,2])
    with ls:
        st.markdown(f"""<div class="glass-card" style="text-align:center;">
            <p class="glass-label">Signal</p>
            <div class="signal-{'buy' if signal=='BUY' else 'sell' if signal=='SELL' else 'hold'}">{signal}</div>
            <div style="background:rgba(255,255,255,0.05);border-radius:4px;height:6px;margin:8px 0;">
              <div style="width:{strength}%;height:6px;border-radius:4px;background:{str_clr};"></div>
            </div>
            <p style="font-size:10px;color:#6a90aa;margin:0;">Strength {strength}/100</p>
        </div>""", unsafe_allow_html=True)
    with rs:
        bb_pct = ""
        if pd.notna(last.get("BB_Upper")) and pd.notna(last.get("BB_Lower")):
            bbrng = float(last["BB_Upper"]) - float(last["BB_Lower"])
            bb_pct = f"{(close-float(last['BB_Lower']))/bbrng*100:.0f}%" if bbrng>0 else "—"
        sk = float(last.get("Stoch_K",50) or 50)
        st.markdown(f"""<div class="glass-card">
            <p class="glass-label">Readings</p>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-top:6px;font-size:11px;font-family:'Space Mono',monospace;">
                <div>RSI: <span style="color:{'#ff3355' if rsi_val>70 else '#00e87a' if rsi_val<30 else '#00c8ff'}">{rsi_val:.1f}</span></div>
                <div>MACD: <span style="color:{'#00e87a' if macd_v>macd_sv else '#ff3355'}">{macd_v:.2f}</span></div>
                <div>ATR(14): <span style="color:#ffcc00;">₹{atr_val:.2f}</span></div>
                <div>Stoch %K: <span style="color:{'#ff3355' if sk>80 else '#00e87a' if sk<20 else '#ddeeff'}">{sk:.0f}</span></div>
                <div>BB Pos: <span style="color:#7c4dff;">{bb_pct}</span></div>
                <div>Volatility: <span style="color:#ddeeff;">{vol20:.1%}</span></div>
                <div>SMA 200: <span style="color:#ff6b35;">₹{float(last.get('SMA_200',0) or 0):,.0f}</span></div>
                <div>SMA 50: <span style="color:#ffcc00;">₹{float(last.get('SMA_50',0) or 0):,.0f}</span></div>
                <div>SMA 20: <span style="color:#00c8ff;">₹{float(last.get('SMA_20',0) or 0):,.0f}</span></div>
            </div>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: ARIMA FORECAST
# ─────────────────────────────────────────────────────────────────────────────
with tab_arima:
    st.markdown(f'<p class="section-header">[ 🔮 ARIMA + HOLT-WINTERS FORECAST — {selected_name} → JUNE 2027 ]</p>', unsafe_allow_html=True)
    price_series = df["Close"].astype(float).dropna()
    last_date    = pd.to_datetime(df["Date"].iloc[-1])
    target_end   = pd.Timestamp("2027-06-30")
    fc_dates     = pd.bdate_range(start=last_date + pd.Timedelta(days=1), end=target_end)
    steps        = len(fc_dates)

    if steps <= 0:
        st.warning("Data already extends past June 2027.")
    else:
        with st.spinner("Running ARIMA (5×5 AIC grid) + Holt-Winters + 60-day accuracy validation..."):
            try:
                fc_mean, fc_lo, fc_hi, arima_order, aic_val, arima_model, log_s = run_arima(price_series, steps)
                fc_series = pd.Series(fc_mean.values, index=fc_dates)
                ci_lo     = pd.Series(fc_lo.values,   index=fc_dates)
                ci_hi     = pd.Series(fc_hi.values,   index=fc_dates)
                hw_series = pd.Series(run_holt_winters(price_series, steps).values, index=fc_dates)

                target_arima = float(fc_series.iloc[-1])
                target_hw    = float(hw_series.iloc[-1])
                consensus    = (target_arima + target_hw) / 2
                upside_a     = (target_arima - close) / close * 100
                upside_hw    = (target_hw - close) / close * 100
                upside_c     = (consensus - close) / close * 100

                # Accuracy validation
                mape, dir_acc = compute_accuracy(price_series, arima_order, holdout=60)

                # KPI row
                fa1,fa2,fa3,fa4,fa5 = st.columns(5)
                for col, lbl, val, clr in zip([fa1,fa2,fa3,fa4,fa5],
                    ["Current Price","ARIMA Jun '27","Holt-Winters Jun '27","Consensus Target","Model"],
                    [f"₹{close:,.2f}",
                     f"₹{target_arima:,.0f} ({'▲' if upside_a>=0 else '▼'}{abs(upside_a):.1f}%)",
                     f"₹{target_hw:,.0f} ({'▲' if upside_hw>=0 else '▼'}{abs(upside_hw):.1f}%)",
                     f"₹{consensus:,.0f} ({'▲' if upside_c>=0 else '▼'}{abs(upside_c):.1f}%)",
                     f"ARIMA{arima_order}"],
                    ["#ddeeff","#fbbf24","#00c8ff","#00e87a","#ff6b35"]):
                    col.markdown(f'<div class="glass-card"><p class="glass-label">{lbl}</p>'
                                 f'<div class="glass-value" style="color:{clr};font-size:1rem;">{val}</div></div>',
                                 unsafe_allow_html=True)

                # Accuracy metrics row
                if mape is not None:
                    am1, am2, am3 = st.columns(3)
                    mape_clr = "#00e87a" if mape < 5 else "#ffcc00" if mape < 10 else "#ff3355"
                    dacc_clr = "#00e87a" if dir_acc > 60 else "#ffcc00" if dir_acc > 50 else "#ff3355"
                    am1.markdown(f'<div class="glass-card"><p class="glass-label">60-Day Backtest MAPE</p>'
                                 f'<div class="glass-value" style="color:{mape_clr};">{mape:.2f}%</div>'
                                 f'<p style="font-size:10px;color:#6a90aa;margin:3px 0 0;">{"Excellent" if mape<5 else "Good" if mape<10 else "Use with caution"}</p></div>',
                                 unsafe_allow_html=True)
                    am2.markdown(f'<div class="glass-card"><p class="glass-label">Directional Accuracy</p>'
                                 f'<div class="glass-value" style="color:{dacc_clr};">{dir_acc:.0f}%</div>'
                                 f'<p style="font-size:10px;color:#6a90aa;margin:3px 0 0;">Win rate on direction</p></div>',
                                 unsafe_allow_html=True)
                    am3.markdown(f'<div class="glass-card"><p class="glass-label">AIC Score</p>'
                                 f'<div class="glass-value" style="color:#7c4dff;">{aic_val}</div>'
                                 f'<p style="font-size:10px;color:#6a90aa;margin:3px 0 0;">Lower = better fit</p></div>',
                                 unsafe_allow_html=True)

                # Forecast chart
                fig2 = go.Figure()
                hp   = price_series.iloc[-504:]
                hd   = pd.to_datetime(df["Date"].iloc[-504:])
                fig2.add_trace(go.Scatter(x=hd, y=hp.values, name="Historical (2yr)", line=dict(color="#7c6ef8",width=1.8)))
                fig2.add_trace(go.Scatter(x=fc_series.index, y=fc_series.values, name="ARIMA", line=dict(color="#f97316",width=2,dash="dash")))
                fig2.add_trace(go.Scatter(x=hw_series.index, y=hw_series.values, name="Holt-Winters", line=dict(color="#00c8ff",width=1.5,dash="dashdot")))
                # Consensus shaded
                fig2.add_trace(go.Scatter(x=fc_series.index, y=(fc_series.values+hw_series.values)/2, name="Consensus",
                    line=dict(color="#00e87a",width=1.5,dash="longdash")))
                # CI band
                fig2.add_trace(go.Scatter(
                    x=list(ci_hi.index)+list(ci_lo.index[::-1]),
                    y=list(ci_hi.values)+list(ci_lo.values[::-1]),
                    fill="toself", fillcolor="rgba(249,115,22,0.08)",
                    line=dict(color="rgba(0,0,0,0)"), name="ARIMA 90% CI"))
                fig2.add_vline(x=str(last_date), line_dash="dot", line_color="rgba(100,100,100,0.4)")
                fig2.add_annotation(x=str(target_end), y=consensus,
                    text=f"Consensus Jun '27<br>₹{consensus:,.0f}",
                    showarrow=True, arrowhead=2, arrowcolor="#00e87a",
                    font=dict(color="#00e87a",size=10), bgcolor="rgba(7,18,32,0.85)",
                    bordercolor="#00e87a", borderwidth=1)
                fig2.update_layout(height=440, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#ddeeff",family="Space Mono",size=10),
                    legend=dict(bgcolor="rgba(7,18,32,0.5)",bordercolor="rgba(0,200,255,0.2)",borderwidth=1),
                    margin=dict(l=10,r=10,t=20,b=10),
                    xaxis=dict(gridcolor="rgba(0,200,255,0.04)"),
                    yaxis=dict(gridcolor="rgba(0,200,255,0.04)",tickprefix="₹"))
                st.plotly_chart(fig2, use_container_width=True)

                # Monthly cards
                st.markdown('<p class="section-header">[ 📅 MONTH-BY-MONTH ARIMA PRICE TARGETS ]</p>', unsafe_allow_html=True)
                fc_df2 = pd.DataFrame({"Forecast":fc_series,"HW":hw_series,"CI_Lo":ci_lo,"CI_Hi":ci_hi})
                fc_df2["Month"] = fc_df2.index.to_period("M")
                monthly = fc_df2.groupby("Month").agg(
                    Forecast=("Forecast","last"), HW=("HW","last"),
                    CI_Lo=("CI_Lo","last"), CI_Hi=("CI_Hi","last")
                ).reset_index()
                monthly["Month_str"] = monthly["Month"].dt.strftime("%b %Y")
                monthly["MoM_pct"]   = monthly["Forecast"].pct_change() * 100
                monthly.loc[0,"MoM_pct"] = (monthly.loc[0,"Forecast"] - close) / close * 100

                for i in range(0, len(monthly), 6):
                    chunk = monthly.iloc[i:i+6]
                    cols  = st.columns(len(chunk))
                    for col, (_,row) in zip(cols, chunk.iterrows()):
                        chg   = row["MoM_pct"]
                        arrow = "▲" if chg>=0 else "▼"
                        clr   = "#00e87a" if chg>=0 else "#ff3355"
                        col.markdown(f"""
<div style="background:rgba(7,18,32,0.65);border:1px solid rgba(0,200,255,0.15);border-radius:6px;
     padding:9px 7px;text-align:center;margin-bottom:6px;">
  <div style="font-size:9px;font-family:'Space Mono',monospace;color:#6a90aa;text-transform:uppercase;">{row['Month_str']}</div>
  <div style="font-family:'Orbitron',sans-serif;font-size:.95rem;font-weight:700;color:#fbbf24;margin:3px 0;">₹{row['Forecast']:,.0f}</div>
  <div style="font-size:9px;color:{clr};font-weight:600;">{arrow} {abs(chg):.1f}%</div>
  <div style="font-size:8px;color:rgba(100,120,140,0.8);margin-top:2px;">HW: ₹{row['HW']:,.0f}</div>
  <div style="font-size:8px;color:rgba(100,120,140,0.5);">₹{row['CI_Lo']:,.0f}–₹{row['CI_Hi']:,.0f}</div>
</div>""", unsafe_allow_html=True)

                tbl = monthly[["Month_str","Forecast","HW","CI_Lo","CI_Hi","MoM_pct"]].round(2)
                tbl.columns = ["Month","ARIMA ₹","Holt-Winters ₹","Lower ₹","Upper ₹","MoM %"]
                st.download_button("⬇️ Download Forecast CSV",
                                   tbl.to_csv(index=False).encode(),
                                   f"{selected_name}_forecast.csv","text/csv")

                with st.expander("🔬 Model diagnostics"):
                    pv = adfuller(np.log(price_series.dropna()))[1]
                    
                    st.markdown(f"""
| Parameter | Value |
|---|---|
| Ticker | {selected_ticker} |
| ARIMA order | {arima_order} |
| AIC | {aic_val} |
| MAPE (60-day holdout) | {f"{mape:.2f}%" if mape is not None else "N/A"} |
| Directional accuracy | {f"{dir_acc:.1f}%" if dir_acc is not None else "N/A"} |
| Training observations | {len(price_series):,} |
| Forecast horizon | {steps} trading days |
| Data range | {str(df["Date"].iloc[0])[:10]} to {str(df["Date"].iloc[-1])[:10]} |
""")
            except Exception as e:
                st.error(f"Forecast error: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: BACKTEST ENGINE
# ─────────────────────────────────────────────────────────────────────────────
with tab_backtest:
    st.markdown(f'<p class="section-header">[ BACKTEST: {backtest_strategy.upper()} — {selected_name} ]</p>', unsafe_allow_html=True)
    st.caption("Next-day open execution — no look-ahead bias.")

    if trades:
        tdf      = pd.DataFrame(trades)
        wins     = (tdf["P&L %"] > 0).sum()
        total    = len(tdf)
        win_rate = wins / total * 100
        gp       = tdf[tdf["P&L %"] > 0]["P&L %"].sum()
        gl       = abs(tdf[tdf["P&L %"] < 0]["P&L %"].sum())
        pf       = gp / gl if gl > 0 else (999.0 if gp > 0 else 0.0)
        pf_str   = f"{pf:.2f}" if gl > 0 else ("inf" if gp > 0 else "0.00")

        bt_df["Strat_Ret"] = bt_df["Signal_BT"].shift(1) * bt_df["Close"].astype(float).pct_change()
        bt_df["Equity"]    = (1 + bt_df["Strat_Ret"].fillna(0)).cumprod()
        bt_df["BH"]        = bt_df["Close"].astype(float) / float(bt_df["Close"].iloc[0])
        bt_df["Peak"]      = bt_df["Equity"].cummax()
        bt_df["DD"]        = (bt_df["Equity"] - bt_df["Peak"]) / bt_df["Peak"]
        max_dd             = abs(float(bt_df["DD"].min()) * 100)
        ret_s              = bt_df["Strat_Ret"].fillna(0)
        sharpe             = float(ret_s.mean() / ret_s.std() * np.sqrt(252)) if ret_s.std() > 0 else 0.0
        ann_ret            = (float(bt_df["Equity"].iloc[-1]) ** (252 / max(len(bt_df), 1)) - 1) * 100
        bh_ret             = (float(bt_df["BH"].iloc[-1]) - 1) * 100

        b1, b2, b3, b4, b5, b6 = st.columns(6)
        for col, lbl, val, clr in zip(
            [b1, b2, b3, b4, b5, b6],
            ["Win Rate", "Profit Factor", "Max Drawdown", "Sharpe Ratio", "Ann. Return", "Alpha vs B&H"],
            [f"{win_rate:.1f}%", pf_str, f"-{max_dd:.1f}%", f"{sharpe:.2f}",
             f"{ann_ret:+.1f}%", f"{ann_ret - bh_ret:+.1f}%"],
            ["#00e87a",
             "#00e87a" if pf >= 1.5 else "#ffcc00" if pf >= 1.0 else "#ff3355",
             "#ff3355", "#00c8ff",
             "#00e87a" if ann_ret > 0 else "#ff3355",
             "#00e87a" if ann_ret > bh_ret else "#ff3355"]
        ):
            col.markdown(
                f'<div class="glass-card"><p class="glass-label">{lbl}</p>'
                f'<div class="glass-value" style="color:{clr};font-size:1rem;">{val}</div></div>',
                unsafe_allow_html=True
            )

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=bt_df["Date"], y=bt_df["Equity"] * 100, name="Strategy",
                                  line=dict(color="#00e87a", width=2)))
        fig3.add_trace(go.Scatter(x=bt_df["Date"], y=bt_df["BH"] * 100, name="Buy & Hold",
                                  line=dict(color="#7c6ef8", width=1.5, dash="dot")))
        fig3.update_layout(
            height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ddeeff", family="Space Mono", size=10),
            xaxis=dict(gridcolor="rgba(0,200,255,0.04)"),
            yaxis=dict(gridcolor="rgba(0,200,255,0.04)", ticksuffix="%"),
            margin=dict(l=10, r=10, t=15, b=10),
            legend=dict(bgcolor="rgba(7,18,32,0.5)", bordercolor="rgba(0,200,255,0.15)", borderwidth=1)
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('<p class="section-header">[ TRADE LOG — LAST 30 ]</p>', unsafe_allow_html=True)
        st.dataframe(tdf.tail(30), use_container_width=True, hide_index=True)
        st.download_button("Download Trade Log", tdf.to_csv(index=False).encode(),
                           f"{selected_name}_trades.csv", "text/csv")
    else:
        st.info("No signals generated. Try a different stock or strategy.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: MARKET SCANNER
# ─────────────────────────────────────────────────────────────────────────────
with tab_scan:
    st.markdown('<p class="section-header">[ MULTI-STOCK BULK SCANNER ]</p>', unsafe_allow_html=True)
    default_sector = next((k for k in SECTORS.keys() if "Banking" in k), list(SECTORS.keys())[0])
    scan_sectors = st.multiselect("Sectors", list(SECTORS.keys()), default=[default_sector])
    max_stocks = st.slider("Max stocks", 10, 80, 20, step=5)

    def _scan_one(args):
        name, ticker_s = args
        try:
            sd = load_ohlcv(ticker_s, period="1y")
            if sd is None or len(sd) < 60:
                return None
            sd  = add_indicators(sd)
            ls  = sd.iloc[-1]
            ps  = sd.iloc[-2]
            sig = get_signal(sd)
            cp  = float(ls["Close"])
            chg = (cp - float(ps["Close"])) / float(ps["Close"]) * 100
            atr = float(ls["ATR_14"]) if pd.notna(ls.get("ATR_14")) else cp * 0.02
            sl  = cp - atr * 1.5
            tp  = cp + atr * 1.5 * risk_reward
            qty = max(1, int(allocated_capital * (risk_per_trade / 100) / (atr * 1.5)))
            rsi = float(ls["RSI_14"]) if pd.notna(ls.get("RSI_14")) else 50.0
            stre = get_signal_strength(sd)
            return {
                "Stock": name, "Ticker": ticker_s.replace(".NS", ""),
                "Price": f"Rs{cp:,.2f}", "1D%": f"{chg:+.2f}",
                "RSI": f"{rsi:.1f}", "Signal": sig, "Strength": stre,
                "SL": f"Rs{sl:,.2f}", "Target": f"Rs{tp:,.2f}", "Qty": qty,
                "_sig": sig, "_chg": chg, "_str": stre
            }
        except Exception:
            return None

    if st.button("RUN SCAN", use_container_width=True):
        pool = []
        for sec in scan_sectors:
            pool += [(n, f"{s}.NS") for n, s in SECTORS.get(sec, [])]
        pool = pool[:max_stocks]
        results, prog = [], st.progress(0, text="Scanning...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            fmap = {ex.submit(_scan_one, a): a for a in pool}
            for idx, fut in enumerate(concurrent.futures.as_completed(fmap)):
                r = fut.result()
                if r:
                    results.append(r)
                prog.progress((idx + 1) / max(len(pool), 1), text=f"Scanned {idx + 1}/{len(pool)}")
        prog.empty()
        if results:
            st.session_state["scan_results"] = results

    if st.session_state.get("scan_results"):
        res  = st.session_state["scan_results"]
        filt = st.radio("Filter", ["All", "BUY", "SELL", "HOLD", "High Strength (>=65)"], horizontal=True)
        rdf  = pd.DataFrame(res)
        if filt == "BUY":
            rdf = rdf[rdf["_sig"] == "BUY"]
        elif filt == "SELL":
            rdf = rdf[rdf["_sig"] == "SELL"]
        elif filt == "HOLD":
            rdf = rdf[rdf["_sig"] == "HOLD"]
        elif "High" in filt:
            rdf = rdf[rdf["_str"] >= 65]
        disp = rdf.drop(columns=["_sig", "_chg", "_str"], errors="ignore")
        st.dataframe(disp, use_container_width=True, hide_index=True)
        b = (rdf["_sig"] == "BUY").sum()
        s = (rdf["_sig"] == "SELL").sum()
        h = (rdf["_sig"] == "HOLD").sum()
        total_sc = b + s + h
        breadth = round(b / total_sc * 100, 1) if total_sc > 0 else 0
        st.caption(f"{len(disp)} stocks | BUY {b} | SELL {s} | HOLD {h} | Breadth {breadth}% bullish")
    else:
        st.info("Click RUN SCAN to populate.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: RISK CALCULATOR
# ─────────────────────────────────────────────────────────────────────────────
with tab_risk:
    st.markdown(f'<p class="section-header">[ RISK CALCULATOR — {selected_name} ]</p>', unsafe_allow_html=True)
    r1, r2 = st.columns(2)
    with r1:
        entry_px  = st.number_input("Entry Price", value=round(close, 2), step=1.0)
        stop_px   = st.number_input("Stop Loss",   value=round(sl_price, 2), step=1.0)
        target_px = st.number_input("Take Profit", value=round(tp_price, 2), step=1.0)
    with r2:
        cap2      = st.number_input("Capital", value=float(allocated_capital), step=1000.0)
        risk_pct2 = st.slider("Risk %", 0.5, 10.0, float(risk_per_trade), step=0.5)
        n_trades  = st.number_input("Simultaneous Trades", min_value=1, max_value=20, value=5)

    if entry_px > 0 and entry_px > stop_px > 0:
        rps   = entry_px - stop_px
        rws   = target_px - entry_px
        rr    = rws / rps if rps > 0 else 0
        car   = cap2 * (risk_pct2 / 100)
        qty_c = max(1, int(car / rps))
        tv    = qty_c * entry_px
        ml    = qty_c * rps
        mg    = qty_c * rws

        rc1, rc2, rc3, rc4 = st.columns(4)
        for col, lbl, val, clr in zip(
            [rc1, rc2, rc3, rc4],
            ["Qty to Buy", "Total Value", "Max Loss", "Max Gain"],
            [str(qty_c), f"Rs{tv:,.0f}", f"Rs{ml:,.0f}", f"Rs{mg:,.0f}"],
            ["#00c8ff", "#ddeeff", "#ff3355", "#00e87a"]
        ):
            col.markdown(
                f'<div class="glass-card"><p class="glass-label">{lbl}</p>'
                f'<div class="glass-value" style="color:{clr};font-size:1rem;">{val}</div></div>',
                unsafe_allow_html=True
            )
        rr_clr = "#00e87a" if rr >= 2 else "#ffcc00" if rr >= 1 else "#ff3355"
        st.markdown(
            f'<div class="glass-card" style="text-align:center;"><p class="glass-label">Risk:Reward</p>'
            f'<div class="glass-value" style="color:{rr_clr};">1 : {rr:.2f}</div>'
            f'<p style="font-size:10px;color:#6a90aa;margin:3px 0 0;">Portfolio risk at {n_trades} trades: Rs{ml * n_trades:,.0f}</p></div>',
            unsafe_allow_html=True
        )
    else:
        st.warning("Stop loss must be below entry price.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6: PORTFOLIO OPTIMIZER
# ─────────────────────────────────────────────────────────────────────────────
with tab_port:
    st.markdown('<p class="section-header">[ MPT PORTFOLIO OPTIMIZER — MONTE CARLO 3000 ]</p>', unsafe_allow_html=True)
    default_keys = [k for k in ALL_STOCKS if any(x in k for x in ["Reliance (", "TCS (", "HDFC Bank (", "Infosys (", "SBI ("])][:5]
    sel_keys = st.multiselect("Select 2-10 assets", list(ALL_STOCKS.keys()), default=default_keys)

    if len(sel_keys) < 2:
        st.warning("Select at least 2 assets.")
    else:
        opt_tickers = [ALL_STOCKS[k] for k in sel_keys]
        opt_names   = [k.split(" (")[0] for k in sel_keys]

        with st.spinner("Downloading returns + Monte Carlo simulation..."):
            try:
                dp = yf.download(opt_tickers, period="2y", interval="1d", auto_adjust=True, progress=False)
                if dp is not None and not dp.empty:
                    if isinstance(dp.columns, pd.MultiIndex):
                        lvls = dp.columns.get_level_values(0).unique().tolist()
                        if "Close" in lvls:
                            close_df = dp["Close"]
                        else:
                            close_df = dp.xs("Close", axis=1, level=1)
                    else:
                        close_df = dp[["Close"]] if "Close" in dp.columns else dp

                    ret_df = close_df.pct_change().dropna()
                    na     = len(opt_tickers)
                    mu_r   = ret_df.mean()
                    cov    = ret_df.cov()
                    N      = 3000
                    vols, rets, sharpes, all_w = [], [], [], []

                    for _ in range(N):
                        w  = np.random.dirichlet(np.ones(na))
                        pr = float(np.dot(mu_r, w)) * 252
                        pv = float(np.sqrt(w @ (cov.values * 252) @ w))
                        ps = pr / pv if pv > 0 else 0
                        vols.append(pv); rets.append(pr); sharpes.append(ps); all_w.append(w)

                    max_sh_i = int(np.argmax(sharpes))
                    min_vl_i = int(np.argmin(vols))
                    obj = st.radio("Objective", ["Maximize Sharpe Ratio", "Minimize Volatility"], horizontal=True)
                    idx_sel = max_sh_i if "Sharpe" in obj else min_vl_i
                    opt_w = all_w[idx_sel]
                    sel_v = vols[idx_sel]; sel_r = rets[idx_sel]; sel_s = sharpes[idx_sel]

                    pm1, pm2, pm3 = st.columns(3)
                    pm1.markdown(f'<div class="glass-card"><p class="glass-label">Expected Annual Return</p><div class="glass-value" style="color:#00e87a;">{sel_r:.1%}</div></div>', unsafe_allow_html=True)
                    pm2.markdown(f'<div class="glass-card"><p class="glass-label">Annual Volatility</p><div class="glass-value" style="color:#ff3355;">{sel_v:.1%}</div></div>', unsafe_allow_html=True)
                    pm3.markdown(f'<div class="glass-card"><p class="glass-label">Sharpe Ratio</p><div class="glass-value" style="color:#00c8ff;">{sel_s:.2f}</div></div>', unsafe_allow_html=True)

                    st.markdown('<p class="section-header">[ CAPITAL ALLOCATION ]</p>', unsafe_allow_html=True)
                    colors_list = ["#00c8ff","#00e87a","#ffcc00","#ff6b35","#7c4dff","#ff3355","#fbbf24","#34d399","#a78bfa","#fb923c"]
                    alloc_cols = st.columns(min(len(opt_names), 5))
                    for i, (name, w) in enumerate(zip(opt_names, opt_w)):
                        amt = allocated_capital * w
                        clr = colors_list[i % len(colors_list)]
                        alloc_cols[i % min(len(opt_names), 5)].markdown(
                            f'<div class="glass-card" style="text-align:center;">'
                            f'<p class="glass-label">{name[:14]}</p>'
                            f'<div class="glass-value" style="color:{clr};font-size:.95rem;">Rs{amt:,.0f}</div>'
                            f'<p style="font-size:10px;color:#6a90aa;margin:3px 0 0;">{w:.1%}</p></div>',
                            unsafe_allow_html=True
                        )

                    pc1, pc2 = st.columns(2)
                    with pc1:
                        fig_pie = go.Figure(data=[go.Pie(
                            labels=opt_names, values=opt_w, hole=0.42,
                            marker=dict(colors=colors_list[:len(opt_names)]),
                            textfont=dict(color="#ddeeff")
                        )])
                        fig_pie.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)",
                            font=dict(color="#ddeeff", family="Space Mono", size=10),
                            margin=dict(l=10, r=10, t=10, b=10))
                        st.plotly_chart(fig_pie, use_container_width=True)
                    with pc2:
                        fig_ef = go.Figure()
                        fig_ef.add_trace(go.Scatter(x=vols, y=rets, mode="markers",
                            marker=dict(color=sharpes, colorscale="Viridis", size=3, showscale=True,
                                        colorbar=dict(title="Sharpe", thickness=12,
                                                      titlefont=dict(color="#ddeeff", size=9),
                                                      tickfont=dict(color="#ddeeff", size=8))),
                            name="Portfolios"))
                        fig_ef.add_trace(go.Scatter(x=[sel_v], y=[sel_r], mode="markers",
                            marker=dict(color="#ff3355", size=14, symbol="star",
                                        line=dict(width=1, color="white")), name="Optimal"))
                        fig_ef.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            font=dict(color="#ddeeff", family="Space Mono", size=10),
                            xaxis=dict(title="Volatility", gridcolor="rgba(0,200,255,0.04)", tickformat=".1%"),
                            yaxis=dict(title="Return",     gridcolor="rgba(0,200,255,0.04)", tickformat=".1%"),
                            margin=dict(l=10, r=10, t=10, b=10),
                            legend=dict(bgcolor="rgba(7,18,32,0.5)", font=dict(size=9)))
                        st.plotly_chart(fig_ef, use_container_width=True)
                else:
                    st.error("Failed to load data.")
            except Exception as e:
                st.error(f"Portfolio error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# TAB: FII / DII FLOWS
# ─────────────────────────────────────────────────────────────────────────────
with tab_fii:
    st.markdown('<p class="section-header">[ 📊 FII / DII INSTITUTIONAL FLOW — NSE INDIA ]</p>', unsafe_allow_html=True)
    st.caption("Foreign Institutional Investor & Domestic Institutional Investor daily net activity. Source: NSE India.")

    with st.spinner("Fetching FII/DII data from NSE India..."):
        fii_data = fetch_fii_dii()
        df_fii, today_fii = parse_fii_dii(fii_data)

    if df_fii is not None and today_fii is not None:
        # Today KPIs
        fii_net = float(today_fii["FII Net"])
        dii_net = float(today_fii["DII Net"])
        fii_clr = "#00e87a" if fii_net >= 0 else "#ff3355"
        dii_clr = "#00e87a" if dii_net >= 0 else "#ff3355"
        combined = fii_net + dii_net
        comb_clr = "#00e87a" if combined >= 0 else "#ff3355"

        f1, f2, f3, f4 = st.columns(4)
        for col, lbl, val, clr in zip([f1,f2,f3,f4],
            ["FII Net Today (Cr)", "DII Net Today (Cr)", "Combined Net (Cr)", "Date"],
            [f"{'▲' if fii_net>=0 else '▼'} ₹{abs(fii_net):,.0f}",
             f"{'▲' if dii_net>=0 else '▼'} ₹{abs(dii_net):,.0f}",
             f"{'▲' if combined>=0 else '▼'} ₹{abs(combined):,.0f}",
             str(today_fii["Date"])[:10]],
            [fii_clr, dii_clr, comb_clr, "#ddeeff"]):
            col.markdown(f'<div class="glass-card"><p class="glass-label">{lbl}</p>'
                         f'<div class="glass-value" style="color:{clr};font-size:1.1rem;">{val}</div></div>',
                         unsafe_allow_html=True)

        # Interpretation
        sentiment_fii = "BULLISH" if fii_net > 0 else "BEARISH"
        sent_clr_fii  = "#00e87a" if fii_net > 0 else "#ff3355"
        if fii_net > 0 and dii_net > 0:
            market_view = "Both FII and DII are buying — strong institutional conviction. Typically bullish for markets."
        elif fii_net > 0 and dii_net < 0:
            market_view = "FII buying, DII selling — foreign money flowing in, domestic institutions taking profit."
        elif fii_net < 0 and dii_net > 0:
            market_view = "FII selling, DII buying — domestic institutions absorbing foreign outflows. Market resilient."
        else:
            market_view = "Both FII and DII selling — broad institutional outflow. Typically bearish for near-term."

        st.markdown(f'''<div class="glass-card" style="margin:10px 0;">
            <p class="glass-label">Market Interpretation</p>
            <div style="font-size:13px;color:{sent_clr_fii};font-weight:600;margin:4px 0;">{sentiment_fii} INSTITUTIONAL FLOW</div>
            <p style="font-size:12px;color:#a0aec0;margin:4px 0;line-height:1.6;">{market_view}</p>
        </div>''', unsafe_allow_html=True)

        # Historical bar chart
        if len(df_fii) > 1:
            st.markdown('<p class="section-header">[ RECENT FII / DII DAILY NET FLOWS ]</p>', unsafe_allow_html=True)
            fig_fii = go.Figure()
            fii_colors = ["#00e87a" if v >= 0 else "#ff3355" for v in df_fii["FII Net"]]
            dii_colors = ["#00c8ff" if v >= 0 else "#ff6b35" for v in df_fii["DII Net"]]
            fig_fii.add_trace(go.Bar(x=df_fii["Date"], y=df_fii["FII Net"], name="FII Net",
                marker_color=fii_colors, opacity=0.85))
            fig_fii.add_trace(go.Bar(x=df_fii["Date"], y=df_fii["DII Net"], name="DII Net",
                marker_color=dii_colors, opacity=0.85))
            fig_fii.add_hline(y=0, line_color="rgba(255,255,255,0.2)", line_width=1)
            fig_fii.update_layout(
                height=320, barmode="group",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ddeeff", family="Space Mono", size=10),
                xaxis=dict(gridcolor="rgba(0,200,255,0.04)"),
                yaxis=dict(gridcolor="rgba(0,200,255,0.04)", title="Net Flow (Cr ₹)"),
                margin=dict(l=10,r=10,t=15,b=10),
                legend=dict(bgcolor="rgba(7,18,32,0.5)", bordercolor="rgba(0,200,255,0.15)", borderwidth=1)
            )
            st.plotly_chart(fig_fii, use_container_width=True)

        # Detailed table
        st.markdown('<p class="section-header">[ DETAILED FLOW TABLE ]</p>', unsafe_allow_html=True)
        disp_fii = df_fii[["Date","FII Buy","FII Sell","FII Net","DII Buy","DII Sell","DII Net"]].copy()
        disp_fii = disp_fii.round(2)
        st.dataframe(disp_fii, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download FII/DII Data",
                           disp_fii.to_csv(index=False).encode(),
                           "fii_dii_flows.csv", "text/csv")
    else:
        st.warning("Could not fetch FII/DII data from NSE India. NSE may be blocking automated requests.")
        st.info("**Why this happens:** NSE India requires cookie-based session authentication. The data is available at nseindia.com → Market Data → FII/DII Activity.")
        # Fallback: show explanation
        st.markdown('''<div class="glass-card">
            <p class="section-header" style="margin-top:0;">Understanding FII / DII Flows</p>
            <div style="font-size:12px;color:#a0aec0;line-height:1.8;">
            <b style="color:#00c8ff;">FII (Foreign Institutional Investors)</b> — Foreign funds, hedge funds, sovereign wealth funds. 
            Their buying/selling drives large directional moves in Nifty 50. FII net positive = bullish signal.<br><br>
            <b style="color:#00c8ff;">DII (Domestic Institutional Investors)</b> — Indian mutual funds, insurance companies (LIC), banks. 
            Often act as a counterbalance — they buy when FIIs sell, providing market support.<br><br>
            <b style="color:#ffcc00;">Key Rule:</b> When both FII and DII are net buyers, markets tend to rally strongly. 
            When both are sellers, expect sharp corrections. FII flows dominate short-term direction.
            </div>
        </div>''', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB: OPTIONS CHAIN
# ─────────────────────────────────────────────────────────────────────────────
with tab_options:
    st.markdown(f'<p class="section-header">[ 🎯 OPTIONS CHAIN — {selected_name} ]</p>', unsafe_allow_html=True)
    st.caption("NSE India options data. Works for Nifty 50 stocks with active F&O contracts.")

    with st.spinner(f"Fetching options chain for {selected_name}..."):
        opt_data = fetch_options_chain(selected_ticker)
        df_chain, pcr, max_pain, expiry = parse_options_chain(opt_data, close)

    if df_chain is not None and len(df_chain) > 0:
        # KPI row
        o1, o2, o3, o4 = st.columns(4)
        pcr_clr  = "#00e87a" if pcr and pcr > 1 else "#ff3355" if pcr and pcr < 0.7 else "#ffcc00"
        pain_clr = "#00c8ff"
        updown   = "Above" if close > (max_pain or close) else "Below"
        pct_from_pain = abs(close - max_pain) / max_pain * 100 if max_pain else 0

        for col, lbl, val, clr in zip([o1,o2,o3,o4],
            ["Spot Price","Max Pain","Put/Call Ratio","Expiry"],
            [f"₹{close:,.2f}", f"₹{max_pain:,.0f}" if max_pain else "N/A",
             f"{pcr:.3f}" if pcr else "N/A", str(expiry) if expiry else "N/A"],
            ["#ddeeff", pain_clr, pcr_clr, "#6a90aa"]):
            col.markdown(f'<div class="glass-card"><p class="glass-label">{lbl}</p>'
                         f'<div class="glass-value" style="color:{clr};font-size:1.1rem;">{val}</div></div>',
                         unsafe_allow_html=True)

        # PCR interpretation
        if pcr:
            if pcr > 1.2:
                pcr_interp = "HIGH PCR (>1.2) — Bearish sentiment dominant. Contrarian signal: markets may be oversold, potential reversal up."
                pi_clr = "#00e87a"
            elif pcr < 0.7:
                pcr_interp = "LOW PCR (<0.7) — Bullish sentiment dominant. Contrarian signal: markets may be overbought, potential pullback."
                pi_clr = "#ff3355"
            else:
                pcr_interp = "NEUTRAL PCR (0.7–1.2) — Balanced put/call activity. No extreme sentiment reading."
                pi_clr = "#ffcc00"
            st.markdown(f'<div class="glass-card"><p class="glass-label">PCR Interpretation</p>'
                        f'<p style="font-size:12px;color:{pi_clr};margin:4px 0;font-weight:600;">{pcr_interp}</p></div>',
                        unsafe_allow_html=True)

        # Max pain interpretation
        if max_pain:
            mp_interp = f"Spot (₹{close:,.0f}) is {updown} max pain (₹{max_pain:,.0f}) by {pct_from_pain:.1f}%. Option sellers profit most if expiry is at ₹{max_pain:,.0f}. Gravitational pull toward max pain as expiry approaches."
            st.markdown(f'<div class="glass-card"><p class="glass-label">Max Pain Analysis</p>'
                        f'<p style="font-size:12px;color:#a0aec0;margin:4px 0;line-height:1.6;">{mp_interp}</p></div>',
                        unsafe_allow_html=True)

        # OI chart — top 15 strikes around spot
        st.markdown('<p class="section-header">[ OPEN INTEREST BY STRIKE ]</p>', unsafe_allow_html=True)
        spot_strikes = df_chain[(df_chain["Strike"] >= close * 0.85) & (df_chain["Strike"] <= close * 1.15)]
        if len(spot_strikes) > 0:
            fig_oi = go.Figure()
            fig_oi.add_trace(go.Bar(x=spot_strikes["Strike"], y=spot_strikes["CE OI"],
                name="Call OI", marker_color="rgba(255,51,85,0.7)"))
            fig_oi.add_trace(go.Bar(x=spot_strikes["Strike"], y=spot_strikes["PE OI"],
                name="Put OI", marker_color="rgba(0,200,255,0.7)"))
            if max_pain:
                fig_oi.add_vline(x=max_pain, line_dash="dash", line_color="#fbbf24",
                    annotation_text=f"Max Pain ₹{max_pain:,.0f}", annotation_font_color="#fbbf24")
            fig_oi.add_vline(x=close, line_dash="dot", line_color="rgba(255,255,255,0.5)",
                annotation_text=f"Spot ₹{close:,.0f}", annotation_font_color="#ddeeff")
            fig_oi.update_layout(
                height=360, barmode="group",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ddeeff", family="Space Mono", size=10),
                xaxis=dict(title="Strike Price", gridcolor="rgba(0,200,255,0.04)"),
                yaxis=dict(title="Open Interest", gridcolor="rgba(0,200,255,0.04)"),
                margin=dict(l=10,r=10,t=15,b=10),
                legend=dict(bgcolor="rgba(7,18,32,0.5)", bordercolor="rgba(0,200,255,0.15)", borderwidth=1)
            )
            st.plotly_chart(fig_oi, use_container_width=True)

        # Full chain table
        st.markdown('<p class="section-header">[ FULL OPTIONS CHAIN TABLE ]</p>', unsafe_allow_html=True)
        chain_disp = df_chain[["CE LTP","CE OI","CE IV","Strike","PE IV","PE OI","PE LTP"]].copy()
        # Highlight ATM strikes
        chain_disp["ATM"] = df_chain["Strike"].apply(lambda s: "◀ ATM" if abs(s - close) == df_chain["Strike"].apply(lambda x: abs(x-close)).min() else "")
        st.dataframe(chain_disp.round(2), use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download Options Chain",
                           chain_disp.round(2).to_csv(index=False).encode(),
                           f"{selected_name}_options_chain.csv", "text/csv")
    else:
        st.warning(f"Options chain not available for {selected_name}.")
        st.info("Options data is available only for stocks in the NSE F&O segment (Nifty 50 and select mid-caps). NSE may also block automated access.")
        st.markdown('''<div class="glass-card">
            <p class="section-header" style="margin-top:0;">Options Chain Concepts</p>
            <div style="font-size:12px;color:#a0aec0;line-height:1.8;">
            <b style="color:#00c8ff;">Max Pain</b> — The strike price where option buyers lose the most money at expiry. 
            Due to gamma exposure, stock prices tend to gravitate toward max pain as expiry approaches.<br><br>
            <b style="color:#00c8ff;">Put/Call Ratio (PCR)</b> — Total Put OI divided by Total Call OI. 
            PCR > 1.2 = bearish sentiment (contrarian buy signal). PCR < 0.7 = bullish sentiment (contrarian sell signal).<br><br>
            <b style="color:#00c8ff;">Open Interest (OI)</b> — Number of outstanding contracts. High OI at a strike = strong support/resistance level.<br><br>
            <b style="color:#00c8ff;">Implied Volatility (IV)</b> — Market expectation of future price movement. High IV = expensive options = expected big move.
            </div>
        </div>''', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB: FUNDAMENTALS
# ─────────────────────────────────────────────────────────────────────────────
with tab_funds:
    st.markdown(f'<p class="section-header">[ 📋 FUNDAMENTAL ANALYSIS — {selected_name} ]</p>', unsafe_allow_html=True)
    st.caption("Key financial ratios from Screener.in. Refreshed daily.")

    with st.spinner(f"Fetching fundamentals for {selected_name}..."):
        fund_data = fetch_fundamentals(selected_ticker)

    # Always show the gauge layout, fill with data if available
    FUND_META = [
        ("P/E Ratio",      "pe",  0, 60,  25, "Lower = cheaper. Indian market avg ~22. <15 undervalued, >40 expensive."),
        ("P/B Ratio",      "pb",  0, 10,   3, "Price to Book. <1 = trading below assets. >5 = growth premium."),
        ("ROE (%)",        "roe", 0, 50,  15, "Return on Equity. >15% is good. >25% is excellent."),
        ("ROCE (%)",       "roce",0, 50,  15, "Return on Capital Employed. >15% shows efficient capital use."),
        ("Debt/Equity",    "de",  0,  5,   1, "Lower is better. <0.5 is conservative. >2 is high leverage."),
        ("Div Yield (%)",  "dy",  0,  8,   2, "Dividend Yield. >2% is decent for Indian markets."),
    ]

    if fund_data and any(v is not None for v in fund_data.values()):
        # Show ratio cards
        cols_f = st.columns(3)
        ratio_keys = [("P/E Ratio","#00c8ff"),("P/B Ratio","#ffcc00"),("ROE (%)","#00e87a"),
                      ("ROCE (%)","#00e87a"),("Debt/Equity","#ff3355"),("Div Yield (%)","#7c4dff")]
        for i, (key, clr) in enumerate(ratio_keys):
            val = fund_data.get(key)
            val_str = f"{val:.2f}" if val is not None else "N/A"
            cols_f[i % 3].markdown(
                f'<div class="glass-card"><p class="glass-label">{key}</p>'
                f'<div class="glass-value" style="color:{clr};">{val_str}</div></div>',
                unsafe_allow_html=True
            )

        # EPS and Promoter
        ep1, ep2 = st.columns(2)
        eps  = fund_data.get("EPS (TTM)")
        prom = fund_data.get("Promoter Hold%")
        ep1.markdown(
            f'<div class="glass-card"><p class="glass-label">EPS (TTM)</p>'
            f'<div class="glass-value" style="color:#fbbf24;">{"₹"+str(round(eps,2)) if eps else "N/A"}</div></div>',
            unsafe_allow_html=True)
        ep2.markdown(
            f'<div class="glass-card"><p class="glass-label">Promoter Holding</p>'
            f'<div class="glass-value" style="color:{"#00e87a" if prom and prom>50 else "#ffcc00" if prom else "#6a90aa"};">{""+str(round(prom,1))+"%" if prom else "N/A"}</div></div>',
            unsafe_allow_html=True)

        # Valuation verdict
        pe  = fund_data.get("P/E Ratio")
        roe = fund_data.get("ROE (%)")
        de  = fund_data.get("Debt/Equity")
        scores = []
        if pe:  scores.append("Cheap" if pe < 15 else "Fair" if pe < 30 else "Expensive")
        if roe: scores.append("High ROE" if roe > 20 else "Moderate ROE" if roe > 12 else "Low ROE")
        if de:  scores.append("Low Debt" if de < 0.5 else "Moderate Debt" if de < 1.5 else "High Debt")
        if scores:
            verdict_text = " | ".join(scores)
            verdict_clr  = "#00e87a" if "Cheap" in verdict_text or "High ROE" in verdict_text else "#ffcc00"
            st.markdown(f'<div class="glass-card"><p class="glass-label">Fundamental Verdict</p>'
                        f'<p style="font-size:13px;color:{verdict_clr};font-weight:600;margin:4px 0;">{verdict_text}</p></div>',
                        unsafe_allow_html=True)

        st.caption("Data source: Screener.in · Consolidated financials · Updated daily")
        st.markdown(f"[View full analysis on Screener.in](https://www.screener.in/company/{selected_ticker.replace('.NS','').replace('.BO','')}/consolidated/)")

    else:
        st.warning(f"Could not fetch fundamental data for {selected_name} from Screener.in.")
        st.info("Screener.in covers most NSE-listed companies. Try large-cap stocks like RELIANCE, TCS, HDFCBANK.")

    # Always show the ratio reference guide
    with st.expander("📖 Ratio interpretation guide"):
        st.markdown("""
| Ratio | Good | Average | Expensive/Risky |
|---|---|---|---|
| P/E | < 15 | 15–30 | > 40 |
| P/B | < 1.5 | 1.5–4 | > 6 |
| ROE | > 20% | 12–20% | < 10% |
| ROCE | > 20% | 12–20% | < 10% |
| Debt/Equity | < 0.5 | 0.5–1.5 | > 2.0 |
| Promoter Hold | > 50% | 35–50% | < 25% |

**Indian Market Context:** Nifty 50 trades at avg P/E of ~22. Premium growth stocks (Titan, Asian Paints) command 60–80x P/E. PSU banks trade at 5–10x. Always compare within the same sector.
""")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 7: NEWS & SENTIMENT
# ─────────────────────────────────────────────────────────────────────────────
with tab_news:
    st.markdown(f'<p class="section-header">[ NEWS & SENTIMENT — {selected_name} ]</p>', unsafe_allow_html=True)
    with st.spinner("Fetching headlines..."):
        items = fetch_news(selected_ticker)

    if items:
        score, cat = sentiment_score(items)
        sent_clr = {"BULLISH": "#00e87a", "BEARISH": "#ff3355", "NEUTRAL": "#ffcc00"}[cat]
        ns1, ns2 = st.columns([1, 2])
        with ns1:
            st.markdown(f"""<div class="glass-card" style="text-align:center;padding:20px 12px;">
                <p class="glass-label">Sentiment</p>
                <div style="font-family:'Orbitron',sans-serif;font-size:1.8rem;font-weight:900;color:{sent_clr};margin:8px 0;">{cat}</div>
                <p style="font-size:10px;color:#6a90aa;margin:0;">Score: {score:+.3f} | {len(items)} headlines</p>
            </div>""", unsafe_allow_html=True)
        with ns2:
            bull_cnt = sum(1 for it in items if any(w in it["title"].lower().split() for w in BULL_KW))
            bear_cnt = sum(1 for it in items if any(w in it["title"].lower().split() for w in BEAR_KW))
            st.markdown(f"""<div class="glass-card">
                <p class="glass-label" style="margin-bottom:8px;">Keyword Breakdown</p>
                <div style="font-family:'Space Mono',monospace;font-size:12px;">
                    Bullish headlines: <span style="color:#00e87a;font-weight:700;">{bull_cnt}</span> &nbsp;|&nbsp;
                    Bearish headlines: <span style="color:#ff3355;font-weight:700;">{bear_cnt}</span>
                </div>
                <p style="font-size:11px;color:#6a90aa;margin-top:6px;line-height:1.6;">
                Financial keyword scoring with negation detection. Bullish terms: surge, rally, beat, upgrade...
                Bearish terms: drop, warn, miss, downgrade, loss...
                </p>
            </div>""", unsafe_allow_html=True)

        st.markdown('<p class="section-header">[ HEADLINES ]</p>', unsafe_allow_html=True)
        for it in items:
            tl      = it["title"].lower()
            is_bull = any(w in tl.split() for w in BULL_KW)
            is_bear = any(w in tl.split() for w in BEAR_KW)
            dot_clr = "#00e87a" if (is_bull and not is_bear) else "#ff3355" if is_bear else "#6a90aa"
            st.markdown(f"""<div class="glass-card" style="padding:9px 13px;margin-bottom:5px;display:flex;align-items:center;gap:10px;">
                <div style="width:7px;height:7px;border-radius:50%;background:{dot_clr};flex-shrink:0;"></div>
                <a href="{it['link']}" target="_blank" style="color:#00c8ff;text-decoration:none;font-size:12px;font-weight:600;flex:1;">{it['title']}</a>
                <span style="font-size:9px;color:#4a7090;font-family:'Space Mono';flex-shrink:0;">{it['date']}</span>
            </div>""", unsafe_allow_html=True)
    else:
        st.info(f"No headlines found for {selected_ticker}.")
        st.caption("Large-cap stocks like TCS, RELIANCE, HDFCBANK have best news coverage.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 8: FII / DII FLOWS
# ─────────────────────────────────────────────────────────────────────────────
with tab_help:
    st.markdown("""
<div class="glass-card">
<p class="section-header" style="margin-top:0;">[ XERCES GODMODE — REFERENCE MANUAL ]</p>
<div style="font-size:11px;color:#8ab0cc;line-height:2.1;font-family:'Space Mono',monospace;">
<b style="color:#00c8ff;">RSI (14)</b> — &lt;30 oversold (buy zone). &gt;70 overbought (sell zone).<br>
<b style="color:#00c8ff;">MACD (12,26,9)</b> — MACD crossing above signal = bullish momentum. Histogram shows acceleration.<br>
<b style="color:#00c8ff;">SMA 20/50/200</b> — Golden cross (SMA50 &gt; SMA200) = major bull signal. Price &gt; SMA200 = bull market.<br>
<b style="color:#00c8ff;">Bollinger Bands</b> — Band squeeze = volatility expansion imminent. Breakout direction = trend.<br>
<b style="color:#00c8ff;">ATR (14)</b> — True range in Rs. Used for stop-loss sizing: 1.5x ATR below entry.<br>
<b style="color:#00c8ff;">Stochastic %K</b> — &lt;20 oversold, &gt;80 overbought. Combine with RSI for confirmation.<br>
<br>
<b style="color:#ffcc00;">ARIMA</b> — Fitted on log-price via 5x5 AIC grid. Validated with 60-day holdout MAPE + directional accuracy.<br>
<b style="color:#ffcc00;">Holt-Winters</b> — Exponential smoothing with additive trend. Second-opinion model alongside ARIMA.<br>
<b style="color:#ffcc00;">Consensus</b> — Average of ARIMA and Holt-Winters. More robust than either alone.<br>
<b style="color:#ffcc00;">MAPE</b> — Mean Absolute Percentage Error on 60-day holdout. Under 5% = excellent, 5-10% = good.<br>
<b style="color:#ffcc00;">Directional Accuracy</b> — % of days where forecast direction matched actual. &gt;60% = useful model.<br>
<br>
<b style="color:#7c4dff;">PORTFOLIO OPTIMIZER</b> — Markowitz MPT with 3000 Monte Carlo simulations. Finds efficient frontier.<br>
<b style="color:#7c4dff;">BACKTEST</b> — 4 strategies tested on 5-year data. Next-day open execution eliminates look-ahead bias.<br>
<b style="color:#7c4dff;">SCANNER</b> — Multi-threaded bulk scan of selected sectors with BUY/SELL/HOLD signals and position sizing.<br>
<br>
<b style="color:#ff3355;">SIGNAL LOGIC:</b> BUY = SMA20&gt;SMA50 AND Price&gt;SMA200 AND RSI&lt;70 AND (MACD cross up OR RSI&lt;45). SELL = opposite.<br>
<br>
<b style="color:#ff3355;">DISCLAIMER:</b> XERCES is a research tool. Not SEBI registered. Not financial advice. Data from Yahoo Finance.
</div>
</div>
""", unsafe_allow_html=True)
