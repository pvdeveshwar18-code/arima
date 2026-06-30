import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
import pytz
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import urllib.request
import urllib.parse
import urllib.error
import re
import xml.etree.ElementTree as ET
import json
import time
import io
import zipfile
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.holtwinters import ExponentialSmoothing
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════════
# PAGE & THEME
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(page_title="XERCES // QUANT ENGINE v2", page_icon="⚡", layout="wide")
IST = pytz.timezone("Asia/Kolkata")

def inject_css():
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
</style>
""", unsafe_allow_html=True)
inject_css()

def init_state():
    for k,v in {"search_query":"","scan_results":[],"scan_done":False,"last_data_tick":"--"}.items():
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

# ═══════════════════════════════════════════════════════════════════
# STOCK UNIVERSE — 600+ COMPACT# ═══════════════════════════════════════════════════════════════════
def _stocks(*pairs):
    return [tuple(p.split(":",1)) for p in pairs]

SECTORS = {
    "🏦 Banking & Finance": _stocks(
        "HDFC Bank:HDFCBANK","ICICI Bank:ICICIBANK","SBI:SBIN","Kotak Mahindra Bank:KOTAKBANK",
        "Axis Bank:AXISBANK","IndusInd Bank:INDUSINDBK","Bank of Baroda:BANKBARODA","PNB:PNB",
        "Canara Bank:CANBK","Union Bank:UNIONBANK","Bank of India:BANKINDIA","Indian Bank:INDIANB",
        "UCO Bank:UCOBANK","Central Bank:CENTRALBK","IOB:IOB","Federal Bank:FEDERALBNK",
        "RBL Bank:RBLBANK","Yes Bank:YESBANK","IDFC First Bank:IDFCFIRSTB","Bandhan Bank:BANDHANBNK",
        "AU Small Finance Bank:AUBANK","Equitas Small Finance:EQUITASBNK","Ujjivan Small Finance:UJJIVANSFB",
        "City Union Bank:CUB","Karur Vysya Bank:KARURVYSYA","South Indian Bank:SOUTHBANK",
        "Dhanlaxmi Bank:DHANBANK","Karnataka Bank:KTKBANK","Bajaj Finance:BAJFINANCE",
        "Bajaj Finserv:BAJAJFINSV","Cholamandalam Finance:CHOLAFIN","Muthoot Finance:MUTHOOTFIN",
        "Manappuram Finance:MANAPPURAM","L&T Finance:LTF","Shriram Finance:SHRIRAMFIN",
        "Piramal Enterprises:PEL","HDFC AMC:HDFCAMC","Nippon India AMC:NAM-INDIA","UTI AMC:UTIAMC",
        "Aditya Birla AMC:ABSLAMC","SBI Cards:SBICARD","SBI Life Insurance:SBILIFE","HDFC Life:HDFCLIFE",
        "LIC India:LICI","Star Health Insurance:STARHEALTH","New India Assurance:NIACL",
        "General Insurance Corp:GICRE","ICICI Prudential Life:ICICIPRULI","ICICI Lombard:ICICIGI",
        "Max Financial:MFSL","Five Star Business:FIVESTAR","Aavas Financiers:AAVAS",
        "Home First Finance:HOMEFIRST","Aptus Value Housing:APTUS","Repco Home Finance:REPCOHOME",
        "Can Fin Homes:CANFINHOME","LIC Housing Finance:LICHSGFIN"
    ),
    "💻 IT & Technology": _stocks(
        "TCS:TCS","Infosys:INFY","HCL Technologies:HCLTECH","Wipro:WIPRO","Tech Mahindra:TECHM",
        "LTIMindtree:LTIM","Mphasis:MPHASIS","Coforge:COFORGE","Persistent Systems:PERSISTENT",
        "L&T Technology:LTTS","Tata Elxsi:TATAELXSI","KPIT Technologies:KPITTECH",
        "Zensar Technologies:ZENSARTECH","Mastek:MASTEK","Hexaware:HEXAWARE","Birlasoft:BSOFT",
        "Intellect Design:INTELLECT","Cyient:CYIENT","Sonata Software:SONATSOFTW",
        "Happiest Minds:HAPPSTMNDS","Tanla Platforms:TANLA","Firstsource Solutions:FSL",
        "Newgen Software:NEWGEN","Ramco Systems:RAMCOSYS","KFIN Technologies:KFINTECH",
        "Angel One:ANGELONE","Route Mobile:ROUTE","Nazara Technologies:NAZARA",
        "Netweb Technologies:NETWEB","Tata Communications:TATACOMM","Rategain Travel Tech:RATEGAIN",
        "Zaggle Prepaid:ZAGGLE","Majesco:MAJESCO","Saksoft:SAKSOFT","Nucleus Software:NUCLEUSSOFT"
    ),
    "🏭 Industrials & Capital Goods": _stocks(
        "Larsen & Toubro:LT","Siemens India:SIEMENS","ABB India:ABB","Bharat Electronics:BEL",
        "HAL:HAL","BEML:BEML","Thermax:THERMAX","Cummins India:CUMMINSIND",
        "Bharat Forge:BHARATFORG","Ramkrishna Forgings:RKFORGE","Escorts Kubota:ESCORTS",
        "Carborundum Universal:CARBORUNIV","AIA Engineering:AIAENG","Timken India:TIMKEN",
        "Schaeffler India:SCHAEFFLER","SKF India:SKFINDIA","Grindwell Norton:GRINDWELL",
        "Elgi Equipments:ELGIEQUIP","Kirloskar Brothers:KIRLOSBROS","KSB:KSB",
        "Voltamp Transformers:VOLTAMP","Sterling Wilson:SWSOLAR","Va Tech Wabag:WABAG",
        "NBCC:NBCC","NCC:NCC","KEC International:KEC","Kalpataru Projects:KPIL",
        "G R Infraprojects:GRINFRA","ITD Cementation:ITDCEM","PNC Infratech:PNCINFRA",
        "H.G. Infra:HGINFRA","Ashoka Buildcon:ASHOKA","IRB Infrastructure:IRB",
        "Ahluwalia Contracts:AHLUCONT","Dilip Buildcon:DBL","Rail Vikas Nigam:RVNL",
        "Texmaco Rail:TEXRAIL","Jupiter Wagons:JWL","Titagarh Rail:TITAGARH",
        "Mazagon Dock:MAZDOCK","Garden Reach Shipbuilders:GRSE","Cochin Shipyard:COCHINSHIP"
    ),
    "⚡ Energy & Power": _stocks(
        "Reliance Industries:RELIANCE","ONGC:ONGC","BPCL:BPCL","IOC:IOC","HPCL:HPCL",
        "GAIL India:GAIL","Petronet LNG:PETRONET","Castrol India:CASTROLIND","NTPC:NTPC",
        "Power Grid Corp:POWERGRID","Tata Power:TATAPOWER","Adani Green:ADANIGREEN",
        "Adani Enterprises:ADANIENT","JSW Energy:JSWENERGY","Torrent Power:TORNTPOWER",
        "NHPC:NHPC","SJVN:SJVN","CESC:CESC","Inox Wind:INOXWIND","Suzlon Energy:SUZLON",
        "IREDA:IREDA","PFC:PFC","REC:RECLTD","IGL:IGL","Gujarat Gas:GUJGASLTD",
        "Adani Total Gas:ATGL","Mahanagar Gas:MGL","Reliance Power:RPOWER",
        "Jaiprakash Power:JPPOWER","CPCL:CPCL","Mangalore Refinery:MRPL",
        "Chennai Petroleum:CHENNPETRO","GIPCL:GIPCL","Greenko:GKLENERGY",
        "Acme Solar:ACMESOLAR","Premier Energies:PREMIERENE"
    ),
    "🚗 Auto & Auto Ancillaries": _stocks(
        "Maruti Suzuki:MARUTI","Tata Motors:TATAMOTORS","M&M:M&M","Bajaj Auto:BAJAJ-AUTO",
        "Hero MotoCorp:HEROMOTOCO","Eicher Motors:EICHERMOT","TVS Motor:TVSMOTOR",
        "Ashok Leyland:ASHOKLEY","Force Motors:FORCEMOT","Apollo Tyres:APOLLOTYRE",
        "MRF:MRF","CEAT:CEATLTD","Balkrishna Industries:BALKRISIND","Bosch India:BOSCHLTD",
        "Motherson Sumi:MOTHERSON","Minda Industries:MINDAIND","Minda Corp:MINDACORP",
        "Suprajit Engineering:SUPRAJIT","Endurance Technologies:ENDURANCE",
        "Gabriel India:GABRIEL","Jamna Auto:JAMNAAUTO","Sona BLW Precision:SONACOMS",
        "Uno Minda:UNOMINDA","Fiem Industries:FIEMIND","Sandhar Technologies:SANDHAR",
        "Craftsman Automation:CRAFTSMAN","Bharat Forge:BHARATFORG","Schaeffler India:SCHAEFFLER",
        "Samvardhana Motherson:MOTHERSON","Varroc Engineering:VARROC","Pricol:PRICOL",
        "Lumax Industries:LUMAXIND","Lumax Auto Technologies:LUMAXTECH",
        "Spark Minda:MINDAIND","Automotive Axles:AUTOAXLES"
    ),
    "💊 Pharma & Healthcare": _stocks(
        "Sun Pharma:SUNPHARMA","Dr. Reddy's:DRREDDY","Cipla:CIPLA","Lupin:LUPIN",
        "Biocon:BIOCON","Alkem Labs:ALKEM","Torrent Pharma:TORNTPHARM",
        "Abbott India:ABBOTINDIA","Pfizer India:PFIZER","Sanofi India:SANOFI",
        "Divi's Laboratories:DIVISLAB","Aurobindo Pharma:AUROPHARMA",
        "Zydus Lifesciences:ZYDUSLIFE","Ipca Laboratories:IPCALAB","Natco Pharma:NATCOPHARM",
        "Glenmark Pharma:GLENMARK","Mankind Pharma:MANKIND","Ajanta Pharma:AJANTPHARM",
        "JB Chemicals:JBCHEPHARM","FDC Limited:FDC","Piramal Pharma:PPLPHARMA",
        "Laurus Labs:LAURUSLABS","Granules India:GRANULES","Aarti Drugs:AARTIDRUGS",
        "Caplin Point:CAPLIPOINT","Apollo Hospitals:APOLLOHOSP","Max Healthcare:MAXHEALTH",
        "Fortis Healthcare:FORTIS","Narayana Hrudayalaya:NH","Medanta:MEDANTA",
        "HCG Oncology:HCG","Vijaya Diagnostic:VIJAYA","Metropolis Healthcare:METROPOLIS",
        "Dr. Lal Path Labs:LALPATHLAB","Thyrocare:THYROCARE","Sanofi India:SANOFI",
        "Wockhardt:WOCKPHARMA","Strides Pharma:STAR","Suven Life Sciences:SUVEN",
        "Solara Active Pharma:SOLARA"
    ),
    "🏗️ Metals & Mining": _stocks(
        "Tata Steel:TATASTEEL","JSW Steel:JSWSTEEL","Hindalco:HINDALCO","Vedanta:VEDL",
        "Hindustan Zinc:HINDZINC","National Aluminium:NATIONALUM","SAIL:SAIL",
        "Coal India:COALINDIA","NMDC:NMDC","Jindal Steel:JINDALSTEL",
        "APL Apollo Tubes:APLAPOLLO","Ratnamani Metals:RATNAMANI",
        "Maharashtra Seamless:MAHSEAMLES","Welspun Corp:WELCORP","Shyam Metalics:SHYAMMETL",
        "Godawari Power:GPIL","GMDC:GMDC","MOIL:MOIL","Hindustan Copper:HINDCOPPER",
        "Tinplate Company:TINPLATE","Jindal Stainless:JSL","JSPL:JINDALPOLY",
        "Steel Authority:SAIL","Tata Metaliks:TATAMETALI","Maithan Alloys:MAITHANALL"
    ),
    "🧱 Cement & Construction": _stocks(
        "UltraTech Cement:ULTRACEMCO","Shree Cement:SHREECEM","Ambuja Cements:AMBUJACEM",
        "ACC:ACC","JK Cement:JKCEMENT","Dalmia Bharat:DALBHARAT","Ramco Cements:RAMCOCEM",
        "Heidelberg Cement:HEIDELBERG","JK Lakshmi Cement:JKLAKSHMI",
        "Birla Corporation:BIRLACORPN","Orient Cement:ORIENTCEM","India Cements:INDIACEM",
        "Sagar Cements:SAGCEM","Star Cement:STARCEMENT","NCL Industries:NCLIND",
        "Prism Johnson:PRSMJOHNSN","Kajaria Ceramics:KAJARIACER","CERA Sanitary:CERA",
        "Astral:ASTRAL","Supreme Industries:SUPREMEIND","Finolex Industries:FINPIPE",
        "Somany Ceramics:SOMANYCERA","Cello World:CELLO","Polyplex Corp:POLYPLEX"
    ),
    "🛒 FMCG & Consumer": _stocks(
        "Hindustan Unilever:HINDUNILVR","ITC:ITC","Nestle India:NESTLEIND",
        "Britannia:BRITANNIA","Dabur India:DABUR","Godrej Consumer:GODREJCP",
        "Marico:MARICO","Emami:EMAMILTD","Bajaj Consumer:BAJAJCON","Tata Consumer:TATACONSUM",
        "Varun Beverages:VBL","Radico Khaitan:RADICO","United Spirits:MCDOWELL-N",
        "United Breweries:UBL","Jubilant FoodWorks:JUBLFOOD","Westlife Foodworld:WESTLIFE",
        "Burger King India:BURGERKING","Devyani International:DEVYANI","Sapphire Foods:SAPPHIRE",
        "Mrs Bectors Food:BECTORFOOD","Heritage Foods:HERITGFOOD","Hatsun Agro:HATSUN",
        "Bikaji Foods:BIKAJI","P&G Hygiene:PGHH","Colgate Palmolive:COLPAL",
        "Kansai Nerolac:KANSAINER","Asian Paints:ASIANPAINT","Berger Paints:BERGEPAINT",
        "Indigo Paints:INDIGOPNTS","Pidilite:PIDILITIND","Prataap Snacks:PRATAAP",
        "DFM Foods:DFMFOODS","CCL Products:CCL"
    ),
    "🛍️ Retail & E-Commerce": _stocks(
        "Zomato:ZOMATO","Eternal (Zomato):ETERNAL","Swiggy:SWIGGY","Paytm:PAYTM",
        "Nykaa:NYKAA","PB Fintech:POLICYBZR","Delhivery:DELHIVERY",
        "Info Edge (Naukri):NAUKRI","IndiaMart:INDIAMART","Just Dial:JUSTDIAL",
        "Matrimony.com:MATRIMONY","CarTrade Tech:CARTRADE","Avenue Supermarts (DMart):DMART",
        "Trent:TRENT","V-Mart Retail:VMART","Bata India:BATAINDIA",
        "Relaxo Footwear:RELAXO","Campus Activewear:CAMPUS","Metro Brands:METROBRAND",
        "Shoppers Stop:SHOPERSTOP","Titan Company:TITAN","Kalyan Jewellers:KALYANKJIL",
        "Senco Gold:SENCO","PC Jeweller:PCJEWELLER","Thangamayil Jewellery:THANGAMAYL"
    ),
    "✈️ Infrastructure & Logistics": _stocks(
        "Adani Ports:ADANIPORTS","GMR Airports:GMRINFRA","IndiGo:INDIGO","SpiceJet:SPICEJET",
        "Blue Dart:BLUEDART","Container Corp:CONCOR","Gateway Distriparks:GDL",
        "Mahindra Logistics:MAHLOG","Delhivery:DELHIVERY","IRCTC:IRCTC","RITES:RITES",
        "IRFC:IRFC","Rail Vikas Nigam:RVNL","Adani Wilmar:AWL",
        "Interglobe Aviation:INDIGO","TCI Express:TCIEXP","Gati:GATI","VRL Logistics:VRLLOG",
        "Allcargo Logistics:ALLCARGO","Transport Corp:TCI","Navkar Corp:NAVKARCORP"
    ),
    "🔬 Chemicals & Fertilizers": _stocks(
        "UPL:UPL","PI Industries:PIIND","Coromandel Int.:COROMANDEL",
        "Bayer CropScience:BAYERCROP","Sumitomo Chemical:SUMICHEM","Rallis India:RALLIS",
        "Deepak Nitrite:DEEPAKNTR","Aarti Industries:AARTIIND","Navin Fluorine:NAVINFLUOR",
        "SRF Limited:SRF","Vinati Organics:VINATIORGA","Galaxy Surfactants:GALAXYSURF",
        "Fine Organics:FINEORG","Balaji Amines:BALAMINES","Alkyl Amines:ALKYLAMINE",
        "Neogen Chemicals:NEOGEN","Clean Science:CLEAN","Anupam Rasayan:ANURAS",
        "Tata Chemicals:TATACHEM","GHCL:GHCL","Gujarat Fluorochemicals:FLUOROCHEM",
        "Himadri Speciality:HSCL","Sudarshan Chemical:SUDARSCHEM","NOCIL:NOCIL",
        "Chambal Fertilisers:CHAMBLFERT","NFL:NFL","GSFC:GSFC","RCF:RCF","FACT:FACT",
        "Atul Ltd:ATUL","Rossari Biotech:ROSSARI","Tatva Chintan:TATVA",
        "Ami Organics:AMIORG","Archean Chemical:ARCHEAN"
    ),
    "🏠 Real Estate": _stocks(
        "Godrej Properties:GODREJPROP","DLF:DLF","Prestige Estates:PRESTIGE",
        "Brigade Enterprises:BRIGADE","Sobha:SOBHA","Oberoi Realty:OBEROIRLTY",
        "Macrotech (Lodha):LODHA","Mahindra Lifespace:MAHLIFE","Kolte Patil:KOLTEPATIL",
        "Puravankara:PURVA","DB Realty:DBREALTY","Indiabulls Real Estate:IBREALEST",
        "Embassy REIT:EMBASSY","Mindspace REIT:MINDSPACE","Brookfield REIT:BIRET",
        "Nexus Select Trust:NEXUSSELCT","Sunteck Realty:SUNTECK","Phoenix Mills:PHOENIXLTD",
        "Shriram Properties:SHRIRAMPPS","Signature Global:SIGNATURE"
    ),
    "📡 Telecom & Media": _stocks(
        "Bharti Airtel:BHARTIARTL","Vodafone Idea:IDEA","MTNL:MTNL",
        "Tata Communications:TATACOMM","Route Mobile:ROUTE","Tanla Platforms:TANLA",
        "Dish TV:DISHTV","Zee Entertainment:ZEEL","Sun TV Network:SUNTV",
        "PVR Inox:PVRINOX","Saregama India:SAREGAMA","Nazara Technologies:NAZARA",
        "Network18 Media:NETWORK18","TV18 Broadcast:TV18BRDCST","Hathway Cable:HATHWAY",
        "Den Networks:DEN","Indiacast Media:INDIACAST"
    ),
    "🧵 Textiles & Apparel": _stocks(
        "Page Industries:PAGEIND","Lux Industries:LUXIND","Dollar Industries:DOLLAR",
        "Trident:TRIDENT","Welspun India:WELSPUNIND","Raymond:RAYMOND","Arvind:ARVIND",
        "Vardhman Textiles:VTL","KPR Mill:KPRMILL","Siyaram Silk Mills:SIYARAM",
        "Nitin Spinners:NITINSPIN","Indo Count Industries:ICIL","Gokaldas Exports:GOKEX",
        "TCNS Clothing:TCNSBRANDS","Go Fashion:GOCOLORS","Monte Carlo:MONTECARLO",
        "Kewal Kiran:KKCL"
    ),
    "🔌 Electronics & Capital Equipment": _stocks(
        "Dixon Technologies:DIXON","Amber Enterprises:AMBER","Voltas:VOLTAS",
        "Blue Star:BLUESTARCO","Havells India:HAVELLS","Polycab India:POLYCAB",
        "KEI Industries:KEI","Finolex Cables:FINCABLES","V-Guard:VGUARD",
        "Crompton Greaves:CROMPTON","Orient Electric:ORIENTELEC","Bajaj Electricals:BAJAJELEC",
        "Whirlpool India:WHIRLPOOL","Kaynes Technology:KAYNES","Syrma SGS:SYRMA",
        "Elin Electronics:ELIN","Avalon Technologies:AVALON","CDSL:CDSL","BSE Ltd:BSE",
        "MCX India:MCX","Multi Comm Exchange:MCX","Genus Power:GENUSPOWER",
        "Apar Industries:APARINDS","Transformers & Rectifiers:TRIL"
    ),
    "🌾 Agriculture & Food": _stocks(
        "ITC (Agri):ITC","Kaveri Seed:KSCL","Dhanuka Agritech:DHANUKA",
        "Venky's India:VENKEYS","Avanti Feeds:AVANTIFEED","Waterbase:WATERBASE",
        "Heritage Foods:HERITGFOOD","CCL Products:CCL","Agro Tech Foods:AGROTECH",
        "Adani Wilmar:AWL","Patanjali Foods:PATANJALI","Krbl:KRBL","LT Foods:LTFOODS",
        "Triveni Engineering:TRIVENI","Balrampur Chini:BALRAMCHIN",
        "Dalmia Bharat Sugar:DALMIASUG","EID Parry:EIDPARRY","Bajaj Hindusthan:BAJAJHIND",
        "Shakti Pumps:SHAKTIPUMP","Jain Irrigation:JISLJALEQS"
    ),
    "🏛️ PSU & Defence": _stocks(
        "HAL:HAL","BEL:BEL","BEML:BEML","Mazagon Dock:MAZDOCK",
        "Garden Reach Shipbuilders:GRSE","Cochin Shipyard:COCHINSHIP","MTNL:MTNL",
        "Bharat Dynamics:BDL","Data Patterns:DATAPATTNS","Paras Defence:PARAS",
        "Solar Industries:SOLARINDS","Munitions India:MIL","GRSE:GRSE",
        "RVNL:RVNL","IRFC:IRFC","IREDA:IREDA","NHPC:NHPC","SJVN:SJVN","NTPC:NTPC",
        "PGCIL:POWERGRID","NMDC:NMDC","SAIL:SAIL","Coal India:COALINDIA","ONGC:ONGC",
        "IOC:IOC","BPCL:BPCL","HPCL:HPCL","GAIL India:GAIL"
    ),
}
ALL_STOCKS = {}
for sector, stocks in SECTORS.items():
    for name, sym in stocks:
        key = f"{name} ({sym})"
        if key not in ALL_STOCKS:
            ALL_STOCKS[key] = f"{sym}.NS"
REV_STOCKS = {v:k.split(" (")[0] for k,v in ALL_STOCKS.items()}
# dedup symbolsSYM2NAME = {}
for k,v in ALL_STOCKS.items():
    if v not in SYM2NAME:
        SYM2NAME[v] = k.split(" (")[0]

# ═══════════════════════════════════════════════════════════════════
# UI HELPERS
# ═══════════════════════════════════════════════════════════════════
def card(label, value, color="#ddeeff"):
    return f'<div class="glass-card"><p class="glass-label">{label}</p><div class="glass-value" style="color:{color};font-size:1.1rem;">{value}</div></div>'

def dark_fig(fig, h=400):
    fig.update_layout(
        height=h,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ddeeff", family="Space Mono", size=10),
        margin=dict(l=10,r=10,t=15,b=10),
    )
    fig.update_xaxes(gridcolor="rgba(0,200,255,0.04)")
    fig.update_yaxes(gridcolor="rgba(0,200,255,0.04)")
    return fig

def ist_now():
    return dt.datetime.now(IST)

def market_status():
    now = ist_now()
    if now.weekday() >= 5:
        return "🔴 NSE CLOSED", "#ff3355"
    ot = now.replace(hour=9, minute=15, second=0, microsecond=0)
    ct = now.replace(hour=15, minute=30, second=0, microsecond=0)
    if ot <= now <= ct:
        return "🟢 NSE OPEN", "#00e87a"
    return "🔴 NSE CLOSED", "#ff3355"

# ═══════════════════════════════════════════════════════════════════
# DATA LAYER — NORMALIZED + BATCHED
# ═══════════════════════════════════════════════════════════════════
def norm_yf(df):
    if df is None or df.empty:
        return None
    df = df.reset_index()
    # Ensure Date column exists
    if "Date" not in df.columns and "index" in df.columns:
        df = df.rename(columns={"index":"Date"})
    # Drop unnamed index columns if any
    df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed", regex=True)]
    # yfinance multi-ticker or flat quirks
    if isinstance(df.columns, pd.MultiIndex):
        # grab the first ticker block — caller extracts per ticker before norming
        df.columns = df.columns.get_level_values(0 if df.columns.names[0] is not None else 1)
    df.columns = [str(c).strip() for c in df.columns]
    cmap = {"Open":"Open","High":"High","Low":"Low","Close":"Close","Adj Close":"Close","Volume":"Volume"}
    keep = {c:cmap[c] for c in df.columns if c in cmap}
    df = df[list(keep.keys())].rename(columns=keep)
    for c in ["Open","High","Low","Close","Volume"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["Close","Date"])
    return df

@st.cache_data(ttl=3600, show_spinner=False)
def load_ohlcv(ticker, period="5y"):
    try:
        df = yf.download(ticker, period=period, interval="1d", auto_adjust=True, progress=False, timeout=14, threads=False)
        return norm_yf(df)
    except Exception:
        return None

@st.cache_data(ttl=1800, show_spinner=False)
def load_indices():
    tickers = ["^NSEI","^NSEBANK","^BSESN","^CRSMID","^CNXSC","^INDIAVIX"]
    results = {}
    for t in tickers:
        try:
            df = yf.download(t, period="5d", interval="1d", auto_adjust=True, progress=False, timeout=10, threads=False)
            results[t] = norm_yf(df)
        except Exception:
            pass
    return results

def download_batch(tickers, period="1y"):
    """Batch yfinance with modest chunking. More efficient + gentler than raw threads."""
    out = {}
    chunk_sz = 8
    for i in range(0, len(tickers), chunk_sz):
        chunk = tickers[i:i+chunk_sz]
        try:
            data = yf.download(
                chunk, period=period, interval="1d", auto_adjust=True,
                progress=False, group_by="ticker", threads=False, timeout=16
            )
            if data is None or data.empty:
                continue
            for t in chunk:
                try:
                    if isinstance(data.columns, pd.MultiIndex):
                        sub = data[t].copy()
                    else:
                        sub = data.copy()
                    sub = norm_yf(sub)
                    if sub is not None and len(sub) >= 40:
                        out[t] = sub
                except Exception:
                    continue
        except Exception:
            pass time.sleep(0.2)
    return out

# ═══════════════════════════════════════════════════════════════════
# ENGINE — VECTORIZED INDICATORS / SIGNALS / BACKTEST / FORECAST
# ═══════════════════════════════════════════════════════════════════
class Indicators:
    @staticmethod
    def apply(df: pd.DataFrame) -> pd.DataFrame:
        if len(df) < 20:
            return df
        c = df["Close"].astype(float)
        df["Return"] = c.pct_change()
        df["SMA_20"] = c.rolling(20).mean()
        df["SMA_50"] = c.rolling(50).mean()
        df["SMA_200"] = c.rolling(200).mean()
        df["EMA_12"] = c.ewm(span=12, adjust=False).mean()
        df["EMA_26"] = c.ewm(span=26, adjust=False).mean()
        df["MACD"] = df["EMA_12"] - df["EMA_26"]
        df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
        df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]
        bb_std = c.rolling(20).std()
        df["BB_Mid"] = df["SMA_20"]
        df["BB_Upper"] = df["BB_Mid"] + 2*bb_std
        df["BB_Lower"] = df["BB_Mid"] - 2*bb_std
        df["Volatility_20"] = df["Return"].rolling(20).std() * np.sqrt(252)
        d = c.diff()
        gain = d.clip(lower=0).rolling(14).mean()
        loss = (-d.clip(upper=0)).rolling(14).mean()
        df["RSI_14"] = 100 - (100 / (1 + gain/(loss+1e-9)))
        h = df["High"].astype(float)
        l = df["Low"].astype(float)
        hl = h - l
        hc = (h - c.shift()).abs()
        lc = (l - c.shift()).abs()
        df["ATR_14"] = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(14).mean()
        low14 = l.rolling(14).min()
        high14 = h.rolling(14).max()
        df["Stoch_K"] = (c - low14) / (high14 - low14 + 1e-9) * 100
        df["Stoch_D"] = df["Stoch_K"].rolling(3).mean()
        # OBV — vectorized
        if "Volume" in df.columns:
            vol = df["Volume"].astype(float).fillna(0)
            signed = vol * np.sign(c.diff())
            signed.iloc[0] = 0
            df["OBV"] = signed.cumsum()
        return df

class SignalEngine:
    @staticmethod
    def get(df: pd.DataFrame) -> str:
        if len(df) < 52:
            return "HOLD"
        last = df.iloc[-1]
        prev = df.iloc[-2]
        need = ["SMA_20","SMA_50","RSI_14","MACD","MACD_Signal"]
        if any(pd.isna(last.get(k, np.nan)) for k in need):
            return "HOLD"
        macd_up = float(last["MACD"]) > float(last["MACD_Signal"]) and float(prev["MACD"]) <= float(prev["MACD_Signal"])
        macd_dn = float(last["MACD"]) < float(last["MACD_Signal"]) and float(prev["MACD"]) >= float(prev["MACD_Signal"])
        trend_up = float(last["SMA_20"]) > float(last["SMA_50"])
        trend_dn = float(last["SMA_20"]) < float(last["SMA_50"])
        above_200 = pd.notna(last.get("SMA_200")) and float(last["Close"]) > float(last["SMA_200"])
        rsi = float(last["RSI_14"])
        if trend_up and above_200 and rsi < 70 and (macd_up or rsi < 45):
            return "BUY"
        if trend_dn and (rsi > 70 or macd_dn):
            return "SELL"
        return "HOLD"

    @staticmethod
    def strength(df: pd.DataFrame) -> int:
        if len(df) < 52:
            return 50
        last = df.iloc[-1]
        s = 50 try:
            rsi = float(last.get("RSI_14",50) or 50)
            if rsi < 30: s += 20
            elif rsi < 45: s += 10
            elif rsi > 70: s -= 20
            elif rsi > 60: s -= 10
            sma20 = float(last.get("SMA_20",0) or 0); sma50 = float(last.get("SMA_50",0) or 0)
            sma200 = float(last.get("SMA_200",0) or 0); cl = float(last.get("Close",0) or 0)
            if sma20 > sma50: s += 10
            else: s -= 10
            if cl > sma200: s += 10
            else: s -= 10
            mc = float(last.get("MACD",0) or 0); ms = float(last.get("MACD_Signal",0) or 0)
            if mc > ms: s += 10
            else: s -= 10
        except Exception:
            pass
        return max(0, min(100, s))

class BacktestEngine:
    STRATEGIES = ["SMA Crossover","RSI Mean Reversion","Bollinger Bands Breakout","MACD Crossover"]

    @staticmethod
    def run(df: pd.DataFrame, strategy: str):
        bt = df.copy().reset_index(drop=True)
        sig = pd.Series(0, index=bt.index)
        if strategy == "SMA Crossover":
            sig = (bt["SMA_20"] > bt["SMA_50"]).astype(int)
        elif strategy == "RSI Mean Reversion":
            sig = pd.Series(np.nan, index=bt.index)
            sig[bt["RSI_14"] < 30] = 1
            sig[bt["RSI_14"] > 70] = 0
            sig = sig.ffill().fillna(0)
        elif strategy == "Bollinger Bands Breakout":
            sig = pd.Series(np.nan, index=bt.index)
            sig[bt["Close"] > bt["BB_Upper"]] = 1
            sig[bt["Close"] < bt["BB_Lower"]] = 0
            sig = sig.ffill().fillna(0)
        elif strategy == "MACD Crossover":
            m = bt["MACD"]; ms = bt["MACD_Signal"]
            up = (m > ms) & (m.shift(1) <= ms.shift(1))
            dn = (m < ms) & (m.shift(1) >= ms.shift(1))
            sig = pd.Series(np.nan, index=bt.index)
            sig.loc[up] = 1
            sig.loc[dn] = 0
            sig = sig.ffill().fillna(0)
        bt["Signal_BT"] = sig.astype(int)
        bt["Position"] = bt["Signal_BT"].diff()
        # Next-day-open execution
        bt["NextOpen"] = bt["Open"].shift(-1)
        bt["NextHigh"] = bt["High"].shift(-1)
        bt["NextLow"] = bt["Low"].shift(-1)
        bt["NextDate"] = bt["Date"].shift(-1)
        trades = []
        buy_x, buy_y, sell_x, sell_y = [], [], [], []
        entry_q = []
        for i in range(len(bt)):
            if bt["Position"].iloc[i] == 1:
                entry_q.append(i)
            elif bt["Position"].iloc[i] == -1 and entry_q:
                ei = entry_q.pop(0)
                xi = i                # skip if next-bar doesn't exist
                if xi+1 >= len(bt) or ei+1 >= len(bt):
                    continue
                ed = bt["NextDate"].iloc[ei]
                xd = bt["NextDate"].iloc[xi]
                ep = float(bt["NextOpen"].iloc[ei])
                xp = float(bt["NextOpen"].iloc[xi])
                pnl = (xp - ep)/ep*100
                trades.append({
                    "Entry Date": str(ed)[:10], "Exit Date": str(xd)[:10],
                    "Entry ₹": round(ep,2), "Exit ₹": round(xp,2),
                    "P&L %": round(pnl,2), "Result": "✅ WIN" if pnl>0 else "❌ LOSS"
                })
                buy_x.append(ed)
                buy_y.append(float(bt["NextLow"].iloc[ei])*0.985 if pd.notna(bt["NextLow"].iloc[ei]) else ep)
                sell_x.append(xd)
                sell_y.append(float(bt["NextHigh"].iloc[xi])*1.015 if pd.notna(bt["NextHigh"].iloc[xi]) else xp)
        # metrics bt["Strat_Ret"] = bt["Signal_BT"].shift(1) * bt["Close"].astype(float).pct_change()
        bt["Equity"] = (1 + bt["Strat_Ret"].fillna(0)).cumprod()
        bt["BH"] = bt["Close"].astype(float)/float(bt["Close"].iloc[0])
        peak = bt["Equity"].cummax()
        dd = (bt["Equity"] - peak)/peak
        max_dd = abs(dd.min())*100 if len(dd)>0 else 0 rets = bt["Strat_Ret"].fillna(0)
        sharpe = float(rets.mean()/rets.std()*np.sqrt(252)) if rets.std()>0 else 0
        downside = rets[rets<0]
        sortino = float(rets.mean()*np.sqrt(252)/downside.std()) if len(downside)>0 and downside.std()>0 else 0
        ann_ret = (float(bt["Equity"].iloc[-1])**(252/max(len(bt),1))-1)*100
        bh_ret = (float(bt["BH"].iloc[-1])-1)*100
        # trade stats
        if trades:
            tdf = pd.DataFrame(trades)
            wins = (tdf["P&L %"]>0).sum(); total = len(tdf)
            wr = wins/total*100            gw = tdf[tdf["P&L %"]>0]["P&L %"].sum(); gl = abs(tdf[tdf["P&L %"]<0]["P&L %"].sum())
 pf = gw/gl if gl>0 else (999 if gw>0 else 0)
            avg_w = tdf[tdf["P&L %"]>0]["P&L %"].mean() if wins>0 else 0
            avg_l = tdf[tdf["P&L %"]<0]["P&L %"].mean() if (total-wins)>0 else 0
            exp = (wr/100)*avg_w + (1-wr/100)*avg_l if total>0 else 0
            calmar = ann_ret/max_dd if max_dd>0 else 0 best = tdf["P&L %"].max(); worst = tdf["P&L %"].min()
            metrics = {
                "WinRate":wr,"ProfitFactor":pf,"MaxDD":max_dd,"Sharpe":sharpe,"Sortino":sortino,
                "AnnRet":ann_ret,"Alpha":ann_ret-bh_ret,"AvgWin":avg_w,"AvgLoss":avg_l,
                "Expectancy":exp,"Calmar":calmar,"Best":best,"Worst":worst,"Total":total }
        else:
            metrics = {k:0 for k in ["WinRate","ProfitFactor","MaxDD","Sharpe","Sortino","AnnRet","Alpha","AvgWin","AvgLoss","Expectancy","Calmar","Best","Worst","Total"]}
        return bt, trades, metrics, buy_x, buy_y, sell_x, sell_y

class ForecastEngine:
    @staticmethod
    def holt_winters(series: pd.Series, steps: int=260):
        try:
            s = series.astype(float).dropna()
            m = ExponentialSmoothing(s, trend="add", seasonal=None, initialization_method="estimated").fit()
            return m.forecast(steps)
        except Exception:
            s = series.astype(float).dropna()
            drift = (float(s.iloc[-1]) - float(s.iloc[0]))/max(len(s),1)
            return pd.Series([float(s.iloc[-1]) + drift*i for i in range(1, steps+1)])

    @staticmethod
    def arima(series: pd.Series, steps: int=260):
        log_s = np.log(series.astype(float).dropna())
        pval = adfuller(log_s)[1]
        d = 0 if pval < 0.05 else 1
        best_aic, best_m, best_ord = np.inf, None, (1,d,1)
        for p in range(0,3):
            for q in range(0,3):
                try:
                    m = ARIMA(log_s, order=(p,d,q)).fit()
                    if m.aic < best_aic:
                        best_aic, best_m, best_ord = m.aic, m, (p,d,q)
                except Exception:
                    continue
        if best_m is None:
            best_m = ARIMA(log_s, order=(1,1,1)).fit()
            best_ord = (1,1,1)
            best_aic = best_m.aic
        fc = best_m.get_forecast(steps=steps)
        mu = fc.predicted_mean
        ci = fc.conf_int(alpha=0.10)
        return np.exp(mu), np.exp(ci.iloc[:,0]), np.exp(ci.iloc[:,1]), best_ord, round(best_aic,1)

    @staticmethod
    def accuracy(series: pd.Series, order: tuple, holdout: int=60):
        try:
            if len(series) < holdout + 80:
                return None, None
            train = series.iloc[:-holdout]
            test = series.iloc[-holdout:]
            log_train = np.log(train.astype(float).dropna())
            m = ARIMA(log_train, order=order).fit()
            fc_log = m.forecast(steps=holdout)
            fc = np.exp(fc_log.values)
            tv = test.values[:len(fc)]
            mape = float(np.mean(np.abs((tv - fc)/(tv+1e-9)))*100)
            dacc = float(np.mean(np.sign(np.diff(tv)) == np.sign(np.diff(fc)))*100) if len(tv)>1 else 50.0
            return round(mape,2), round(dacc,1)
        except Exception:
            return None, None

# ═══════════════════════════════════════════════════════════════════
# NEWS + SENTIMENT + SCRAPING# ═══════════════════════════════════════════════════════════════════
BULL_KW = {"surge","rally","grow","growth","jump","rise","gain","profit","record","bullish","beat","positive","expand","outperform","buy","upgrade","strong","boom","breakout","upside"}
BEAR_KW = {"slump","fall","decline","drop","loss","plunge","negative","bearish","miss","sell","downgrade","weak","crash","warn","crisis","debt","cut","lower","pressure","concern"}

@st.cache_data(ttl=900, show_spinner=False)
def fetch_news(ticker: str, company_name: str=""):
    clean = ticker.replace(".NS","").replace(".BO","")
    q = company_name.strip() if company_name.strip() else clean
    items = []
    try:
        gq = urllib.parse.quote(f"{q} stock NSE")
        gurl = f"https://news.google.com/rss/search?q={gq}&hl=en-IN&gl=IN&ceid=IN:en"
        req = urllib.request.Request(gurl, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            root = ET.fromstring(r.read())
        for item in root.findall(".//item")[:15]:
            title = (item.find("title").text or "") if item.find("title") is not None else ""
            link  = (item.find("link").text or "") if item.find("link") is not None else ""
            pub   = (item.find("pubDate").text or "") if item.find("pubDate") is not None else ""
            if title:
                items.append({"title":title,"link":link,"date":pub[:16]})
    except Exception:
        pass
    if items:
        return items
    try:
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={clean}&region=IN&lang=en-IN"
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as r:
            root = ET.fromstring(r.read())
        for item in root.findall(".//item"):
            title = (item.find("title").text or "") if item.find("title") is not None else ""
            link  = (item.find("link").text or "") if item.find("link") is not None else ""
            pub   = (item.find("pubDate").text or "") if item.find("pubDate") is not None else ""
            items.append({"title":title,"link":link,"date":pub[:16]})
        return items
    except Exception:
        return items

def sentiment_score(items):
    if not items:
        return 0.0, "NEUTRAL"
    tot = 0
    for it in items:
        tl = it["title"].lower(); words = set(tl.split())
        bull = len(words & BULL_KW); bear = len(words & BEAR_KW)
        for bw in BULL_KW:
            if f"not {bw}" in tl or f"no {bw}" in tl:
                bull -= 2
        tot += (bull - bear)
    avg = tot/len(items)
    cat = "BULLISH" if avg > 0.2 else "BEARISH" if avg < -0.2 else "NEUTRAL"
    return round(avg,3), cat

def _parse_ratio_li(html, label):
    li_pat = re.compile(
 r'<li[^>]*>\s*<span class="name">\s*(?:<a[^>]*>)?\s*' + re.escape(label) +
        r'\s*(?:</a>)?\s*</span>(.*?)</li>', re.IGNORECASE|re.DOTALL
    )
    m = li_pat.search(html)
    if not m:
        return None
    nums = re.findall(r'-?[\d]+(?:,\d{3})*(?:\.\d+)?', m.group(1))
    if not nums:
        return None
    try:
        return float(nums[-1].replace(",",""))
    except Exception:
        return None

def _sane(value, lo, hi):
    if value is None:
        return None
    return value if lo <= value <= hi else None

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_fundamentals(symbol: str):
    clean = symbol.replace(".NS","").replace(".BO","").upper()
    url = f"https://www.screener.in/company/{clean}/consolidated/"
    hdr = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    html = ""
    try:
        req = urllib.request.Request(url, headers=hdr)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")
    except Exception:
        try:
            url2 = f"https://www.screener.in/company/{clean}/"
            req2 = urllib.request.Request(url2, headers=hdr)
            with urllib.request.urlopen(req2, timeout=10) as r:
                html = r.read().decode("utf-8", errors="ignore")
            url = url2
        except Exception:
            return {}, url
    pe   = _sane(_parse_ratio_li(html,"Stock P/E"),0, 500)
    pb   = _sane(_parse_ratio_li(html,"Price to Book value"), 0, 100)
    roe  = _sane(_parse_ratio_li(html,"ROE"), -100, 100)
    roce = _sane(_parse_ratio_li(html,"ROCE"), -100, 100)
    de   = _sane(_parse_ratio_li(html,"Debt to equity"), 0, 20)
    prom = _sane(_parse_ratio_li(html,"Promoter holding"), 0, 100)
    eps  = _sane(_parse_ratio_li(html,"EPS"), -1000, 100000)
    dy   = _sane(_parse_ratio_li(html,"Dividend Yield"), 0, 25)
    return {
        "P/E Ratio":pe,"P/B Ratio":pb,"ROE (%)":roe,"ROCE (%)":roce,
        "Debt/Equity":de,"Promoter Hold%":prom,"EPS (TTM)":eps,"Div Yield (%)":dy
    }, url

def fetch_fii_dii():
    url = "https://www.nseindia.com/api/fiidiiTradeReact"
    hdr = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept":"application/json, text/plain, */*",
        "Referer":"https://www.nseindia.com/market-data/fii-dii-activity",
    }
    try:
        import http.cookiejar
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.open(urllib.request.Request("https://www.nseindia.com", headers=hdr), timeout=8)
        time.sleep(0.4)
        with opener.open(urllib.request.Request(url, headers=hdr), timeout=8) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None

def parse_fii_dii(data):
    if not data:
        return None, None
    try:
        rows = data if isinstance(data, list) else data.get("data", [])
 recs = []
        for row in rows[:20]:
            try:
                ds = row.get("date", row.get("Date",""))
                fb = float(str(row.get("fiiBuy", row.get("FII_BUY",0))).replace(",","") or 0)
                fs = float(str(row.get("fiiSell",row.get("FII_SELL",0))).replace(",","") or 0)
                db = float(str(row.get("diiBuy", row.get("DII_BUY",0))).replace(",","") or 0)
                ds_ = float(str(row.get("diiSell",row.get("DII_SELL",0))).replace(",","") or 0)
 recs.append({
                    "Date":ds,"FII Net":round(fb-fs,2),"DII Net":round(db-ds_,2),
                    "FII Buy":fb,"FII Sell":fs,"DII Buy":db,"DII Sell":ds_
                })
            except Exception:
                continue
        if not recs:
            return None, None
        df = pd.DataFrame(recs)
        return df, df.iloc[0] if len(df) else None
    except Exception:
        return None, None

def fetch_options_chain(symbol):
    clean = symbol.replace(".NS","").replace(".BO","").upper()
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={clean}"
    hdr = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept":"application/json, text/plain, */*",
        "Referer":f"https://www.nseindia.com/get-quotes/derivatives?symbol={clean}",
    }
    try:
        import http.cookiejar
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.open(urllib.request.Request("https://www.nseindia.com", headers=hdr), timeout=8)
        time.sleep(0.4)
        with opener.open(urllib.request.Request(url, headers=hdr), timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None

def parse_options_chain(data, spot):
    if not data:
        return None, None, None, None
    try:
        recs = data.get("records", {})
        eds = recs.get("expiryDates", [])
        nearest = eds[0] if eds else None
        rows = []
        for item in recs.get("data", []):
            if nearest and item.get("expiryDate") != nearest:
                continue
            strike = item.get("strikePrice", 0)
            ce = item.get("CE", {}); pe = item.get("PE", {})
            rows.append({
                "Strike":strike,
                "CE OI":ce.get("openInterest",0),"CE Chg OI":ce.get("changeinOpenInterest",0),
                "CE LTP":ce.get("lastPrice",0),"CE IV":ce.get("impliedVolatility",0),
                "PE OI":pe.get("openInterest",0),"PE Chg OI":pe.get("changeinOpenInterest",0),
                "PE LTP":pe.get("lastPrice",0),"PE IV":pe.get("impliedVolatility",0),
            })
        if not rows:
            return None, None, None, nearest
        df = pd.DataFrame(rows).sort_values("Strike")
        tc = df["CE OI"].sum(); tp = df["PE OI"].sum()
        pcr = round(tp/tc, 3) if tc>0 else None
        strikes = df["Strike"].values        pain = []
        for s in strikes:
            cp = sum(max(0, s-k)*o for k,o in zip(strikes, df["CE OI"].values))
            pp = sum(max(0, k-s)*o for k,o in zip(strikes, df["PE OI"].values))
            pain.append(cp+pp)
        mp = float(strikes[int(np.argmin(pain))])
        return df, pcr, mp, nearest
    except Exception:
        return None, None, None, None

# ═══════════════════════════════════════════════════════════════════
# HEADER + SEARCH
# ═══════════════════════════════════════════════════════════════════
def clear_search():
    st.session_state.search_query = ""

col_title, col_clock = st.columns([2,1])
with col_title:
    st.markdown('<h1 class="xerces-title">XERCES // QUANT ENGINE v2</h1>', unsafe_allow_html=True)
    st.markdown("<p class='telemetry-tag'>[ NSE/BSE UNIVERSE: 600+ STOCKS // ARIMA + TECHNICAL + PORTFOLIO ENGINE // GODMODE ]</p>", unsafe_allow_html=True)
with col_clock:
    n = ist_now(); ms, mc = market_status()
    st.markdown(f"""
