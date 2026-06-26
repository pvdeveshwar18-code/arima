import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import requests

st.set_page_config(page_title="Indian Stocks Forecast Pro", page_icon="📈", layout="wide")

# Premium Cyberpunk-Dark Style Sheet
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght=400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background:
        radial-gradient(circle at top left, rgba(0,212,170,0.12), transparent 25%),
        radial-gradient(circle at top right, rgba(56,189,248,0.12), transparent 20%),
        linear-gradient(180deg, #050816 0%, #0b1020 100%);
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1220 0%, #070b15 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
div[data-baseweb="tab-list"] { gap: 10px; }
button[data-baseweb="tab"] {
    border-radius: 999px !important;
    padding: 0.45rem 1.2rem !important;
    background: rgba(15, 23, 42, 0.55) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    color: #94a3b8 !important;
    font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(90deg, rgba(0,212,170,0.25), rgba(56,189,248,0.25)) !important;
    border: 1px solid rgba(0,212,170,0.40) !important;
    color: #00d4aa !important;
}
.stButton > button {
    background: linear-gradient(90deg, #00d4aa, #38bdf8) !important;
    color: #03111f !important;
    border: none !important;
    border-radius: 999px !important;
    font-weight: 700 !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.2s ease-in-out;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,212,170,0.3);
}
.stTextInput input, .stTextArea textarea, .stSelectbox div, .stMultiSelect div {
    background: rgba(15, 23, 42, 0.85) !important;
    color: #e5e7eb !important;
    border-radius: 8px !important;
}
::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 999px; }
.suggestion-box {
    background: rgba(15, 23, 42, 0.95);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 0.5rem;
    margin-top: 0.35rem;
    max-height: 250px;
    overflow-y: auto;
}
.badge {
    display: inline-block;
    padding: 0.22rem 0.55rem;
    border-radius: 999px;
    font-size: 0.78rem;
    margin-left: 0.35rem;
    background: rgba(56,189,248,0.14);
    border: 1px solid rgba(56,189,248,0.22);
    color: #bae6fd;
}
</style>
""",
    unsafe_allow_html=True,
)

# Header Section
st.markdown(
    """
<div style="margin-bottom: 1.0rem;">
    <h1 style="margin:0; font-size:2.3rem; font-weight:800; background: linear-gradient(90deg,#00d4aa,#38bdf8,#a78bfa); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
        Indian Stocks Forecast Pro
    </h1>
    <p style="margin:0.25rem 0 0 0; color: rgba(229,231,235,.65); font-size: 0.95rem;">
        Forecasts, indicators, backtesting, market structure, risk mitigation metrics, and core fundamentals.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

@st.cache_data(ttl=24 * 60 * 60)
def load_stock_universe():
    frames = []
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get("https://raw.githubusercontent.com/anirbanghoshsbi/NSE-LIST/master/NSE_EQUITIES_LIST.csv", headers=headers, timeout=5)
        if res.status_code == 200:
            from io import StringIO
            nse = pd.read_csv(StringIO(res.text))
            nse.columns = [c.strip().upper() for c in nse.columns]
            sym_col = "SYMBOL" if "SYMBOL" in nse.columns else nse.columns[0]
            name_col = "NAME OF COMPANY" if "NAME OF COMPANY" in nse.columns else sym_col
            
            tmp = pd.DataFrame()
            tmp["company"] = nse[name_col].astype(str).str.strip()
            tmp["symbol"] = nse[sym_col].astype(str).str.strip()
            tmp["ticker"] = tmp["symbol"] + ".NS"
            tmp["exchange"] = "NSE"
            frames.append(tmp)
    except Exception:
        pass

    if not frames:
        fallback_data = {
            "company": ["Reliance Industries Ltd", "Tata Consultancy Services", "HDFC Bank Ltd", "Infosys Ltd", "State Bank of India"],
            "symbol": ["RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN"],
            "ticker": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "SBIN.NS"],
            "exchange": ["NSE"] * 5
        }
        frames.append(pd.DataFrame(fallback_data))

    uni = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["ticker"])
    uni["display"] = uni["company"].fillna(uni["symbol"]).astype(str) + " | " + uni["exchange"].astype(str) + " | " + uni["ticker"].astype(str)
    return uni.sort_values(["company", "exchange"]).reset_index(drop=True)

universe = load_stock_universe()

if "main_ticker" not in st.session_state:
    st.session_state.main_ticker = "TCS.NS"
if "selected_company" not in st.session_state:
    st.session_state.selected_company = "Tata Consultancy Services"
if "selected_exchange" not in st.session_state:
    st.session_state.selected_exchange = "NSE"
if "trigger_analysis" not in st.session_state:
    st.session_state.trigger_analysis = True

