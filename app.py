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
import urllib.parse
import re
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
        df = yf.download(ticker, period=period, interval="1d", auto_adjust=True,
                          progress=False, timeout=10)
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

def _download_raw(ticker: str, period: str = "1y"):
    try:
        df = yf.download(ticker, period=period, interval="1d", auto_adjust=True,
                          progress=False, timeout=8, threads=False)
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
    low14  = out["Low"].astype(float).rolling(14).min() if "Low" in out.columns else c.rolling(14).min()
    high14 = out["High"].astype(float).rolling(14).max() if "High" in out.columns else c.rolling(14).max()
    out["Stoch_K"] = (c - low14) / (high14 - low14 + 1e-9) * 100
    out["Stoch_D"] = out["Stoch_K"].rolling(3).mean()
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

@st.cache_data(ttl=900, show_spinner=False)
def fetch_news(ticker: str, company_name: str = ""):
    clean = ticker.replace(".NS", "").replace(".BO", "")
    query = company_name.strip() if company_name.strip() else clean
    items = []
    try:
        gquery = urllib.parse.quote(f"{query} stock NSE")
        gurl = f"https://news.google.com/rss/search?q={gquery}&hl=en-IN&gl=IN&ceid=IN:en"
        req = urllib.request.Request(gurl, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            root = ET.fromstring(r.read())
        for item in root.findall(".//item")[:15]:
            title   = (item.find("title").text   or "") if item.find("title")   is not None else ""
            link    = (item.find("link").text    or "") if item.find("link")    is not None else ""
            pubdate = (item.find("pubDate").text or "") if item.find("pubDate") is not None else ""
            if title:
                items.append({"title": title, "link": link, "date": pubdate[:16]})
    except Exception:
        pass
    if items:
        return items
    try:
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={clean}&region=IN&lang=en-IN"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as r:
            root = ET.fromstring(r.read())
        for item in root.findall(".//item"):
            title   = (item.find("title").text   or "") if item.find("title")   is not None else ""
            link    = (item.find("link").text    or "") if item.find("link")    is not None else ""
            pubdate = (item.find("pubDate").text or "") if item.find("pubDate") is not None else ""
            if title:
                items.append({"title": title, "link": link, "date": pubdate[:16]})
    except Exception:
        pass
    return items

# ══════════════════════════════════════════════════════════════════════════════
# NEW: BACKTESTING ENGINE LOGIC IMPLEMENTATION
# ══════════════════════════════════════════════════════════════════════════════
def run_backtest(df: pd.DataFrame, initial_capital: float = 100000.0, risk_reward_ratio: float = 2.0):
    if len(df) < 52:
        return None
    capital = initial_capital
    position = 0  
    entry_price = 0.0
    stop_loss = 0.0
    take_profit = 0.0
    trades = []
    equity_curve = []
    dates = []
    
    signals = [get_signal(df.iloc[:i+1]) for i in range(len(df))]
    
    for i in range(52, len(df)):
        row = df.iloc[i]
        current_price = float(row["Close"])
        current_date = row["Date"]
        current_signal = signals[i]
        atr = float(row["ATR_14"]) if "ATR_14" in df.columns and pd.notna(row["ATR_14"]) else (current_price * 0.02)

        if position == 1:
            if current_price <= stop_loss:
                capital = capital * (stop_loss / entry_price)
                trades.append({"type": "EXIT_SL", "price": stop_loss, "date": current_date, "pnl": (stop_loss - entry_price) / entry_price})
                position = 0
            elif current_price >= take_profit:
                capital = capital * (take_profit / entry_price)
                trades.append({"type": "EXIT_TP", "price": take_profit, "date": current_date, "pnl": (take_profit - entry_price) / entry_price})
                position = 0
            elif current_signal == "SELL":
                capital = capital * (current_price / entry_price)
                trades.append({"type": "EXIT_SIG", "price": current_price, "date": current_date, "pnl": (current_price - entry_price) / entry_price})
                position = 0
        elif position == 0 and current_signal == "BUY":
            position = 1
            entry_price = current_price
            stop_loss = current_price - (atr * 1.5)
            take_profit = current_price + (atr * 1.5 * risk_reward_ratio)
            trades.append({"type": "ENTRY", "price": entry_price, "date": current_date, "pnl": 0.0})

        current_value = capital if position == 0 else capital * (current_price / entry_price)
        equity_curve.append(current_value)
        dates.append(current_date)

    if not trades:
        return None

    equity_series = pd.Series(equity_curve)
    total_return = ((equity_curve[-1] - initial_capital) / initial_capital) * 100
    roll_max = equity_series.cummax()
    drawdowns = (equity_series - roll_max) / roll_max
    max_drawdown = float(drawdowns.min() * 100) if not drawdowns.empty else 0.0
    closed_trades = [t for t in trades if "EXIT" in t["type"]]
    winning_trades = [t for t in closed_trades if t["pnl"] > 0]
    win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0.0

    return {
        "total_return": total_return,
        "win_rate": win_rate,
        "max_drawdown": max_drawdown,
        "final_value": equity_curve[-1],
        "equity_df": pd.DataFrame({"Date": dates, "Equity": equity_curve}),
        "trade_count": len(closed_trades)
    }

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR AND CAPITAL CONFIGS
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<p class='xerces-title' style='font-size:1.4rem;'>XERCES CORES</p>", unsafe_allow_html=True)
    st.markdown("<hr style='margin:8px 0; border-color:rgba(0,200,255,0.15);'>", unsafe_allow_html=True)
    
    st.markdown("<p class='section-header'>[ RISK CONTROLS ]</p>", unsafe_allow_html=True)
    allocated_capital = st.number_input("Capital Pool (₹)", min_value=1000, value=100000, step=5000)
    risk_reward_ratio = st.slider("Risk Vector (1:X Take Profit)", 1.5, 4.0, 2.0, step=0.5)
    
    st.markdown("<p class='section-header'>[ STOCK SCANNER ]</p>", unsafe_allow_html=True)
    selected_sector = st.selectbox("Choose Target Sector Matrix", options=list(SECTORS.keys()))
    sector_stocks = SECTORS[selected_sector]
    selected_stock_key = st.selectbox("🎯 Target Radar Ticker", options=[f"{n} ({s})" for n, s in sector_stocks])
    full_ticker = ALL_STOCKS[selected_stock_key]

# ══════════════════════════════════════════════════════════════════════════════
# APPLICATION HEADERS & TELEMENTRY SYSTEM ROWS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<h1 class="xerces-title">XERCES // QUANT CORES</h1>', unsafe_allow_html=True)
st.markdown('<p class="telemetry-tag">[ SYSTEM CHANNELS: ACTIVE LOGGING RUN INITIALIZED ]</p>', unsafe_allow_html=True)

# Top Global Core Telemetry Rows
n1, n2, n3, n4 = st.columns(4)
with n1:
    st.markdown(f'<div class="glass-card"><p class="glass-label">[ Total Cash Pool ]</p><div class="glass-value" style="color:#ddeeff;">₹{allocated_capital:,.2f}</div></div>', unsafe_allow_html=True)
with n2:
    st.markdown(f'<div class="glass-card"><p class="glass-label">[ Stock Invested ]</p><div class="glass-value" style="color:#00e87a;">₹0.00</div></div>', unsafe_allow_html=True)
with n3:
    st.markdown(f'<div class="glass-card"><p class="glass-label">[ Unallocated Cash ]</p><div class="glass-value" style="color:#ffcc00;">₹{allocated_capital:,.2f}</div></div>', unsafe_allow_html=True)
with n4:
    st.markdown(f'<div class="glass-card"><p class="glass-label">[ Net Total Wealth ]</p><div class="glass-value" style="color:#00c8ff;">₹{allocated_capital:,.2f}</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CORE NAVIGATION TABS ASSEMBLY
# ══════════════════════════════════════════════════════════════════════════════
view_tab, backtest_tab, scanner_tab, news_tab = st.tabs([
    "🔍 TERMINAL ANALYSIS & FORECAST", 
    "📈 BACKTEST ENGINE",
    "⚡ CONCURRENT NETWORK SCANNER",
    "📰 INTELLIGENCE & SENTIMENT FEED"
])

df_asset = load_ohlcv(full_ticker, period="5y")

# ──────────────────────────────────────────────────────────
# TAB 1: TERMINAL ANALYSIS & PREDICTIVE FORECAST CHANNELS
# ──────────────────────────────────────────────────────────
with view_tab:
    if df_asset is not None and not df_asset.empty:
        df = add_indicators(df_asset)
        last_row = df.iloc[-1]
        last_close = float(last_row["Close"])
        signal = get_signal(df)
        strength = get_signal_strength(df)

        left_p, right_p = st.columns([2.2, 1])
        
        with left_p:
            st.markdown(f'<p class="section-header">[ 📊 TECHNICAL STREAM FOR {selected_stock_key} ]</p>', unsafe_allow_html=True)
            
            # Predictive Engineering Calculations (ARIMA + Holt-Winters)
            with st.spinner("Processing optimization matrices..."):
                steps_pred = 60
                fc_arima, low_ci, up_ci, order_arima, aic_val, _, _ = run_arima(df["Close"], steps=steps_pred)
                fc_hw = run_holt_winters(df["Close"], steps=steps_pred)
                mape_val, dir_acc = compute_accuracy(df["Close"], order_arima)
                
                # Generate Projection Subplots
                future_dates = [df["Date"].iloc[-1] + datetime.timedelta(days=i) for i in range(1, steps_pred + 1)]
                
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.7, 0.3])
                fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Historical Close", line=dict(color="#00c8ff", width=2)), row=1, col=1)
                fig.add_trace(go.Scatter(x=future_dates, y=fc_arima, name=f"ARIMA {order_arima}", line=dict(color="#00e87a", width=2, dash="dash")), row=1, col=1)
                fig.add_trace(go.Scatter(x=future_dates, y=fc_hw, name="Holt-Winters Vector", line=dict(color="#ffcc00", width=2, dash="dot")), row=1, col=1)
                
                if "RSI_14" in df.columns:
                    fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI_14"], name="RSI (14)", line=dict(color="#ff3355", width=1)), row=2, col=1)
                    fig.add_hline(y=70, line_dash="dash", line_color="rgba(255,51,85,0.3)", row=2, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="rgba(0,232,122,0.3)", row=2, col=1)
                
                fig.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#ddeeff", family="Space Mono"), height=480, showlegend=True,
                    xaxis2=dict(gridcolor="rgba(0,200,255,0.04)"), yaxis=dict(gridcolor="rgba(0,200,255,0.04)"),
                    yaxis2=dict(gridcolor="rgba(0,200,255,0.04)", range=[0, 100])
                )
                st.plotly_chart(fig, use_container_width=True)
                
        with right_p:
            st.markdown('<p class="section-header">[ ⚡ MATRIX METRICS ]</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="glass-card"><p class="glass-label">[ Last Asset Valuation ]</p><div class="glass-value">₹{last_close:,.2f}</div></div>', unsafe_allow_html=True)
            
            color_map = {"BUY": "#00e87a", "SELL": "#ff3355", "HOLD": "#ffcc00"}
            st.markdown(f'<div class="glass-card"><p class="glass-label">[ Structural Bias ]</p><div class="glass-value" style="color:{color_map.get(signal)};">{signal} ({strength}%)</div></div>', unsafe_allow_html=True)
            
            st.markdown('<p class="section-header">[ 🧠 FORECAST MODEL TELEMETRY ]</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="glass-card"><p class="glass-label">[ Optimal Order Structural Match ]</p><div class="glass-value" style="font-size:1.1rem; color:#00c8ff;">ARIMA {order_arima}</div></div>', unsafe_allow_html=True)
            
            if mape_val is not None:
                acc_style = "accuracy-good" if mape_val < 5 else ("accuracy-mid" if mape_val < 12 else "accuracy-bad")
                st.markdown(f'<div class="glass-card"><p class="glass-label">[ Holdout Back-Validation MAPE ]</p><div class="glass-value {acc_style}">{mape_val}%</div></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="glass-card"><p class="glass-label">[ Directional Movement Target Hit ]</p><div class="glass-value" style="color:#00e87a;">{dir_acc}%</div></div>', unsafe_allow_html=True)
    else:
        st.error("❌ Target asset data link failure. Verify structure settings.")