<div style="text-align:right;font-family:'Space Mono',monospace;font-size:11px;color:#6a90aa;background:rgba(7,18,32,0.5);padding:8px;border-radius:4px;border:1px solid rgba(0,200,255,0.08);">
<div>CLOCK: <span style="color:#ffcc00;font-weight:bold;">{n.strftime('%H:%M:%S')} IST</span></div>
<div>DATE: <span style="color:#00c8ff;">{n.strftime('%d %b %Y')}</span></div>
<div style="margin-top:3px;color:{mc};font-weight:bold;">{ms}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<hr style='border-color:rgba(0,200,255,0.12);margin:0.65rem 0;'>", unsafe_allow_html=True)

st.markdown("<div style='background:rgba(7,18,32,0.45);border:1px solid rgba(0,200,255,0.12);padding:10px 16px;border-radius:6px;margin-bottom:12px;'>", unsafe_allow_html=True)
sc1, sc2 = st.columns([5,1])
with sc1:
    st.text_input("Search", placeholder="Search any NSE/BSE stock — name or symbol (e.g. Reliance, TCS, SBIN, INFY)...",
 label_visibility="collapsed", key="search_query")
    search_raw = st.session_state.search_query
with sc2:
    st.button("✕ Clear", on_click=clear_search, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Resolve ticker
search = search_raw.strip()
selected_ticker, selected_name, is_dashboard = "^NSEI", "NIFTY 50", True
if search:
    is_dashboard = False
    match_t, match_n = None, None
    sl = search.lower()
    for label, ticker in ALL_STOCKS.items():
        if sl in label.lower():
            match_t, match_n = ticker, label.split(" (")[0]; break
    if not match_t:
        for label, ticker in ALL_STOCKS.items():
            sym = ticker.replace(".NS","")
            if sl.upper() == sym or sl.upper() == ticker.upper():
                match_t, match_n = ticker, label.split(" (")[0]; break
    if match_t:
        selected_ticker, selected_name = match_t, match_n
    else:
        cand = search.upper()
        if not cand.endswith(".NS") and not cand.endswith(".BO") and "^" not in cand:
            cand = cand + ".NS"
        selected_ticker = cand
        selected_name = cand.replace(".NS","").replace(".BO","")

# ═══════════════════════════════════════════════════════════════════
# DASHBOARD LANDING
# ═══════════════════════════════════════════════════════════════════
if is_dashboard:
    st.markdown('<h2 class="xerces-title" style="font-size:1.5rem;margin-bottom:12px;">📊 LIVE MARKET OVERVIEW</h2>', unsafe_allow_html=True)
    with st.spinner("Loading market indices..."):
        idx_data = load_indices()
    META = [
        ("^NSEI","NIFTY 50","#00e87a"),("^NSEBANK","BANK NIFTY","#00c8ff"),
        ("^BSESN","SENSEX","#ffcc00"),("^CRSMID","NIFTY MIDCAP","#ff6b35"),
        ("^CNXSC","NIFTY SMALLCAP","#7c6ef8"),("^INDIAVIX","INDIA VIX","#ff3355"),
    ]
    cols = st.columns(6)
    for col, (sym, name, clr) in zip(cols, META):
        try:
            idf = idx_data.get(sym)
            if idf is None or len(idf) < 2:
                col.warning(name); continue
            cv = float(idf["Close"].iloc[-1]); pv = float(idf["Close"].iloc[-2])
            chg = (cv-pv)/pv*100
            flip = sym == "^INDIAVIX"
            cclr = ("#ff3355" if chg>=0 else "#00e87a") if flip else ("#00e87a" if chg>=0 else "#ff3355")
            ar = "▲" if chg>=0 else "▼"
            col.markdown(f'<div class="glass-card"><p class="glass-label" style="color:{clr};">{name}</p>'
 f'<div class="glass-value" style="font-size:1.1rem;">{cv:,.2f}</div>'
                         f'<p style="font-size:11px;color:{cclr};margin:2px 0;font-weight:600;">{ar} {abs(chg):.2f}%</p></div>', unsafe_allow_html=True)
        except Exception:
            col.warning(name)
    try:
        n50 = idx_data.get("^NSEI")
        if n50 is not None and not n50.empty:
            fig0 = go.Figure()
            fig0.add_trace(go.Scatter(x=n50["Date"], y=n50["Close"], line=dict(color="#00e87a",width=2), name="Nifty 50", fill="tozeroy", fillcolor="rgba(0,232,122,0.04)"))
            dark_fig(fig0, 280)
            fig0.update_layout(showlegend=False, yaxis=dict(tickprefix="₹"))
            st.plotly_chart(fig0, use_container_width=True)
    except Exception:
        pass
    st.markdown("""<div class="glass-card" style="margin-top:10px;">
<p class="section-header" style="margin-top:0;">💡 How to use XERCES v2</p>
<p style="font-size:12px;color:#a0aec0;line-height:1.7;margin:0;">
Search any NSE/BSE stock above. You'll get live technical charts with overlays, MACD/RSI/Bollinger, instant Holt-Winters forecast (opt-in ARIMA),
multi-strategy backtesting with Sortino & Calmar, batch scanner with batched downloads, MPT portfolio optimizer + correlation heatmap,
FII/DII & options with CSV fallbacks, news sentiment, and full risk calculator.
</p></div>""", unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════════════════════════════
with st.spinner(f"Loading {selected_name} ({selected_ticker})..."):
    raw_df = load_ohlcv(selected_ticker, period="5y")
if raw_df is None or len(raw_df) < 60:
    st.error(f"❌ Could not load data for **{selected_ticker}**.")
    if selected_ticker.endswith(".NS"):
        st.info("Try the BSE suffix: type `SYMBOL.BO` in search.")
    else:
        st.info("For NSE append `.NS` (e.g. RELIANCE.NS). For BSE append `.BO`.")
    st.stop()

df = Indicators.apply(raw_df)
df = df.reset_index(drop=True)
last = df.iloc[-1]; prev = df.iloc[-2]
close = float(last["Close"]); chg1d = (close - float(prev["Close"]))/float(prev["Close"])*100
hi52 = float(df["Close"].iloc[-252:].max()) if len(df)>=252 else float(df["Close"].max())
lo52 = float(df["Close"].iloc[-252:].min()) if len(df)>=252 else float(df["Close"].min())
rsi_val = float(last["RSI_14"]) if pd.notna(last.get("RSI_14")) else 50.0
atr_val = float(last["ATR_14"]) if pd.notna(last.get("ATR_14")) else close*0.02
vol20 = float(last.get("Volatility_20") or 0)
macd_v = float(last.get("MACD") or 0); macd_sv = float(last.get("MACD_Signal") or 0)
signal = SignalEngine.get(df); strength = SignalEngine.strength(df)
st.session_state.last_data_tick = ist_now().strftime("%H:%M:%S")

# ═══════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<p class='telemetry-tag' style='color:#00c8ff;font-weight:700;'>[ 🛡️ RISK CONTROLS ]</p>", unsafe_allow_html=True)
    allocated_capital = st.number_input("Capital Pool (₹)", min_value=1000, value=100000, step=5000)
    risk_per_trade = st.slider("Risk per Trade (%)", 0.5, 5.0, 1.5, step=0.1)
    risk_reward = st.slider("Risk:Reward (1:X)", 1.5, 4.0, 2.0, step=0.5)
    st.markdown("---")
    st.markdown("<p class='telemetry-tag' style='color:#00c8ff;font-weight:700;'>[ 📎 COMPARE ]</p>", unsafe_allow_html=True)
    compare_sel = st.multiselect("Overlay normalized price (2 max)", list(ALL_STOCKS.keys()), default=[], max_selections=2, key="compare_sel")
    st.markdown("---")
    st.markdown("<p class='telemetry-tag' style='color:#00c8ff;font-weight:700;'>[ ⚙️ CHART SETTINGS ]</p>", unsafe_allow_html=True)
    show_bb = st.checkbox("Bollinger Bands", value=True); show_sma = st.checkbox("SMA 20/50/200", value=True)
    show_vol = st.checkbox("Volume bars", value=True)
    st.markdown("---")
    st.markdown("<p class='telemetry-tag' style='color:#00c8ff;font-weight:700;'>[ 📈 BACKTEST STRATEGY ]</p>", unsafe_allow_html=True)
    backtest_strategy = st.selectbox("Strategy", BacktestEngine.STRATEGIES)
    st.markdown("---")
    st.caption("⚠️ Not SEBI registered. Statistical analysis only. Not financial advice.")

sl_price = close - atr_val*1.5
tp_price = close + atr_val*1.5*risk_reward

# KPIs
k1,k2,k3,k4,k5,k6,k7 = st.columns(7)
sig_clr = {"BUY":"#00e87a","SELL":"#ff3355","HOLD":"#ffcc00"}[signal]
chg_clr = "#00e87a" if chg1d>=0 else "#ff3355"
str_clr = "#00e87a" if strength>=65 else "#ff3355" if strength<=35 else "#ffcc00"
for col,lbl,val,clr in zip(
 [k1,k2,k3,k4,k5,k6,k7],
    ["Last Close","1D Change","52W High","52W Low","RSI (14)","Signal","Strength"],
    [f"₹{close:,.2f}",f"{'▲' if chg1d>=0 else '▼'} {abs(chg1d):.2f}%",f"₹{hi52:,.2f}",f"₹{lo52:,.2f}",f"{rsi_val:.1f}",signal,f"{strength}/100"],
    ["#ddeeff",chg_clr,"#ddeeff","#ddeeff", "#ff3355" if rsi_val>70 else "#00e87a" if rsi_val<30 else "#00c8ff", sig_clr, str_clr]
):
    col.markdown(card(lbl,val,clr), unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════
tabs = st.tabs(["📊 CHART","🔮 FORECAST","📈 BACKTEST","📡 SCANNER","🛡️ RISK","💼 PORTFOLIO","📊 FII/DII","🎯 OPTIONS","📋 FUNDAMENTALS","📰 NEWS","❓ MANUAL"])

# ── TAB: CHART ────────────────────────────────────────────────────
with tabs[0]:
    rows = 4 if show_vol else 3
    rh = [0.48,0.18,0.18,0.16] if show_vol else [0.56,0.22,0.22]
    titles = ["Price + Indicators","RSI (14)","MACD"] + (["Volume"] if show_vol else [])
    specs = [[{"secondary_y":True}]] + [[{"secondary_y":False}]]*(rows-1)
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, row_heights=rh,
                        vertical_spacing=0.025, subplot_titles=titles, specs=specs)
    fig.add_trace(go.Candlestick(
        x=df["Date"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name="OHLC", increasing_line_color="#00e87a", decreasing_line_color="#ff3355",
        increasing_fillcolor="rgba(0,232,122,0.25)", decreasing_fillcolor="rgba(255,51,85,0.25)"
    ), row=1, col=1, secondary_y=False)
    if show_sma:
        for cn,clr,dsh in [("SMA_20","#00c8ff","dot"),("SMA_50","#ffcc00","dash"),("SMA_200","#ff6b35","solid")]:
            if cn in df.columns:
                fig.add_trace(go.Scatter(x=df["Date"], y=df[cn], name=cn.replace("_"," "), line=dict(color=clr,width=1.2,dash=dsh), opacity=0.85), row=1, col=1, secondary_y=False)
    if show_bb and "BB_Upper" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_Upper"], name="BB Upper", line=dict(color="rgba(124,78,255,0.5)",width=1,dash="dot")), row=1,col=1,secondary_y=False)
        fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_Lower"], name="BB Lower", line=dict(color="rgba(124,78,255,0.5)",width=1,dash="dot"), fill="tonexty", fillcolor="rgba(124,78,255,0.04)"), row=1,col=1,secondary_y=False)
    fig.add_hline(y=sl_price, line_dash="dash", line_color="rgba(255,51,85,0.6)", annotation_text=f"SL ₹{sl_price:,.0f}", row=1,col=1,secondary_y=False)
    fig.add_hline(y=tp_price, line_dash="dash", line_color="rgba(0,232,122,0.6)", annotation_text=f"TP ₹{tp_price:,.0f}", row=1,col=1,secondary_y=False)
    # Compare overlay on secondary_y
    for key in compare_sel:
        tk = ALL_STOCKS[key]
        cdf = load_ohlcv(tk, period="1y")
        if cdf is not None and not cdf.empty:
            norm = cdf["Close"]/cdf["Close"].iloc[0]*100
            fig.add_trace(go.Scatter(x=cdf["Date"], y=norm, name=key.split(" (")[0], opacity=0.45, line=dict(width=1)), row=1, col=1, secondary_y=True)
    # Backtest markers (reuse backtest results lazily if already computed)
    if "bt_markers" in st.session_state:
        mx = st.session_state.bt_markers
        if mx["buy_x"]:
            fig.add_trace(go.Scatter(x=mx["buy_x"], y=mx["buy_y"], mode="markers", name="Buy Entry",
                marker=dict(symbol="triangle-up", size=9, color="#00e87a", line=dict(width=1,color="#020813"))), row=1, col=1, secondary_y=False)
        if mx["sell_x"]:
            fig.add_trace(go.Scatter(x=mx["sell_x"], y=mx["sell_y"], mode="markers", name="Sell Exit",
                marker=dict(symbol="triangle-down", size=9, color="#ff3355", line=dict(width=1,color="#020813")))), row=1, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI_14"], name="RSI 14", line=dict(color="#00c8ff",width=1.5)), row=2, col=1)
    for lvl,lc in [(70,"rgba(255,51,85,0.4)"),(30,"rgba(0,232,122,0.4)"),(50,"rgba(255,255,255,0.08)")]:
        fig.add_hline(y=lvl, line_dash="dot", line_color=lc, row=2, col=1)
    mc = ["#00e87a" if v>=0 else "#ff3355" for v in df["MACD_Hist"].fillna(0)]
    fig.add_trace(go.Bar(x=df["Date"], y=df["MACD_Hist"], name="MACD Hist", marker_color=mc, opacity=0.7), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["MACD"], name="MACD", line=dict(color="#00c8ff",width=1.2)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["MACD_Signal"], name="Signal", line=dict(color="#ffcc00",width=1.2,dash="dot")), row=3, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.1)", row=3, col=1)
    if show_vol and "Volume" in df.columns:
        vc = ["rgba(0,232,122,0.4)" if r["Close"]>=r["Open"] else "rgba(255,51,85,0.4)" for _,r in df.iterrows()]
        fig.add_trace(go.Bar(x=df["Date"], y=df["Volume"], name="Volume", marker_color=vc), row=4, col=1)
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_layout(legend=dict(bgcolor="rgba(7,18,32,0.5)",bordercolor="rgba(0,200,255,0.15)",borderwidth=1,font=dict(size=9)))
    dark_fig(fig, 780)
    st.plotly_chart(fig, use_container_width=True)
    # Signal panel
    ls, rs = st.columns([1,2])
    with ls:
        st.markdown(f'<div class="glass-card" style="text-align:center;"><p class="glass-label">Signal</p>'
 f'<div class="signal-{"buy" if signal=="BUY" else "sell" if signal=="SELL" else "hold"}">{signal}</div>'
                    f'<div style="background:rgba(255,255,255,0.05);border-radius:4px;height:6px;margin:8px 0;">'
                    f'<div style="width:{strength}%;height:6px;border-radius:4px;background:{str_clr};"></div></div>'
                    f'<p style="font-size:10px;color:#6a90aa;margin:0;">Strength {strength}/100</p></div>', unsafe_allow_html=True)
    with rs:
        bb_pct = ""
        if pd.notna(last.get("BB_Upper")) and pd.notna(last.get("BB_Lower")):
            rng = float(last["BB_Upper"])-float(last["BB_Lower"])
            bb_pct = f"{(close-float(last['BB_Lower']))/rng*100:.0f}%" if rng>0 else "—"
        sk = float(last.get("Stoch_K",50) or 50)
        st.markdown(f'<div class="glass-card"><p class="glass-label">Readings</p>'
                    f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-top:6px;font-size:11px;font-family:"Space Mono",monospace;">'
                    f'<div>RSI: <span style="color:{"#ff3355" if rsi_val>70 else "#00e87a" if rsi_val<30 else "#00c8ff"}">{rsi_val:.1f}</span></div>'
                    f'<div>MACD: <span style="color:{"#00e87a" if macd_v>macd_sv else "#ff3355"}">{macd_v:.2f}</span></div>'
                    f'<div>ATR(14): <span style="color:#ffcc00;">₹{atr_val:.2f}</span></div>'
                    f'<div>Stoch %K: <span style="color:{"#ff3355" if sk>80 else "#00e87a" if sk<20 else "#ddeeff"}">{sk:.0f}</span></div>'
                    f'<div>BB Pos: <span style="color:#7c4dff;">{bb_pct}</span></div>'
                    f'<div>Volatility: <span style="color:#ddeeff;">{vol20:.1%}</span></div>'
                    f'<div>SMA 200: <span style="color:#ff6b35;">₹{float(last.get("SMA_200",0) or 0):,.0f}</span></div>'
                    f'<div>SMA 50: <span style="color:#ffcc00;">₹{float(last.get("SMA_50",0) or 0):,.0f}</span></div>'
                    f'<div>SMA 20: <span style="color:#00c8ff;">₹{float(last.get("SMA_20",0) or 0):,.0f}</span></div>'
                    f'</div></div>', unsafe_allow_html=True)

# ── TAB: FORECAST ─────────────────────────────────────────────────
with tabs[1]:
    st.markdown(f'<p class="section-header">[ 🔮 FORECAST — {selected_name} → JUNE 2027 ]</p>', unsafe_allow_html=True)
    price_series = df["Close"].astype(float)
 ld = pd.to_datetime(df["Date"].iloc[-1])
    target_end = pd.Timestamp("2027-06-30")
    fc_dates = pd.bdate_range(start=ld+pd.Timedelta(days=1), end=target_end)
    steps = len(fc_dates)
    if steps <= 0:
        st.warning("Data already extends past June 2027.")
    else:
        # Always fast ETS
        hw_vals = ForecastEngine.holt_winters(price_series, steps)
        hw_s = pd.Series(hw_vals.values, index=fc_dates)
        run_deep = st.checkbox("Run Deep ARIMA (16-model AIC grid) — slower", value=False)
        fc_s = None; ci_lo = None; ci_hi = None; aic_val = None; arima_order = None; mape = None; dacc = None
        if run_deep:
            with st.spinner("Fitting ARIMA + 60-day validation..."):
                fc_mean, fc_lo, fc_hi, arima_order, aic_val = ForecastEngine.arima(price_series, steps)
                fc_s = pd.Series(fc_mean.values, index=fc_dates)
                ci_lo = pd.Series(fc_lo.values, index=fc_dates)
                ci_hi = pd.Series(fc_hi.values, index=fc_dates)
                mape, dacc = ForecastEngine.accuracy(price_series, arima_order, holdout=60)
        # Show metrics row
        arr = []
        if fc_s is not None:
            ta = float(fc_s.iloc[-1]); ua = (ta-close)/close*100
            arr.append(("ARIMA Jun '27", f"₹{ta:,.0f} ({'▲' if ua>=0 else '▼'}{abs(ua):.1f}%)", "#fbbf24"))
        thw = float(hw_s.iloc[-1]); uhw = (thw-close)/close*100
        arr += [
            ("Current Price", f"₹{close:,.2f}", "#ddeeff"),
            ("Holt-Winters Jun '27", f"₹{thw:,.0f} ({'▲' if uhw>=0 else '▼'}{abs(uhw):.1f}%)", "#00c8ff"),
        ]
        if fc_s is not None:
            cons = (ta+thw)/2; uc = (cons-close)/close*100
            arr.append(("Consensus Target", f"₹{cons:,.0f} ({'▲' if uc>=0 else '▼'}{abs(uc):.1f}%)", "#00e87a"))
            arr.append(("Model", f"ARIMA{arima_order}", "#ff6b35"))
        ccols = st.columns(len(arr))
        for col, (lbl,val,clr) in zip(ccols, arr):
            col.markdown(card(lbl,val,clr), unsafe_allow_html=True)
        if run_deep and mape is not None:
            am1,am2,am3 = st.columns(3)
            mape_clr = "#00e87a" if mape<5 else "#ffcc00" if mape<10 else "#ff3355"
            dacc_clr = "#00e87a" if dacc>60 else "#ffcc00" if dacc>50 else "#ff3355"
            am1.markdown(card("60-Day MAPE",f"{mape:.2f}%",mape_clr), unsafe_allow_html=True)
            am2.markdown(card("Directional Accuracy",f"{dacc:.0f}%",dacc_clr), unsafe_allow_html=True)
            am3.markdown(card("AIC Score",str(aic_val),"#7c4dff"), unsafe_allow_html=True)
        # Chart fig2 = go.Figure()
        hp = price_series.iloc[-504:]
        hd = pd.to_datetime(df["Date"].iloc[-504:])
        fig2.add_trace(go.Scatter(x=hd, y=hp.values, name="Historical (2yr)", line=dict(color="#7c6ef8",width=1.8)))
        if fc_s is not None:
            fig2.add_trace(go.Scatter(x=fc_s.index, y=fc_s.values, name="ARIMA", line=dict(color="#f97316",width=2,dash="dash")))
            fig2.add_trace(go.Scatter(x=list(ci_hi.index)+list(ci_lo.index[::-1]), y=list(ci_hi.values)+list(ci_lo.values[::-1]),
                fill="toself", fillcolor="rgba(249,115,22,0.08)", line=dict(color="rgba(0,0,0,0)"), name="ARIMA 90% CI"))
        fig2.add_trace(go.Scatter(x=hw_s.index, y=hw_s.values, name="Holt-Winters", line=dict(color="#00c8ff",width=1.5,dash="dashdot")))
        if fc_s is not None:
            cons = (fc_s+hw_s)/2
            fig2.add_trace(go.Scatter(x=cons.index, y=cons.values, name="Consensus", line=dict(color="#00e87a",width=1.5,dash="longdash")))
        fig2.add_vline(x=str(ld), line_dash="dot", line_color="rgba(100,100,100,0.4)")
        dark_fig(fig2, 440); fig2.update_layout(yaxis=dict(tickprefix="₹"))
 st.plotly_chart(fig2, use_container_width=True)
        # Monthly table
        if fc_s is not None:
            tdf = pd.DataFrame({"Forecast":fc_s,"HW":hw_s,"CI_Lo":ci_lo,"CI_Hi":ci_hi})
        else:
            tdf = pd.DataFrame({"HW":hw_s})
            tdf["Forecast"] = np.nan; tdf["CI_Lo"]=np.nan; tdf["CI_Hi"]=np.nan
        tdf["Month"] = tdf.index.to_period("M")
        mon = tdf.groupby("Month").agg(
            Forecast=("Forecast","last"), HW=("HW","last"),
            CI_Lo=("CI_Lo","last"), CI_Hi=("CI_Hi","last")
        ).reset_index()
        mon["Month_str"] = mon["Month"].dt.strftime("%b %Y")
        use_col = "Forecast" if fc_s is not None else "HW"
        mon["MoM_pct"] = mon[use_col].pct_change()*100
        mon.loc[0,"MoM_pct"] = (mon.loc[0,use_col]-close)/close*100
        st.markdown('<p class="section-header">[ MONTH-BY-MONTH TARGETS ]</p>', unsafe_allow_html=True)
        for i in range(0, len(mon), 6):
            chunk = mon.iloc[i:i+6]; ccols = st.columns(len(chunk))
            for col, (_,row) in zip(ccols, chunk.iterrows()):
                chg = row["MoM_pct"]; arrow = "▲" if chg>=0 else "▼"; clr = "#00e87a" if chg>=0 else "#ff3355"
                col.markdown(f'<div style="background:rgba(7,18,32,0.65);border:1px solid rgba(0,200,255,0.15);border-radius:6px;padding:9px 7px;text-align:center;margin-bottom:6px;">'
                             f'<div style="font-size:9px;font-family:Space Mono;color:#6a90aa;">{row["Month_str"]}</div>'
                             f'<div style="font-family:Orbitron;font-size:.95rem;font-weight:700;color:#fbbf24;margin:3px 0;">₹{row[use_col]:,.0f}</div>'
                             f'<div style="font-size:9px;color:{clr};font-weight:600;">{arrow} {abs(chg):.1f}%</div>'
                             f'<div style="font-size:8px;color:rgba(100,120,140,0.5);">₹{row["CI_Lo"]:,.0f}–₹{row["CI_Hi"]:,.0f}</div></div>', unsafe_allow_html=True)
        tbl = mon[["Month_str",use_col,"HW","CI_Lo","CI_Hi","MoM_pct"]].round(2)
        tbl.columns = ["Month","Target ₹","Holt-Winters ₹","Lower ₹","Upper ₹","MoM %"]
        st.download_button("⬇️ Download Forecast CSV", tbl.to_csv(index=False).encode(), f"{selected_name}_forecast.csv", "text/csv")

# ── TAB: BACKTEST ─────────────────────────────────────────────────
with tabs[2]:
    st.markdown(f'<p class="section-header">[ BACKTEST: {backtest_strategy.upper()} — {selected_name} ]</p>', unsafe_allow_html=True)
    bt_df, trades, metrics, buy_x, buy_y, sell_x, sell_y = BacktestEngine.run(df, backtest_strategy)
    st.session_state.bt_markers = {"buy_x":buy_x,"buy_y":buy_y,"sell_x":sell_x,"sell_y":sell_y}
    if metrics["Total"]>0:
        b1,b2,b3,b4,b5,b6 = st.columns(6)
        items = [
            ("Win Rate",f"{metrics['WinRate']:.1f}%","#00e87a"),
            ("Profit Factor",f"{metrics['ProfitFactor']:.2f}","#00e87a" if metrics['ProfitFactor']>=1.5 else "#ffcc00" if metrics['ProfitFactor']>=1 else "#ff3355"),
            ("Max Drawdown",f"-{metrics['MaxDD']:.1f}%","#ff3355"),
            ("Sharpe",f"{metrics['Sharpe']:.2f}","#00c8ff"),
            ("Ann. Return",f"{metrics['AnnRet']:+.1f}%","#00e87a" if metrics['AnnRet']>0 else "#ff3355"),
            ("Alpha vs B&H",f"{metrics['Alpha']:+.1f}%","#00e87a" if metrics['Alpha']>0 else "#ff3355"),
        ]
        for col, (lbl,val,clr) in zip([b1,b2,b3,b4,b5,b6], items):
            col.markdown(card(lbl,val,clr), unsafe_allow_html=True)
        st.markdown('<p class="section-header">[ EXTENDED METRICS ]</p>', unsafe_allow_html=True)
        ex1,ex2,ex3,ex4,ex5,ex6 = st.columns(6)
        ex_items = [
            ("Sortino",f"{metrics['Sortino']:.2f}","#00c8ff"),
            ("Calmar",f"{metrics['Calmar']:.2f}","#00c8ff"),
            ("Expectancy",f"{metrics['Expectancy']:.2f}%","#ffcc00"),
            ("Avg Win",f"{metrics['AvgWin']:.2f}%","#00e87a"),
            ("Avg Loss",f"{metrics['AvgLoss']:.2f}%","#ff3355"),
            ("Best / Worst",f"{metrics['Best']:.1f}% / {metrics['Worst']:.1f}%","#ddeeff"),
        ]
        for col, (lbl,val,clr) in zip([ex1,ex2,ex3,ex4,ex5,ex6], ex_items):
            col.markdown(card(lbl,val,clr), unsafe_allow_html=True)
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=bt_df["Date"], y=bt_df["Equity"]*100, name="Strategy", line=dict(color="#00e87a",width=2)))
        fig3.add_trace(go.Scatter(x=bt_df["Date"], y=bt_df["BH"]*100, name="Buy & Hold", line=dict(color="#7c6ef8",width=1.5,dash="dot")))
        dark_fig(fig3, 280); fig3.update_layout(yaxis=dict(ticksuffix="%"))
        st.plotly_chart(fig3, use_container_width=True)
        if trades:
            tdf = pd.DataFrame(trades)
            st.markdown('<p class="section-header">[ TRADE LOG — LAST 30 ]</p>', unsafe_allow_html=True)
            st.dataframe(tdf.tail(30), use_container_width=True, hide_index=True)
            st.download_button("⬇️ Download Trade Log", tdf.to_csv(index=False).encode(), f"{selected_name}_trades.csv", "text/csv")
    else:
        st.info("No signals generated. Try a different stock or strategy.")

