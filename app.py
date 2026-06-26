import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_error, mean_squared_error
from math import sqrt
import requests

st.set_page_config(page_title="Indian Stocks Forecast Pro", page_icon="📈", layout="wide")

# Premium Cyberpunk-Dark Style Sheet
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
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

st.markdown(
    """
<div style="margin-bottom: 1.5rem;">
    <h1 style="margin:0; font-size:2.3rem; font-weight:800; background: linear-gradient(90deg,#00d4aa,#38bdf8,#a78bfa); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
        Indian Stocks Forecast Pro
    </h1>
    <p style="margin:0.25rem 0 0 0; color: rgba(229,231,235,.65); font-size: 0.95rem;">
        Forecasts, indicators, backtesting, market structure, and swing-trade context
    </p>
</div>
""",
    unsafe_allow_html=True,
)

@st.cache_data(ttl=24 * 60 * 60)
def load_stock_universe():
    frames = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        res = requests.get("https://nsearchives.nseindia.com/content/equities/sec_list.csv", headers=headers, timeout=3)
        if res.status_code == 200:
            from io import StringIO
            nse = pd.read_csv(StringIO(res.text))
            nse.columns = [c.strip() for c in nse.columns]
            if "SYMBOL" in nse.columns:
                tmp = pd.DataFrame()
                tmp["company"] = nse["NAME OF COMPANY"].astype(str).str.strip() if "NAME OF COMPANY" in nse.columns else nse["SYMBOL"].astype(str).str.strip()
                tmp["symbol"] = nse["SYMBOL"].astype(str).str.strip()
                tmp["ticker"] = tmp["symbol"] + ".NS"
                tmp["exchange"] = "NSE"
                frames.append(tmp)
    except Exception:
        pass

    if not frames:
        fallback_data = {
            "company": ["Reliance Industries Ltd", "Tata Consultancy Services", "HDFC Bank Ltd", "Infosys Ltd", "State Bank of India", "ICICI Bank Ltd", "ITC Ltd", "Larsen & Toubro Ltd", "Bharti Airtel Ltd", "Hindustan Unilever Ltd"],
            "symbol": ["RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN", "ICICIBANK", "ITC", "LT", "BHARTIARTL", "HINDUNILVR"],
            "ticker": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "SBIN.NS", "ICICIBANK.NS", "ITC.NS", "LT.NS", "BHARTIARTL.NS", "HINDUNILVR.NS"],
            "exchange": ["NSE"] * 10
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
    st.session_state.trigger_analysis = False

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

with st.sidebar:
    st.header("Search Stock")
    search_text = st.text_input(
        "Type company name or symbol",
        value="",
        placeholder="e.g. Reliance, TCS, INFY",
    )

    matches = suggestion_matches(search_text)
    
    if search_text.strip() != "" and not matches.empty:
        st.markdown('<div class="suggestion-box">', unsafe_allow_html=True)
        for _, row in matches.iterrows():
            if st.button(row["display"], key=f"sel_{row['ticker']}", use_container_width=True):
                set_selected(row["display"])
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    elif search_text.strip() != "":
        st.caption("✨ Custom Ticker detected. Press 'Run Analysis' to process it directly!")

    cleaned_input = search_text.strip().upper()
    if cleaned_input.endswith(".NS") or cleaned_input.endswith(".BO"):
        st.session_state.main_ticker = cleaned_input
        st.session_state.selected_company = cleaned_input.split(".")[0]
        st.session_state.selected_exchange = cleaned_input.split(".")[1]

    st.markdown(
        f"Selected: **{st.session_state.selected_company}** "
        f"<span class='badge'>{st.session_state.selected_exchange}</span> "
        f"<span class='badge'>{st.session_state.main_ticker}</span>",
        unsafe_allow_html=True,
    )

    period = st.selectbox("History", ["5y", "3y", "2y", "1y"], index=0)
    interval = st.selectbox("Interval", ["1d", "1wk"], index=0)
    forecast_days = st.slider("Forecast horizon (trading days)", 5, 252, 60)
    use_case = st.radio("Use case", ["Swing trade", "Long term"])
    backtest_split = st.slider("Backtest split (%)", 60, 90, 80)
    show_raw = st.checkbox("Show raw data", value=False)
    compare_all = st.checkbox("Compare selected tickers", value=True)
    
    if st.button("Run Analysis", use_container_width=True):
        raw_text = search_text.strip().upper()
        if raw_text and not (raw_text.endswith(".NS") or raw_text.endswith(".BO")) and matches.empty:
            st.session_state.main_ticker = f"{raw_text}.NS"
            st.session_state.selected_company = raw_text
            st.session_state.selected_exchange = "NSE"
            
        st.session_state.trigger_analysis = True
        st.rerun()