def set_selected(display):
    row = universe[universe["display"] == display].head(1)
    if not row.empty:
        st.session_state.main_ticker = row["ticker"].iloc[0]
        st.session_state.selected_company = row["company"].iloc[0]
        st.session_state.selected_exchange = row["exchange"].iloc[0]

def suggestion_matches(query):
    if universe.empty:
        return pd.DataFrame(columns=universe.columns)
    q = (query or "").lower().strip()
    if not q:
        return universe.head(8)
    mask = (
        universe["company"].astype(str).str.lower().str.contains(q, na=False)
        | universe["symbol"].astype(str).str.lower().str.contains(q, na=False)
        | universe["ticker"].astype(str).str.lower().str.contains(q, na=False)
    )
    return universe.loc[mask].head(8)

def add_indicators(df):
    out = df.copy()
    if len(out) < 2: return out
    out["Return"] = out["Close"].pct_change()
    out["SMA_20"] = out["Close"].rolling(20).mean()
    out["SMA_50"] = out["Close"].rolling(50).mean()
    out["Volatility_20"] = out["Return"].rolling(20).std() * np.sqrt(252)
    
    delta = out["Close"].diff()
    gain = (delta.clip(lower=0)).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    out["RSI_14"] = 100 - (100 / (1 + rs))
    
    out["ATR_14"] = (out["High"] - out["Low"]).rolling(14).mean() if {"High", "Low"}.issubset(out.columns) else out["Close"].rolling(14).std()
    return out

def signal_label(df):
    if len(df) < 2: return "Hold"
    last = df.iloc[-1]
    if pd.isna(last["SMA_20"]) or pd.isna(last["SMA_50"]) or pd.isna(last["RSI_14"]):
        return "Hold"
    if last["SMA_20"] > last["SMA_50"] and last["RSI_14"] < 70:
        return "Buy"
    if last["SMA_20"] < last["SMA_50"] and last["RSI_14"] > 30:
        return "Exit"
    return "Hold"

@st.cache_data(ttl=3600)
def download_stock(ticker, period, interval):
    try:
        df = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False, show_errors=False)
        if df is not None and not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] for c in df.columns]
            df = df.reset_index()
            if "Datetime" in df.columns: df = df.rename(columns={"Datetime": "Date"})
            df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
            return df.dropna(subset=["Date", "Close"])
    except: pass
    return pd.DataFrame()

# --- SIDEBAR INTERFACE & NAVIGATION MENU ---
with st.sidebar:
    st.header("📌 Navigation")
    app_mode = st.radio("Go to view:", ["🔍 Asset Deep-Dive", "🎯 Buy Recommendations Scanner"])
    
    st.markdown("---")
    st.header("Parameters")
    period = st.selectbox("History", ["5y", "3y", "2y", "1y"], index=3) # Set default history closer for faster execution
    interval = st.selectbox("Interval", ["1d", "1wk"], index=0)
    
    if app_mode == "🔍 Asset Deep-Dive":
        forecast_days = st.slider("Forecast horizon (trading days)", 5, 252, 60)
    
    st.markdown("---")
    st.header("⚙️ Strategic Sizing")
    allocated_capital = st.number_input("Total Trade Capital (₹)", min_value=1000, value=100000, step=5000)
    risk_per_trade = st.slider("Max Capital Risk Per Trade (%)", 0.5, 5.0, 1.5, step=0.1)
    risk_reward_ratio = st.slider("Target Risk-to-Reward Ratio (1:X)", 1.5, 4.0, 2.0, step=0.5)