# ── TAB: SCANNER ──────────────────────────────────────────────────
with tabs[3]:
    st.markdown('<p class="section-header">[ MULTI-STOCK BULK SCANNER ]</p>', unsafe_allow_html=True)
    def_sec = next((k for k in SECTORS if "Banking" in k), list(SECTORS.keys())[0])
    scan_sectors = st.multiselect("Sectors", list(SECTORS.keys()), default=[def_sec])
    max_stocks = st.slider("Max stocks", 10, 80, 20, step=5)
    if st.button("RUN SCAN", use_container_width=True):
        pool = []
        for sec in scan_sectors:
            for _,sym in SECTORS.get(sec, []):
                t = f"{sym}.NS"
                if t not in pool:
                    pool.append(t)
        pool = pool[:max_stocks]
        prog = st.progress(0, text="Downloading batch data…")
        batch_data = download_batch(pool, period="1y")
        prog.empty()
        results = []
        for tk, sd in batch_data.items():
            try:
                sd = Indicators.apply(sd)
                nm = SYM2NAME.get(tk, tk.replace(".NS",""))
                sig = SignalEngine.get(sd)
                ls = sd.iloc[-1]; ps = sd.iloc[-2]
                cp = float(ls["Close"])
                ch = (cp - float(ps["Close"]))/float(ps["Close"])*100
                atr = float(ls["ATR_14"]) if pd.notna(ls.get("ATR_14")) else cp*0.02
                sl = cp - atr*1.5                tp = cp + atr*1.5*risk_reward
                qty = max(1, int(allocated_capital*(risk_per_trade/100)/(atr*1.5)))
                rsi = float(ls["RSI_14"]) if pd.notna(ls.get("RSI_14")) else 50.0
                stn = SignalEngine.strength(sd)
                results.append({
                    "Stock":nm,"Ticker":tk.replace(".NS",""),
                    "Price":f"₹{cp:,.2f}","1D%":f"{ch:+.2f}","RSI":f"{rsi:.1f}",
                    "Signal":sig,"Strength":stn,"SL":f"₹{sl:,.2f}","Target":f"₹{tp:,.2f}","Qty":qty,
 "_sig":sig,"_str":stn
 })
            except Exception:
                continue
        st.session_state.scan_results = results
        st.session_state.scan_done = True
    if st.session_state.get("scan_results"):
        rdf = pd.DataFrame(st.session_state.scan_results)
        filt = st.radio("Filter", ["All","BUY","SELL","HOLD","High Strength (>=65)"], horizontal=True)
        if filt=="BUY": rdf = rdf[rdf["_sig"]=="BUY"]
        elif filt=="SELL": rdf = rdf[rdf["_sig"]=="SELL"]
        elif filt=="HOLD": rdf = rdf[rdf["_sig"]=="HOLD"]
        elif "High" in filt: rdf = rdf[rdf["_str"]>=65]
        disp = rdf.drop(columns=["_sig","_str"], errors="ignore")
        st.dataframe(disp, use_container_width=True, hide_index=True)
        b=(rdf["_sig"]=="BUY").sum(); s=(rdf["_sig"]=="SELL").sum(); h=(rdf["_sig"]=="HOLD").sum()
        tot = b+s+h; br = round(b/tot*100,1) if tot>0 else 0
        st.caption(f"{len(disp)} stocks | BUY {b} | SELL {s} | HOLD {h} | Breadth {br}% bullish")
    else:
        st.info("Click RUN SCAN to populate.")