@st.cache_data(ttl=3600)
def download_stock(ticker, period, interval):
    try:
        df = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False, threads=False)
        if df is not None and not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] for c in df.columns]
            df = df.reset_index()
            if "Datetime" in df.columns:
                df = df.rename(columns={"Datetime": "Date"})
            df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
            df = df.dropna(subset=["Date", "Close"])
            for col in ["Open", "High", "Low", "Close", "Volume"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            return df
    except Exception as e:
        pass
    return pd.DataFrame()

def add_indicators(df):
    out = df.copy()
    out["Return"] = out["Close"].pct_change()
    out["SMA_20"] = out["Close"].rolling(20).mean()
    out["SMA_50"] = out["Close"].rolling(50).mean()
    out["EMA_20"] = out["Close"].ewm(span=20, adjust=False).mean()
    out["Volatility_20"] = out["Return"].rolling(20).std() * np.sqrt(252)
    
    delta = out["Close"].diff()
    gain = (delta.clip(lower=0)).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    out["RSI_14"] = 100 - (100 / (1 + rs))
    
    out["ATR_14"] = (out["High"] - out["Low"]).rolling(14).mean() if {"High", "Low"}.issubset(out.columns) else np.nan
    ema12 = out["Close"].ewm(span=12, adjust=False).mean()
    ema26 = out["Close"].ewm(span=26, adjust=False).mean()
    out["MACD"] = ema12 - ema26
    out["MACD_Signal"] = out["MACD"].ewm(span=9, adjust=False).mean()
    out["MACD_Hist"] = out["MACD"] - out["MACD_Signal"]
    
    m = out["Close"].rolling(20).mean()
    s = out["Close"].rolling(20).std()
    out["BB_Mid"] = m
    out["BB_Upper"] = m + 2 * s
    out["BB_Lower"] = m - 2 * s
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

def sentiment_label(df):
    if len(df) < 2: return "Neutral"
    last = df.iloc[-1]
    score = 0
    if pd.notna(last["SMA_20"]) and pd.notna(last["SMA_50"]) and last["SMA_20"] > last["SMA_50"]:
        score += 1
    if pd.notna(last["RSI_14"]) and last["RSI_14"] < 60:
        score += 1
    if pd.notna(last["Volatility_20"]) and last["Volatility_20"] < 0.35:
        score += 1
    return "Positive" if score >= 2 else ("Neutral" if score == 1 else "Weak")

def backtest_crossover(df):
    d = df.dropna(subset=["SMA_20", "SMA_50"]).copy()
    if d.empty:
        return df.copy(), 0, 0, 0, 0, 0
    d["Signal"] = 0
    d.loc[d["SMA_20"] > d["SMA_50"], "Signal"] = 1
    d["Position"] = d["Signal"].diff().fillna(0)
    d["Strategy_Return"] = d["Return"] * d["Signal"].shift(1).fillna(0)
    d["Equity"] = (1 + d["Strategy_Return"].fillna(0)).cumprod()
    d["BuyHold"] = (1 + d["Return"].fillna(0)).cumprod()
    total_return = d["Equity"].iloc[-1] - 1 if len(d) > 0 else 0
    bh_return = d["BuyHold"].iloc[-1] - 1 if len(d) > 0 else 0
    trades = int((d["Position"] == 1).sum())
    win_days = int((d["Strategy_Return"] > 0).sum())
    loss_days = int((d["Strategy_Return"] < 0).sum())
    return d, total_return, bh_return, trades, win_days, loss_days

def forecast_arima(series, steps):
    clean = series.dropna()
    if len(clean) < 30: return None, None
    for order in [(1, 1, 1), (2, 1, 0)]:
        try:
            model = ARIMA(clean, order=order).fit()
            fc = model.get_forecast(steps=steps)
            return fc.predicted_mean, fc.conf_int()
        except:
            continue
    return None, None

def forecast_ets(series, steps):
    clean = series.dropna()
    if len(clean) < 30: return None
    try:
        model = ExponentialSmoothing(clean, trend="add", seasonal=None).fit(optimized=True)
        return model.forecast(steps)
    except:
        return None

def forecast_metrics(actual, pred):
    n = min(len(actual), len(pred))
    if n < 2: return 0, 0, 0
    a = actual[-n:]
    p = pred[-n:]
    mae = mean_absolute_error(a, p)
    rmse = sqrt(mean_squared_error(a, p))
    mape = np.mean(np.abs((a - p) / np.where(a == 0, np.nan, a))) * 100
    return mae, rmse, mape

def anchored_vwap(df, anchor_idx=None):
    d = df.copy()
    if anchor_idx is None:
        anchor_idx = max(0, len(d) - 60)
    d = d.iloc[anchor_idx:].copy()
    if d.empty or "Volume" not in d.columns or d["Volume"].sum() == 0:
        return pd.Series(dtype=float)
    typical = (d["High"] + d["Low"] + d["Close"]) / 3
    avwap = (typical * d["Volume"]).cumsum() / d["Volume"].cumsum()
    avwap.index = d["Date"]
    return avwap

def volume_profile(df, bins=20):
    d = df.copy()
    if d.empty or "Volume" not in d.columns or d["Volume"].sum() == 0:
        return pd.DataFrame()
    p_min, p_max = float(d["Low"].min()), float(d["High"].max())
    if p_max <= p_min: return pd.DataFrame()
    edges = np.linspace(p_min, p_max, bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2
    bucket = pd.cut(d["Close"], bins=edges, include_lowest=True, labels=False)
    vol = d.groupby(bucket, observed=False)["Volume"].sum().reindex(range(bins), fill_value=0).values
    vp = pd.DataFrame({"price": centers, "volume": vol})
    poc = vp.loc[vp["volume"].idxmax(), "price"] if not vp.empty else np.nan
    return vp.assign(POC=poc, VAH=p_max * 0.95, VAL=p_min * 1.05)

def liquidity_sweep(df, lookback=20):
    d = df.copy()
    if len(d) < lookback + 2: return "None", None
    recent = d.iloc[-lookback - 1 : -1]
    last = d.iloc[-1]
    prev_high, prev_low = recent["High"].max(), recent["Low"].min()
    if last["Low"] < prev_low and last["Close"] > prev_low:
        return "Bullish Sweep", float(prev_low)
    if last["High"] > prev_high and last["Close"] < prev_high:
        return "Bearish Sweep", float(prev_high)
    return "None", None

def fvg_zones(df):
    d = df.copy()
    zones = []
    if len(d) < 3: return zones
    for i in range(2, len(d)):
        c1, c3 = d.iloc[i - 2], d.iloc[i]
        if c3["Low"] > c1["High"]:
            zones.append(("Bullish FVG", float(c1["High"]), float(c3["Low"]), d.iloc[i]["Date"]))
        elif c3["High"] < c1["Low"]:
            zones.append(("Bearish FVG", float(c3["High"]), float(c1["Low"]), d.iloc[i]["Date"]))
    return zones

def amd_state(df):
    if len(df) < 20: return "Unknown"
    trend = df["Close"].iloc[-1] - df["Close"].iloc[-15]
    return "Distribution" if trend > 0 else "Accumulation"


# Main Core Framework Execution
if st.session_state.trigger_analysis:
    main_ticker = st.session_state.main_ticker
    base = download_stock(main_ticker, period, interval)
    
    if base.empty:
        st.error(f"⚠️ No historical price records could be loaded for target identifier: '{main_ticker}'. Verify the symbol formatting on Yahoo Finance.")
    else:
        base = add_indicators(base)
        last_close = float(base["Close"].iloc[-1])
        ytd_return = float((base["Close"].iloc[-1] / base["Close"].iloc[0] - 1) * 100)
        annual_vol = float(base["Volatility_20"].iloc[-1]) if pd.notna(base["Volatility_20"].iloc[-1]) else 0.0
        
        signal = signal_label(base)
        sentiment = sentiment_label(base)
        backtested, strat_ret, bh_ret, trades, win_days, loss_days = backtest_crossover(base)
        
        steps = forecast_days if interval == "1d" else max(4, forecast_days // 5)
        arima_pred, arima_ci = forecast_arima(base["Close"], steps)
        ets_pred = forecast_ets(base["Close"], steps)
        
        split_idx = int(len(base) * backtest_split / 100)
        mae, rmse, mape = 0, 0, 0
        if split_idx > 15:
            try:
                eval_model = ARIMA(base["Close"].iloc[:split_idx].dropna(), order=(1,1,1)).fit()
                eval_fc = eval_model.get_forecast(steps=len(base) - split_idx)
                mae, rmse, mape = forecast_metrics(base["Close"].iloc[split_idx:].values, eval_fc.predicted_mean.values)
            except: pass

        # 1. ENHANCED GLASSMORPHIC KPI BOARD
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(
                f"""
                <div style="background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(255,255,255,0.08); backdrop-filter: blur(12px); border-radius: 16px; padding: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.25);">
                    <p style="margin:0; font-size:0.85rem; color: #94a3b8; font-weight:600; text-transform: uppercase; letter-spacing: 0.05em;">Last Close</p>
                    <h2 style="margin: 8px 0 0 0; font-size:1.8rem; font-weight:800; color:#ffffff;">₹{last_close:,.2f}</h2>
                    <span style="font-size:0.75rem; color:#00d4aa; background:rgba(0,212,170,0.1); padding: 2px 8px; border-radius:999px; font-weight:700;">● Live Feed</span>
                </div>
                """, 
                unsafe_allow_html=True
            )

        with c2:
            ret_color = "#00d4aa" if ytd_return >= 0 else "#ef4444"
            ret_bg = "rgba(0,212,170,0.1)" if ytd_return >= 0 else "rgba(239,68,68,0.1)"
            st.markdown(
                f"""
                <div style="background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(255,255,255,0.08); backdrop-filter: blur(12px); border-radius: 16px; padding: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.25);">
                    <p style="margin:0; font-size:0.85rem; color: #94a3b8; font-weight:600; text-transform: uppercase; letter-spacing: 0.05em;">Period Return</p>
                    <h2 style="margin: 8px 0 0 0; font-size:1.8rem; font-weight:800; color:{ret_color};">{ytd_return:+.2f}%</h2>
                    <span style="font-size:0.75rem; color:{ret_color}; background:{ret_bg}; padding: 2px 8px; border-radius:999px; font-weight:700;">{'▲' if ytd_return >= 0 else '▼'} Performance</span>
                </div>
                """, 
                unsafe_allow_html=True
            )

        with c3:
            vol_color = "#ef4444" if annual_vol > 0.30 else "#38bdf8"
            vol_bg = "rgba(239,68,68,0.1)" if annual_vol > 0.30 else "rgba(56,189,248,0