# ──────────────────────────────────────────────────────────
# TAB 2: BACKTEST ENGINE FRAMEWORK PANEL
# ──────────────────────────────────────────────────────────
with backtest_tab:
    st.markdown("<p class='telemetry-tag' style='color:#00c8ff;'>[ // STRATEGIC BACKTEST RADAR SIMULATION CHANNELS ACTIVE ]</p>", unsafe_allow_html=True)
    if df_asset is not None and not df_asset.empty:
        df = add_indicators(df_asset)
        with st.spinner("Compiling tactical backtest metrics..."):
            bt_results = run_backtest(df, initial_capital=float(allocated_capital), risk_reward_ratio=risk_reward_ratio)
            
            if bt_results:
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    ret_color = "#00e87a" if bt_results["total_return"] >= 0 else "#ff3355"
                    st.markdown(f'<div class="glass-card"><p class="glass-label">[ Simulated Return ]</p><div class="glass-value" style="color:{ret_color};">{bt_results["total_return"]:+.2f}%</div></div>', unsafe_allow_html=True)
                with m2:
                    st.markdown(f'<div class="glass-card"><p class="glass-label">[ Algorithmic Win Rate ]</p><div class="glass-value" style="color:#00c8ff;">{bt_results["win_rate"]:.1f}%</div></div>', unsafe_allow_html=True)
                with m3:
                    st.markdown(f'<div class="glass-card"><p class="glass-label">[ System Drawdown Peak ]</p><div class="glass-value" style="color:#ffcc00;">{bt_results["max_drawdown"]:.2f}%</div></div>', unsafe_allow_html=True)
                with m4:
                    st.markdown(f'<div class="glass-card"><p class="glass-label">[ Transaction Blocks Executed ]</p><div class="glass-value" style="color:#ddeeff;">{bt_results["trade_count"]} Blocks</div></div>', unsafe_allow_html=True)
                
                st.markdown('<p class="section-header">[ 📈 SIMULATED ACCUMULATED EQUITY CURVE ]</p>', unsafe_allow_html=True)
                fig_bt = go.Figure()
                fig_bt.add_trace(go.Scatter(x=bt_results["equity_df"]["Date"], y=bt_results["equity_df"]["Equity"], name="System Wealth Pool", line=dict(color="#00e87a", width=2)))
                fig_bt.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#ddeeff", family="Space Mono"), height=300,
                    xaxis=dict(gridcolor="rgba(0,200,255,0.04)"), yaxis=dict(gridcolor="rgba(0,200,255,0.04)")
                )
                st.plotly_chart(fig_bt, use_container_width=True)
            else:
                st.warning("⚠️ No historical transition signal vectors found to compute systematic metrics profiling.")
    else:
        st.info("💡 Target engine historical analysis stream must be populated before compiling backtest matrices.")