# ── TAB: RISK ───────────────────────────────────────────────────────
with tabs[4]:
    st.markdown(f'<p class="section-header">[ RISK CALCULATOR — {selected_name} ]</p>', unsafe_allow_html=True)
    r1,r2 = st.columns(2)
    with r1:
        entry_px = st.number_input("Entry Price", value=round(close,2), step=1.0)
        stop_px = st.number_input("Stop Loss", value=round(sl_price,2), step=1.0)
        target_px = st.number_input("Take Profit", value=round(tp_price,2), step=1.0)
    with r2:
        cap2 = st.number_input("Capital", value=float(allocated_capital), step=1000.0)
        risk_pct2 = st.slider("Risk %", 0.5, 10.0, float(risk_per_trade), step=0.5)
        n_trades = st.number_input("Simultaneous Trades", 1, 20, 5)
    if entry_px >0 and entry_px > stop_px > 0:
        rps = entry_px - stop_px
        rws = target_px - entry_px
        rr = rws/rps if rps>0 else 0
        car = cap2*(risk_pct2/100)
        qty_c = max(1, int(car/rps))
        tv = qty_c*entry_px; ml = qty_c*rps; mg = qty_c*rws
        rc1,rc2,rc3,rc4 = st.columns(4)
        for col,lbl,val,clr in zip([rc1,rc2,rc3,rc4], ["Qty to Buy","Total Value","Max Loss","Max Gain"],
 [str(qty_c),f"₹{tv:,.0f}",f"₹{ml:,.0f}",f"₹{mg:,.0f}"],
 ["#00c8ff","#ddeeff","#ff3355","#00e87a"]):
            col.markdown(card(lbl,val,clr), unsafe_allow_html=True)
        rr_clr = "#00e87a" if rr>=2 else "#ffcc00" if rr>=1 else "#ff3355"
        st.markdown(f'<div class="glass-card" style="text-align:center;"><p class="glass-label">Risk:Reward</p>'
 f'<div class="glass-value" style="color:{rr_clr};">1 : {rr:.2f}</div>'
                    f'<p style="font-size:10px;color:#6a90aa;margin:3px 0 0;">Portfolio risk at {n_trades} trades: ₹{ml*n_trades:,.0f}</p></div>', unsafe_allow_html=True)
        # Kelly from backtest if available
        if "bt_metrics" in st.session_state:
            km = st.session_state.bt_metrics
            if km["Total"]>0 and km["AvgWin"]>0:
                wr = km["WinRate"]/100
                kelly = (wr*km["AvgWin"] - (1-wr)*abs(km["AvgLoss"]))/km["AvgWin"] if km["AvgWin"]>0 else 0
                if kelly>0:
                    st.markdown(f'<div class="glass-card"><p class="glass-label">Kelly Criterion (from backtest)</p>'
 f'<div class="glass-value" style="color:#00e87a;">{kelly:.1%}</div></div>', unsafe_allow_html=True)
    else:
        st.warning("Stop loss must be below entry price.")