# ==========================================================
# VIEW 1: INDIVIDUAL ASSET DEEP DIVE
# ==========================================================
if app_mode == "🔍 Asset Deep-Dive":
    st.markdown("### 🔍 Search Symbol")
    search_col1, search_col2 = st.columns([0.8, 0.2])
    with search_col1:
        search_text = st.text_input("Type company name or exchange symbol", value="", placeholder="🔍 Symbol, company... (e.g. TCS, RELIANCE)", label_visibility="collapsed")
    with search_col2:
        run_pressed = st.button("Run Analysis", use_container_width=True)

    matches = suggestion_matches(search_text)
    if search_text.strip() != "" and not matches.empty:
        st.markdown('<div class="suggestion-box">', unsafe_allow_html=True)
        for _, row in matches.iterrows():
            if st.button(row["display"], key=f"sel_{row['ticker']}", use_container_width=True):
                set_selected(row["display"])
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    if run_pressed:
        raw_text = search_text.strip().upper()
        if raw_text and not (raw_text.endswith(".NS") or raw_text.endswith(".BO")):
            st.session_state.main_ticker = f"{raw_text}.NS"
            st.session_state.selected_company = raw_text
            st.session_state.selected_exchange = "NSE"
        st.session_state.trigger_analysis = True
        st.rerun()

    st.markdown(f"<div style='margin-bottom: 1.5rem;'>Active Asset Focus: <strong>{st.session_state.selected_company}</strong> <span class='badge'>{st.session_state.selected_exchange}</span> <span class='badge'>{st.session_state.main_ticker}</span></div>", unsafe_allow_html=True)

    if st.session_state.trigger_analysis:
        base = download_stock(st.session_state.main_ticker, period, interval)
        if base.empty:
            st.error(f"No valid price history fetched for {st.session_state.main_ticker}.")
        else:
            base = add_indicators(base)
            last_close = float(base["Close"].iloc[-1])
            ytd_return = float((base["Close"].iloc[-1] / base["Close"].iloc[0] - 1) * 100)
            annual_vol = float(base["Volatility_20"].iloc[-1]) if pd.notna(base["Volatility_20"].iloc[-1]) else 0.0
            signal = signal_label(base)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Last Close", f"₹{last_close:,.2f}", "Live Engine")
            c2.metric("Period Return", f"{ytd_return:+.2f}%", "Historical Baseline")
            c3.metric("Annual Volatility", f"{annual_vol:.2%}", "Risk Standard", delta_color="inverse")
            c4.metric("Tactical Bias", signal, "Quant Rules")

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=base["Date"], y=base["Close"], name="Close Price", line=dict(color="#00d4aa")))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#e5e7eb"), height=400)
            st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# VIEW 2: AUTOMATED WHOLE-MARKET BUY RECOMMENDATIONS SCANNER
# ==========================================================
elif app_mode == "🎯 Buy Recommendations Scanner":
    st.markdown("### ⚡ Full National Stock Exchange (NSE) Scanner Engine")
    st.markdown(f"Total traceable securities indexed: **{len(universe)} listed listings**.")
    
    scan_limit = st.number_input("Scan Limit (Limit list size to prevent timeout spikes)", min_value=10, max_value=3000, value=250, step=50)
    
    if st.button("🚀 Execute Broad Market Scan", use_container_width=True):
        tickers_to_scan = universe["ticker"].head(scan_limit).tolist()
        
        st.info("Downloading historical multi-matrix frames in vectorized layout chunks...")
        
        try:
            # Vectorized multi-download architecture prevents slow step loops
            raw_data = yf.download(tickers_to_scan, period="6mo", interval=interval, group_by='ticker', auto_adjust=False, progress=False, show_errors=False)
            
            results = []
            for ticker in tickers_to_scan:
                try:
                    if ticker in raw_data.columns.levels[0]:
                        df_ticker = raw_data[ticker].dropna(subset=["Close"]).reset_index()
                        if len(df_ticker) < 30: continue
                        
                        df_calc = add_indicators(df_ticker)
                        last_row = df_calc.iloc[-1]
                        bias = signal_label(df_calc)
                        
                        current_price = float(last_row["Close"])
                        atr = last_row["ATR_14"] if pd.notna(last_row["ATR_14"]) else (current_price * 0.02)
                        sl_dist = atr * 1.5
                        sl_price = current_price - sl_dist
                        tp_price = current_price + (sl_dist * risk_reward_ratio)
                        
                        rupees_at_risk = allocated_capital * (risk_per_trade / 100.0)
                        shares_to_buy = int(rupees_at_risk // sl_dist) if sl_dist > 0 else 0
                        
                        results.append({
                            "Ticker Symbol": ticker.replace(".NS", ""),
                            "Current Price": f"₹{current_price:,.2f}",
                            "RSI (14)": f"{last_row['RSI_14']:.1f}",
                            "Technical Recommendation": bias,
                            "Suggested Sizing": f"{shares_to_buy} Units",
                            "Calculated Stop-Loss": f"₹{sl_price:,.2f}",
                            "Profit Target": f"₹{tp_price:,.2f}"
                        })
                except:
                    continue
            
            if results:
                df_scan = pd.DataFrame(results)
                buys_only = df_scan[df_scan["Technical Recommendation"] == "Buy"]
                exits_only = df_scan[df_scan["Technical Recommendation"] == "Exit"]
                
                t_buy, t_exit, t_all = st.tabs([f"🟢 Active Buys ({len(buys_only)})", f"🔴 Active Exits ({len(exits_only)})", "🌐 Scanned Tracker Matrix"])
                
                with t_buy:
                    if not buys_only.empty: st.dataframe(buys_only, use_container_width=True, hide_index=True)
                    else: st.info("No active crossover buy setups matched across current segment list.")
                with t_exit:
                    if not exits_only.empty: st.dataframe(exits_only, use_container_width=True, hide_index=True)
                    else: st.info("No structural exit signals flagged.")
                with t_all:
                    st.dataframe(df_scan, use_container_width=True, hide_index=True)
            else:
                st.error("Could not construct matrix. Try shrinking the timeframe data window depth.")
        except Exception as e:
            st.error(f"Vector calculation error: {str(e)}")