# ──────────────────────────────────────────────────────────
# TAB 3: THREAD-SAFE CONCURRENT SECTOR NETWORK SCANNER
# ──────────────────────────────────────────────────────────
with scanner_tab:
    st.markdown("<p class='section-header'>[ ⚡ PARALLELIZED TELEMETRY MATRIX HARVESTER ]</p>", unsafe_allow_html=True)
    if st.button("RUN CONCURRENT AGGREGATOR SEQUENCE"):
        progress_bar = st.progress(0)
        status_box = st.empty()
        
        scanned_records = []
        stock_items = list(ALL_STOCKS.items())
        total_units = len(stock_items)
        
        def scan_worker(item):
            label, full_sym = item
            raw = _download_raw(full_sym, period="1y")
            if raw is not None and len(raw) > 30:
                ind = add_indicators(raw)
                return {"label": label, "sig": get_signal(ind), "str": get_signal_strength(ind), "close": float(ind["Close"].iloc[-1])}
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as exec_matrix:
            future_to_stock = {exec_matrix.submit(scan_worker, item): item for item in stock_items}
            for index, fut in enumerate(concurrent.futures.as_completed(future_to_stock)):
                res = fut.result()
                if res:
                    scanned_records.append(res)
                progress_bar.progress((index + 1) / total_units)
                status_box.text(f"Processed stream {index+1}/{total_units} frames...")
                
        if scanned_records:
            scan_df = pd.DataFrame(scanned_records)
            buy_df = scan_df[scan_df["sig"] == "BUY"].sort_values(by="str", ascending=False)
            sell_df = scan_df[scan_df["sig"] == "SELL"].sort_values(by="str", ascending=False)
            
            c_left, c_right = st.columns(2)
            with c_left:
                st.markdown("<p style='color:#0