# ── TAB: PORTFOLIO ────────────────────────────────────────────────
with tabs[5]:
    st.markdown('<p class="section-header">[ MPT PORTFOLIO OPTIMIZER ]</p>', unsafe_allow_html=True)
    defs = [k for k in ALL_STOCKS if any(x in k for x in ["Reliance (", "TCS (", "HDFC Bank (", "Infosys (", "SBI (")])][:5]
    sel_keys = st.multiselect("Select 2–10 assets", list(ALL_STOCKS.keys()), default=defs)
    if len(sel_keys) < 2:
        st.warning("Select at least 2 assets.")
    else:
        if st.button("Optimize Portfolio", use_container_width=True):
            with st.spinner("Running Monte Carlo (3000 portfolios) + correlation matrix..."):
                try:
                    tks = [ALL_STOCKS[k] for k in sel_keys]
                    nms = [k.split(" (")[0] for k in sel_keys]
                    raw_batch = download_batch(tks, period="2y")
                    # align closes                    close_d = {}
                    for k,v in raw_batch.items():
                        if v is not None and "Close" in v.columns:
                            close_d[SYM2NAME.get(k,k)] = v.set_index("Date")["Close"].astype(float)
                    if len(close_d) < 2:
                        st.error("Not enough data downloaded for selected assets.")
 st.stop()
                    c_prices = pd.DataFrame(close_d).sort_index().ffill().dropna()
                    if len(c_prices) < 60:
                        st.error("Insufficient aligned history.")
                        st.stop()
                    ret_df = c_prices.pct_change().dropna()
                    # drop assets with >40% missing post-alignment
                    valid = [c for c in ret_df.columns if ret_df[c].isna().mean()<0.4]
                    ret_df = ret_df[valid].dropna()
                    na = len(ret_df.columns)
                    mu = ret_df.mean(); cov = ret_df.cov()
                    N = 3000
                    vols,rets,sharpes,all_w = [],[],[],[]
 for _ in range(N):
                        w = np.random.dirichlet(np.ones(na))
                        pr = float(np.dot(mu,w))*252
                        pv = float(np.sqrt(max(w @ (cov.values*252) @ w, 0)))
                        ps = pr/pv if pv>0 else 0
                        vols.append(pv); rets.append(pr); sharpes.append(ps); all_w.append(w)
                    max_sh = int(np.argmax(sharpes)); min_vol = int(np.argmin(vols))
 obj = st.radio("Objective", ["Maximize Sharpe Ratio","Minimize Volatility"], horizontal=True)
                    idx = max_sh if "Sharpe" in obj else min_vol
                    opt_w = all_w[idx]; sel_v = vols[idx]; sel_r = rets[idx]; sel_s = sharpes[idx]
                    pm1,pm2,pm3 = st.columns(3)
                    pm1.markdown(card("Expected Return",f"{sel_r:.1%}","#00e87a"), unsafe_allow_html=True)
                    pm2.markdown(card("Volatility",f"{sel_v:.1%}","#ff3355"), unsafe_allow_html=True)
                    pm3.markdown(card("Sharpe Ratio",f"{sel_s:.2f}","#00c8ff"), unsafe_allow_html=True)
                    st.markdown('<p class="section-header">[ CAPITAL ALLOCATION ]</p>', unsafe_allow_html=True)
                    colors = ["#00c8ff","#00e87a","#ffcc00","#ff6b35","#7c4dff","#ff3355","#fbbf24","#34d399","#a78bfa","#fb923c"]
                    acols = st.columns(min(na,5))
                    for i,(nm,w) in enumerate(zip(valid, opt_w)):
                        amt = allocated_capital*w
                        acols[i%len(acols)].markdown(
                            f'<div class="glass-card" style="text-align:center;"><p class="glass-label">{nm[:14]}</p>'
                            f'<div class="glass-value" style="color:{colors[i%len(colors)]};font-size:.95rem;">₹{amt:,.0f}</div>'
                            f'<p style="font-size:10px;color:#6a90aa;">{w:.1%}</p></div>', unsafe_allow_html=True)
                    c1,c2 = st.columns(2)
                    with c1:
 fp = go.Figure(data=[go.Pie(labels=valid, values=opt_w, hole=0.42,
                            marker=dict(colors=colors[:na]), textfont=dict(color="#ddeeff"))])
 fp = dark_fig(fp, 300)
 st.plotly_chart(fp, use_container_width=True)
                    with c2:
                        fe = go.Figure()
                        fe.add_trace(go.Scatter(x=vols, y=rets, mode="markers",
                            marker=dict(color=sharpes, colorscale="Viridis", size=3, showscale=True,
 colorbar=dict(title="Sharpe",thickness=12,tickfont=dict(size=8,color="#ddeeff"))), name="Portfolios"))
                        fe.add_trace(go.Scatter(x=[sel_v], y=[sel_r], mode="markers",
                            marker=dict(color="#ff3355", size=14, symbol="star", line=dict(width=1, color="white")), name="Optimal"))
 fe = dark_fig(fe, 300)
                        fe.update_xaxes(title="Volatility", tickformat=".1%")
                        fe.update_yaxes(title="Return", tickformat=".1%")
                        st.plotly_chart(fe, use_container_width=True)
                    # Correlation heatmap (value add)
                    st.markdown('<p class="section-header">[ CORRELATION MATRIX ]</p>', unsafe_allow_html=True)
                    corr = ret_df.corr()
 fig_hm = go.Figure(data=go.Heatmap(
                        z=corr.values, x=corr.columns, y=corr.columns, colorscale="RdBu", zmid=0,
                        text=np.round(corr.values,2), texttemplate="%{text}", textfont=dict(size=9,color="#fff"),
                    ))
 fig_hm = dark_fig(fig_hm, 340)
                    fig_hm.update_layout(xaxis=dict(tickangle=-30), yaxis=dict(tickangle=0))
                    st.plotly_chart(fig_hm, use_container_width=True)
                except Exception as e:
                    st.error(f"Portfolio error: {e}")

# ── TAB: FII/DII ──────────────────────────────────────────────────
with tabs[6]:
    st.markdown('<p class="section-header">[ 📊 FII / DII INSTITUTIONAL FLOW — NSE INDIA ]</p>', unsafe_allow_html=True)
    fii_data = fetch_fii_dii()
    df_fii, today_fii = parse_fii_dii(fii_data)
    if df_fii is None or today_fii is None:
        st.warning("NSE auto-scrape failed — upload CSV manually to view data.")
        up = st.file_uploader("Upload NSE FII/DII CSV", type=["csv"])
        if up is not None:
            try:
                df_fii = pd.read_csv(up)
                today_fii = df_fii.iloc[0]
            except Exception:
                st.error("Could not parse uploaded CSV.")
 if df_fii is not None and today_fii is not None:
        fii_net = float(today_fii["FII Net"]); dii_net = float(today_fii["DII Net"])
        combined = fii_net + dii_net
        cd = str(today_fii["Date"])[:10]
        fcols = st.columns(4)
        items = [
            ("FII Net Today (Cr)", f"{'▲' if fii_net>=0 else '▼'} ₹{abs(fii_net):,.0f}", "#00e87a" if fii_net>=0 else "#ff3355"),
            ("DII Net Today (Cr)", f"{'▲' if dii_net>=0 else '▼'} ₹{abs(dii_net):,.0f}", "#00e87a" if dii_net>=0 else "#ff3355"),
            ("Combined Net (Cr)", f"{'▲' if combined>=0 else '▼'} ₹{abs(combined):,.0f}", "#00e87a" if combined>=0 else "#ff3355"),
            ("Date", cd, "#ddeeff")
        ]
        for col, (lbl,val,clr) in zip(fcols, items):
            col.markdown(card(lbl,val,clr), unsafe_allow_html=True)
        view = "BULLISH" if fii_net>0 else "BEARISH"
        vclr = "#00e87a" if fii_net>0 else "#ff3355"
        if fii_net>0 and dii_net>0: msg = "Both FII and DII buying — strong conviction. Typically bullish."
        elif fii_net>0 and dii_net<0: msg = "FII buying, DII selling — foreign flow in, domestic profit-booking."
        elif fii_net<0 and dii_net>0: msg = "FII selling, DII buying — domestic absorbing outflows. Resilient."
        else: msg = "Both selling — broad outflow. Typically bearish near-term."
        st.markdown(f'<div class="glass-card"><p class="glass-label">Interpretation</p>'
 f'<div style="font-size:13px;color:{vclr};font-weight:600;">{view} FLOW</div>'
                    f'<p style="font-size:12px;color:#a0aec0;line-height:1.6;">{msg}</p></div>', unsafe_allow_html=True)
        if len(df_fii)>1:
            st.markdown('<p class="section-header">[ RECENT NET FLOWS ]</p>', unsafe_allow_html=True)
            ffig = go.Figure()
            fc = ["#00e87a" if v>=0 else "#ff3355" for v in df_fii["FII Net"]]
            dc = ["#00c8ff" if v>=0 else "#ff6b35" for v in df_fii["DII Net"]]
            ffig.add_trace(go.Bar(x=df_fii["Date"], y=df_fii["FII Net"], name="FII Net", marker_color=fc, opacity=0.85))
            ffig.add_trace(go.Bar(x=df_fii["Date"], y=df_fii["DII Net"], name="DII Net", marker_color=dc, opacity=0.85))
 ffig.add_hline(y=0, line_color="rgba(255,255,255,0.2)", line_width=1)
            ffig = dark_fig(ffig, 320); ffig.update_layout(barmode="group", yaxis=dict(title="Net Flow (Cr ₹)"))
            st.plotly_chart(ffig, use_container_width=True)
        st.markdown('<p class="section-header">[ DETAILED TABLE ]</p>', unsafe_allow_html=True)
        disp = df_fii[["Date","FII Buy","FII Sell","FII Net","DII Buy","DII Sell","DII Net"]].round(2)
        st.dataframe(disp, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download FII/DII CSV", disp.to_csv(index=False).encode(), "fii_dii_flows.csv", "text/csv")

# ── TAB: OPTIONS ──────────────────────────────────────────────────
with tabs[7]:
    st.markdown(f'<p class="section-header">[ 🎯 OPTIONS CHAIN — {selected_name} ]</p>', unsafe_allow_html=True)
    opt_data = fetch_options_chain(selected_ticker)
    df_chain, pcr, max_pain, expiry = parse_options_chain(opt_data, close)
    if df_chain is None:
        st.warning("Options chain scrape failed — upload NSE options CSV to visualize.")
        up2 = st.file_uploader("Upload Options Chain CSV", type=["csv"])
        if up2 is not None:
            try:
                df_chain = pd.read_csv(up2)
                # infer simplest possible                pcr =1.0; max_pain = close; expiry = "Uploaded"
                if "PE OI" in df_chain.columns and "CE OI" in df_chain.columns:
 pcr = round(df_chain["PE OI"].sum()/max(df_chain["CE OI"].sum(),1),3)
            except Exception:
                st.error("Could not parse uploaded options CSV.")
    if df_chain is not None and len(df_chain)>0:
        o1,o2,o3,o4 = st.columns(4)
        pcr_clr = "#00e87a" if pcr and pcr>1 else "#ff3355" if pcr and pcr<0.7 else "#ffcc00"
        for col,lbl,val,clr in zip([o1,o2,o3,o4],
            ["Spot Price","Max Pain","PCR","Expiry"],
            [f"₹{close:,.2f}", f"₹{max_pain:,.0f}" if max_pain else "N/A", f"{pcr:.3f}" if pcr else "N/A", str(expiry) if expiry else "N/A"],
            ["#ddeeff", "#00c8ff", pcr_clr, "#6a90aa"]):
            col.markdown(card(lbl,val,clr), unsafe_allow_html=True)
        if pcr:
            if pcr>1.2: pi = "HIGH PCR (>1.2) — Bearish sentiment dominant. Contrarian: possible reversal up."
            elif pcr<0.7: pi = "LOW PCR (<0.7) — Bullish sentiment dominant. Contrarian: possible pullback."
            else: pi = "NEUTRAL PCR (0.7–1.2) — Balanced activity."
 st.markdown(f'<div class="glass-card"><p class="glass-label">PCR Read</p>'
 f'<p style="font-size:12px;color:{"#00e87a" if pcr>1.2 else "#ff3355" if pcr<0.7 else "#ffcc00"};font-weight:600;">{pi}</p></div>', unsafe_allow_html=True)
        if max_pain:
            updown = "Above" if close>max_pain else "Below"
            pf = abs(close-max_pain)/max_pain*100 if max_pain else 0
            st.markdown(f'<div class="glass-card"><p class="glass-label">Max Pain</p>'
 f'<p style="font-size:12px;color:#a0aec0;">Spot {updown} max pain by {pf:.1f}%. Sellers profit if expiry at ₹{max_pain:,.0f}.</p></div>', unsafe_allow_html=True)
        st.markdown('<p class="section-header">[ OPEN INTEREST BY STRIKE ]</p>', unsafe_allow_html=True)
        near = df_chain[(df_chain["Strike"]>=close*0.85)&(df_chain["Strike"]<=close*1.15)]
        if len(near)>0:
            foi = go.Figure()
            foi.add_trace(go.Bar(x=near["Strike"], y=near["CE OI"], name="Call OI", marker_color="rgba(255,51,85,0.7)"))
            foi.add_trace(go.Bar(x=near["Strike"], y=near["PE OI"], name="Put OI", marker_color="rgba(0,200,255,0.7)"))
            if max_pain:
                foi.add_vline(x=max_pain, line_dash="dash", line_color="#fbbf24", annotation_text=f"Max Pain ₹{max_pain:,.0f}", annotation_font_color="#fbbf24")
            foi.add_vline(x=close, line_dash="dot", line_color="rgba(255,255,255,0.5)", annotation_text=f"Spot ₹{close:,.0f}", annotation_font_color="#ddeeff")
            foi = dark_fig(foi, 360); foi.update_layout(barmode="group", xaxis=dict(title="Strike"), yaxis=dict(title="OI"))
            st.plotly_chart(foi, use_container_width=True)
        st.markdown('<p class="section-header">[ FULL CHAIN TABLE ]</p>', unsafe_allow_html=True)
        cdisp = df_chain[["CE LTP","CE OI","CE IV","Strike","PE IV","PE OI","PE LTP"]].copy().round(2)
        st.dataframe(cdisp, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download Options Chain", cdisp.to_csv(index=False).encode(), f"{selected_name}_options_chain.csv", "text/csv")

# ── TAB: FUNDAMENTALS ─────────────────────────────────────────────
with tabs[8]:
    st.markdown(f'<p class="section-header">[ 📋 FUNDAMENTALS — {selected_name} ]</p>', unsafe_allow_html=True)
    with st.spinner("Fetching..."):
        fund_data, fund_url = fetch_fundamentals(selected_ticker)
    # Manual fallback panel
    if not fund_data or all(v is None for v in fund_data.values()):
        st.warning("Screener.in scrape failed. Enter manually or upload CSV.")
        c1,c2,c3 = st.columns(3)
        with c1:
            m_pe = st.number_input("P/E", value=0.0, step=0.1, key="m_pe"); m_pb = st.number_input("P/B", value=0.0, step=0.1, key="m_pb")
        with c2:
            m_roe = st.number_input("ROE %", value=0.0, step=0.1, key="m_roe"); m_roce = st.number_input("ROCE %", value=0.0, step=0.1, key="m_roce")
        with c3:
            m_de = st.number_input("D/E", value=0.0, step=0.1, key="m_de"); m_dy = st.number_input("Div Yield %", value=0.0, step=0.1, key="m_dy")
        m_eps = st.number_input("EPS", value=0.0, step=0.1, key="m_eps"); m_prom = st.number_input("Promoter %", value=0.0, step=0.1, key="m_prom")
        fund_data = {
            "P/E Ratio":m_pe if m_pe>0 else None,"P/B Ratio":m_pb if m_pb>0 else None,
            "ROE (%)":m_roe if m_roe!=0 else None,"ROCE (%)":m_roce if m_roce!=0 else None,
            "Debt/Equity":m_de if m_de>=0 else None,"Promoter Hold%":m_prom if m_prom>0 else None,
            "EPS (TTM)":m_eps if m_eps!=0 else None,"Div Yield (%)":m_dy if m_dy>=0 else None,
        }
    if fund_data and any(v is not None for v in fund_data.values()):
        fcols = st.columns(3)
        ratio_keys = [("P/E Ratio","#00c8ff"),("P/B Ratio","#ffcc00"),("ROE (%)","#00e87a"),("ROCE (%)","#00e87a"),("Debt/Equity","#ff3355"),("Div Yield (%)","#7c4dff")]
        for i,(key,clr) in enumerate(ratio_keys):
            val = fund_data.get(key)
            val_str = f"{val:.2f}" if val is not None else "N/A"
            fcols[i%3].markdown(card(key,val_str,clr), unsafe_allow_html=True)
        ep1,ep2 = st.columns(2)
        eps = fund_data.get("EPS (TTM)"); prom = fund_data.get("Promoter Hold%")
        ep1.markdown(card("EPS (TTM)", f"₹{round(eps,2)}" if eps else "N/A", "#fbbf24"), unsafe_allow_html=True)
        ep2.markdown(card("Promoter Holding", f"{round(prom,1)}%" if prom else "N/A", "#00e87a" if prom and prom>50 else "#ffcc00"), unsafe_allow_html=True)
        pe=fund_data.get("P/E Ratio"); roe=fund_data.get("ROE (%)"); de=fund_data.get("Debt/Equity")
        scores=[]
        if pe: scores.append("Cheap" if pe<15 else "Fair" if pe<30 else "Expensive")
        if roe: scores.append("High ROE" if roe>20 else "Moderate ROE" if roe>12 else "Low ROE")
        if de: scores.append("Low Debt" if de<0.5 else "Moderate Debt" if de<1.5 else "High Debt")
        if scores:
            st.markdown(f'<div class="glass-card"><p class="glass-label">Verdict</p>'
 f'<p style="font-size:13px;color:{"#00e87a" if "Cheap" in scores or "High ROE" in scores else "#ffcc00"};font-weight:600;">{" | ".join(scores)}</p></div>', unsafe_allow_html=True)
        st.caption("Source: Screener.in · Values garbage-filtered via range checks")
 st.markdown(f"[View on Screener.in]({fund_url})")
    with st.expander("📖 Ratio guide"):
        st.markdown("""
| Ratio | Good | Average | Expensive/Risky |
|---|---|---|---|
| P/E | < 15 | 15–30 | > 40 |
| P/B | < 1.5 | 1.5–4 | > 6 |
| ROE | > 20% | 12–20% | < 10% |
| ROCE | > 20% | 12–20% | < 10% |
| Debt/Equity | < 0.5 | 0.5–1.5 | > 2.0 |
| Promoter Hold | > 50% | 35–50% | < 25% |
""")

# ── TAB: NEWS ─────────────────────────────────────────────────────
with tabs[9]:
    st.markdown(f'<p class="section-header">[ 📰 NEWS & SENTIMENT — {selected_name} ]</p>', unsafe_allow_html=True)
    with st.spinner("Fetching headlines..."):
        items = fetch_news(selected_ticker, selected_name)
    if items:
        score, cat = sentiment_score(items); sent_clr = {"BULLISH":"#00e87a","BEARISH":"#ff3355","NEUTRAL":"#ffcc00"}[cat]
        ns1,ns2 = st.columns([1,2])
        with ns1:
            st.markdown(f'<div class="glass-card" style="text-align:center;padding:20px 12px;">'
                        f'<p class="glass-label">Sentiment</p>'
                        f'<div style="font-family:Orbitron;font-size:1.8rem;font-weight:900;color:{sent_clr};margin:8px 0;">{cat}</div>'
                        f'<p style="font-size:10px;color:#6a90aa;">Score: {score:+.3f} | {len(items)} headlines</p></div>', unsafe_allow_html=True)
        with ns2:
            bc = sum(1 for it in items if any(w in it["title"].lower().split() for w in BULL_KW))
            brc = sum(1 for it in items if any(w in it["title"].lower().split() for w in BEAR_KW))
            st.markdown(f'<div class="glass-card"><p class="glass-label">Keyword Breakdown</p>'
                        f'<div style="font-family:Space Mono;font-size:12px;">Bullish: <span style="color:#00e87a;font-weight:700;">{bc}</span> | '
                        f'Bearish: <span style="color:#ff3355;font-weight:700;">{brc}</span></div>'
                        f'<p style="font-size:11px;color:#6a90aa;margin-top:6px;">Negation-aware keyword scoring.</p></div>', unsafe_allow_html=True)
        st.markdown('<p class="section-header">[ HEADLINES ]</p>', unsafe_allow_html=True)
        for it in items:
            tl = it["title"].lower()
            is_bull = any(w in tl.split() for w in BULL_KW) and not any(f"no {w}" in tl or f"not {w}" in tl for w in BULL_KW)
            is_bear = any(w in tl.split() for w in BEAR_KW)
            dot_clr = "#00e87a" if is_bull and not is_bear else "#ff3355" if is_bear else "#6a90aa"
            st.markdown(f'<div class="glass-card" style="padding:9px 13px;margin-bottom:5px;display:flex;align-items:center;gap:10px;">'
                        f'<div style="width:7px;height:7px;border-radius:50%;background:{dot_clr};flex-shrink:0;"></div>'
                        f'<a href="{it["link"]}" target="_blank" style="color:#00c8ff;text-decoration:none;font-size:12px;font-weight:600;flex:1;">{it["title"]}</a>'
                        f'<span style="font-size:9px;color:#4a7090;font-family:Space Mono;flex-shrink:0;">{it["date"]}</span></div>', unsafe_allow_html=True)
    else:
        st.info(f"No headlines found for {selected_ticker}.")

# ── TAB: MANUAL / HELP ────────────────────────────────────────────
with tabs[10]:
    st.markdown("""
<div class="glass-card">
<p class="section-header" style="margin-top:0;">[ XERCES v2 REFERENCE MANUAL ]</p>
<div style="font-size:11px;color:#8ab0cc;line-height:2.0;font-family:'Space Mono',monospace;">
<b style="color:#00c8ff;">RSI (14)</b> — &lt;30 oversold (buy zone). &gt;70 overbought (sell zone).<br>
<b style="color:#00c8ff;">MACD (12,26,9)</b> — Cross above signal = bullish momentum.<br>
<b style="color:#00c8ff;">SMA 20/50/200</b> — Golden cross = major bull. Price &gt; SMA200 = bull market.<br>
<b style="color:#00c8ff;">Bollinger Bands</b> — Squeeze = volatility expansion imminent.<br>
<b style="color:#00c8ff;">ATR (14)</b> — True range. Stop-loss sizing at 1.5× ATR.<br>
<b style="color:#00c8ff;">Stochastic %K</b> — &lt;20 oversold, &gt;80 overbought.<br>
<br>
<b style="color:#ffcc00;">Forecasting</b> — Holt-Winters (default, instant). ARIMA (16-model grid, opt-in). Consensus = average.<br>
<b style="color:#ffcc00;">Backtest</b> — Next-day-open execution. No look-ahead. Includes Sortino, Calmar, Expectancy, Kelly proxy.<br>
<br>
<b style="color:#7c4dff;">Portfolio</b> — Markowitz MPT with 3000 Monte Carlo draws + correlation heatmap.<br>
<b style="color:#7c4dff;">Scanner</b> — Batched Yahoo Finance downloads (gentler on rate limits).<br>
<br>
<b style="color:#ff3355;">DISCLAIMER:</b> Not SEBI registered. Not financial advice. Data from Yahoo Finance / NSE / Screener.
</div>
</div>
""", unsafe_allow_html=True)
