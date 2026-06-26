import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go

st.set_page_config(page_title="Alpha Surge — Smart Money Engine v2", page_icon="⚡", layout="wide")

# ==========================================================
# FRIENDS DESIGN SYSTEM: CYBERPUNK CSS INJECTION
# ==========================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Space+Mono&family=Inter:wght@300;400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Global Base Theme Styling */
.stApp {
    background: linear-gradient(180deg, #020b14 0%, #071220 100%) !important;
    color: #ddeeff !important;
}
section[data-testid="stSidebar"] {
    background: rgba(2, 11, 20, 0.85) !important;
    border-right: 1px solid rgba(0, 200, 255, 0.1) !important;
}

/* Typography Overrides */
h1, h2, h3 { font-family: 'Orbitron', sans-serif !important; letter-spacing: 2px; }
code, pre { font-family: 'Space Mono', monospace !important; }

/* Custom Premium Sidebar Inputs */
.stNumericInput input, .stSelectbox div {
    background: #0a1928 !important;
    color: #ddeeff !important;
    border: 1px solid rgba(0, 200, 255, 0.2) !important;
}

/* Neon Components & Card Frames */
.premium-card {
    background: #071220;
    border: 1px solid rgba(0, 200, 255, 0.1);
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 15px;
    box-shadow: 0 4px 25px rgba(0,0,0,0.4);
}
.premium-card:hover {
    border-color: rgba(0, 200, 255, 0.3);
    box-shadow: 0 0 15px rgba(0, 200, 255, 0.15);
}

/* Ticker Marquee CSS Animation */
.marquee-container {
    background: rgba(0,0,0,0.5);
    border-bottom: 1px solid rgba(0,200,255,0.15);
    overflow: hidden;
    padding: 6px 0;
    white-space: nowrap;
}
.marquee-track {
    display: inline-block;
    animation: marquee 35s linear infinite;
}
@keyframes marquee {
    0% { transform: translate3d(0, 0, 0); }
    100% { transform: translate3d(-50%, 0, 0); }
}
.marquee-item {
    display: inline-block;
    margin-right: 40px;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
}
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================================
# INTRODUCTORY INTERSTITIAL ENGINE MOCK LOADER
# ==========================================================
if "app_loaded" not in st.session_state:
    st.session_state.app_loaded = False

if not st.session_state.app_loaded:
    load_placeholder = st.empty()
    steps = [
        "Connecting to Financial Core Gateways...",
        "Fetching real-time asset universe quotes...",
        "Running multi-factor tactical engine...",
        "Compiling active risk & sizing metrics...",
        "Ready ✅"
    ]
    
    for idx, step_msg in enumerate(steps):
        progress_pct = int(((idx + 1) / len(steps)) * 100)
        with load_placeholder.container():
            st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style='text-align: center;'>
                    <h2 style='color: #00c8ff; font-size: 32px; font-weight: 900;'>ALPHA SURGE</h2>
                    <p style='font-family: "Space Mono", monospace; color: #4a7090;'>SMART MONEY ENGINE v2</p>
                    <div style='width: 320px; background: rgba(255,255,255,0.05); height: 4px; border-radius: 2px; margin: 20px auto; overflow: hidden;'>
                        <div style='width: {progress_pct}%; background: linear-gradient(90deg, #00c8ff, #7c4dff); height: 100%; transition: width 0.3s;'></div>
                    </div>
                    <p style='font-family: "Space Mono", monospace; font-size: 11px; color: #6a90aa;'>{step_msg}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        time.sleep(0.35)
    
    st.session_state.app_loaded = True
    load_placeholder.empty()
    st.rerun()

# ==========================================================
# MEMORY LAYER, INDICATORS & TICKER SELECTION OBJECTS
# ==========================================================
if "cached_batch_data" not in st.session_state:
    st.session_state.cached_batch_data = None
if "cached_timestamp" not in st.session_state:
    st.session_state.cached_timestamp = None

@st.cache_data(ttl=86400)
def load_stock_universe():
    # Elite liquid listings across core sectors of the Indian economy (NSE)
    nse_symbols = [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN", "ICICIBANK", "BHARTIARTL", "LTIM", "ITC", "LT",
        "HINDUNILVR", "BAJFINANCE", "TATAMOTORS", "AXISBANK", "WIPRO", "HCLTECH", "SUNPHARMA", "NTPC",
        "POWERGRID", "TITAN", "COALINDIA", "ONGC", "ADANIENT", "JIOFIN", "TATASTEEL", "ULTRACEMCO"
    ]
    data = {
        "company": [f"{sym} Traded Security" for sym in nse_symbols],
        "symbol": nse_symbols,
        "ticker": [f"{sym}.NS" for sym in nse_symbols],
        "exchange": ["NSE"] * len(nse_symbols)
    }
    uni = pd.DataFrame(data)
    uni["display"] = uni["symbol"] + " | " + uni["company"]
    return uni

universe = load_stock_universe()

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

def get_signal(df):
    if len(df) < 2: return "HOLD"
    last = df.iloc[-1]
    if pd.isna(last["SMA_20"]) or pd.isna(last["SMA_50"]) or pd.isna(last["RSI_14"]): return "HOLD"
    if last["SMA_20"] > last["SMA_50"] and last["RSI_14"] < 65: return "BUY"
    if last["SMA_20"] < last["SMA_50"] or last["RSI_14"] > 75: return "SELL"
    return "HOLD"

# ==========================================================
# APPLICATION HEADER FRAME
# ==========================================================
st.markdown(
    """
    <div style='display: flex; justify-content: space-between; align-items: center; padding: 10px 0;'>
        <div>
            <span style='font-family: "Orbitron", sans-serif; font-size: 20px; font-weight: 900; color: #00c8ff;'>ALPHA SURGE</span>
            <span style='font-family: "Space Mono", monospace; font-size: 10px; color: #4a7090; margin-left: 10px;'>SMART MONEY ENGINE v2</span>
        </div>
        <div style='font-family: "Space Mono", monospace; font-size: 11px; color: #00e87a;'>
            ● REGULATED MARKET CORE CONNECTED
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Ticker Tape Marquee
st.markdown(
    """
    <div class="marquee-container">
        <div class="marquee-track">
            <span class="marquee-item"><span style="color:#00c8ff">RELIANCE</span> ₹2,450.20 <span style="color:#00e87a">+1.4%</span></span>
            <span class="marquee-item"><span style="color:#00c8ff">TCS</span> ₹3,890.40 <span style="color:#ff3355">-0.8%</span></span>
            <span class="marquee-item"><span style="color:#00c8ff">HDFCBANK</span> ₹1,610.15 <span style="color:#00e87a">+2.1%</span></span>
            <span class="marquee-item"><span style="color:#00c8ff">INFY</span> ₹1,480.60 <span style="color:#ff3355">-1.2%</span></span>
            <span class="marquee-item"><span style="color:#00c8ff">SBIN</span> ₹725.40 <span style="color:#00e87a">+0.5%</span></span>
            <span class="marquee-item"><span style="color:#00c8ff">RELIANCE</span> ₹2,450.20 <span style="color:#00e87a">+1.4%</span></span>
            <span class="marquee-item"><span style="color:#00c8ff">TCS</span> ₹3,890.40 <span style="color:#ff3355">-0.8%</span></span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# CONTROL CONSOLE SIDEBAR
# ==========================================================
with st.sidebar:
    st.markdown("<h3 style='color: #00c8ff; font-size: 14px;'>⚙️ CONTROL CONSOLE</h3>", unsafe_allow_html=True)
    allocated_capital = st.number_input("Trade Allocation (₹)", min_value=1000, value=100000, step=5000)
    risk_per_trade = st.slider("Trade Max Sizing Risk (%)", 0.5, 5.0, 1.5, step=0.1)
    risk_reward_ratio = st.slider("Target Profit Matrix (1:X)", 1.5, 4.0, 2.0, step=0.5)
    
    st.markdown("---")
    st.markdown("<h3 style='color: #00c8ff; font-size: 14px;'>🎛️ HISTORICAL ENGINE</h3>", unsafe_allow_html=True)
    period = st.selectbox("Interval Backfill Length", ["5y", "3y", "1y"], index=2)
    interval = st.selectbox("Execution Frame", ["1d", "1wk"], index=0)

# ==========================================================
# INTERFACE NAVIGATION TABS
# ==========================================================
view_tab, scan_tab, market_tab = st.tabs([
    "🔍 SINGLE ASSET ANALYSIS", 
    "🎯 BROAD QUANT SCANNER", 
    "📊 SYSTEM CORE METRICS"
])

# ----------------------------------------------------------
# OPTIMIZATION A: BULK ENGINE DATA CACHE COMPILATION
# ----------------------------------------------------------
all_tickers = universe["ticker"].tolist()
if st.session_state.cached_batch_data is NULL or st.sidebar.button("🔄 FORCE RE-DOWNLOAD DATA POOL"):
    with st.spinner("Executing Vectorized Multi-Download Stream..."):
        try:
            st.session_state.cached_batch_data = yf.download(all_tickers, period="1y", interval="1d", group_by='ticker', auto_adjust=False, progress=False)
            st.session_state.cached_timestamp = time.strftime("%H:%M:%S")
        except Exception as e:
            st.error(f"Global download execution block interrupted: {e}")

# ----------------------------------------------------------
# TAB 1: SINGLE ASSET FOCUS ANALYTICS
# ----------------------------------------------------------
with view_tab:
    selected_display = st.selectbox("Select Target Core Instrument", options=universe["display"].tolist(), index=0)
    ticker_symbol = universe[universe["display"] == selected_display].iloc[0]["ticker"]
    
    raw_data = st.session_state.cached_batch_data
    if raw_data is not None:
        try:
            if isinstance(raw_data.columns, pd.MultiIndex):
                df_asset = raw_data[ticker_symbol].dropna(subset=["Close"]).reset_index()
            else:
                df_asset = raw_data.dropna(subset=["Close"]).reset_index()
                
            if not df_asset.empty:
                df = add_indicators(df_asset)
                last_row = df.iloc[-1]
                last_close = float(last_row["Close"])
                signal = get_signal(df)
                
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.markdown(f'<div class="premium-card"><p style="color:#4a7090; font-size:10px; margin:0;">LAST PRICE</p><h3 style="color:#ddeeff; margin:5px 0 0 0;">₹{last_close:,.2f}</h3></div>', unsafe_allow_html=True)
                with m2:
                    st.markdown(f'<div class="premium-card"><p style="color:#4a7090; font-size:10px; margin:0;">RSI SYSTEM (14)</p><h3 style="color:#00c8ff; margin:5px 0 0 0;">{last_row["RSI_14"]:.1f}</h3></div>', unsafe_allow_html=True)
                with m3:
                    color_map = {"BUY": "#00e87a", "SELL": "#ff3355", "HOLD": "#ffcc00"}
                    st.markdown(f'<div class="premium-card"><p style="color:#4a7090; font-size:10px; margin:0;">TACTICAL BIAS</p><h3 style="color:{color_map.get(signal, "#fff")}; margin:5px 0 0 0;">{signal}</h3></div>', unsafe_allow_html=True)
                with m4:
                    vol = last_row["Volatility_20"] if pd.notna(last_row["Volatility_20"]) else 0.0
                    st.markdown(f'<div class="premium-card"><p style="color:#4a7090; font-size:10px; margin:0;">ANNUALIZED VOLATILITY</p><h3 style="color:#7c4dff; margin:5px 0 0 0;">{vol:.1%}</h3></div>', unsafe_allow_html=True)
                    
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Close Price", line=dict(color="#00c8ff", width=2)))
                if "SMA_20" in df.columns:
                    fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA_20"], name="SMA 20", line=dict(color="#00e87a", width=1.5, dash="dash")))
                fig.update_layout(
                    margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#ddeeff"), height=400,
                    xaxis=dict(gridcolor="rgba(0,200,255,0.05)"), yaxis=dict(gridcolor="rgba(0,200,255,0.05)")
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Asset compiling fault: {e}")

# ----------------------------------------------------------
# TAB 2: INSTANT CALCULATING BROAD QUANT SCANNER
# ----------------------------------------------------------
with scan_tab:
    st.markdown("<h3 style='font-size:16px;'>🚀 WHOLE-MARKET POSITION INSTANT MATRIX</h3>", unsafe_allow_html=True)
    if st.session_state.cached_timestamp:
        st.markdown(f"<p style='font-size:11px; color:#4a7090; font-family:\"Space Mono\";'>Memory Cache Active. Last download anchor: {st.session_state.cached_timestamp}</p>", unsafe_allow_html=True)
        
    raw_batch = st.session_state.cached_batch_data
    if raw_batch is not None:
        scan_results = []
        for ticker in all_tickers:
            try:
                if isinstance(raw_batch.columns, pd.MultiIndex):
                    if ticker not in raw_batch.columns.levels[0]: continue
                    ticker_df = raw_batch[ticker].dropna(subset=["Close"]).reset_index()
                else:
                    ticker_df = raw_batch.dropna(subset=["Close"]).reset_index()
                    
                if len(ticker_df) < 20: continue
                calc_df = add_indicators(ticker_df)
                last_s_row = calc_df.iloc[-1]
                
                sig = get_signal(calc_df)
                c_price = float(last_s_row["Close"])
                atr = last_s_row["ATR_14"] if pd.notna(last_s_row["ATR_14"]) else (c_price * 0.02)
                
                sl_val = c_price - (atr * 1.5)
                tp_val = c_price + ((atr * 1.5) * risk_reward_ratio)
                capital_at_risk = allocated_capital * (risk_per_trade / 100.0)
                units = int(capital_at_risk // (atr * 1.5)) if atr > 0 else 0
                
                scan_results.append({
                    "Asset Ticker": ticker.replace(".NS", ""),
                    "Current Quote": f"₹{c_price:,.2f}",
                    "RSI": f"{last_s_row['RSI_14']:.1f}",
                    "System Signal": sig,
                    "Allocation Units": f"{units} Share Units",
                    "Stop-Loss Threshold": f"₹{sl_val:,.2f}",
                    "Target Take-Profit": f"₹{tp_val:,.2f}"
                })
            except:
                continue
                
        if scan_results:
            df_final = pd.DataFrame(scan_results)
            b_tab, e_tab, m_tab = st.tabs([f"🟢 Active Buys ({len(df_final[df_final['System Signal']=='BUY'])})", f"🔴 Active Exits ({len(df_final[df_final['System Signal']=='SELL'])})", "🌐 Full Tracker Frame"])
            with b_tab: st.dataframe(df_final[df_final["System Signal"] == "BUY"], use_container_width=True, hide_index=True)
            with e_tab: st.dataframe(df_final[df_final["System Signal"] == "SELL"], use_container_width=True, hide_index=True)
            with m_tab: st.dataframe(df_final, use_container_width=True, hide_index=True)

# ----------------------------------------------------------
# TAB 3: DYNAMIC SECTOR HEATMAP & MOMENTUM ENGINE
# ----------------------------------------------------------
with market_tab:
    c_left, c_right = st.columns([2, 1])
    raw_batch = st.session_state.cached_batch_data
    
    # Pre-calculating variables dynamically from our operational pool
    heatmap_data = []
    bullish_nodes = 0
    total_nodes = 0
    
    if raw_batch is not None:
        for ticker in all_tickers:
            try:
                if isinstance(raw_batch.columns, pd.MultiIndex):
                    df_t = raw_batch[ticker].dropna(subset=["Close"])
                else:
                    df_t = raw_batch.dropna(subset=["Close"])
                
                if len(df_t) < 5: continue
                # Calculation loops
                close_today = float(df_t["Close"].iloc[-1])
                close_yesterday = float(df_t["Close"].iloc[-2])
                pct_change = ((close_today - close_yesterday) / close_yesterday) * 100
                
                # Sizing trend metrics for gauge
                sma20 = df_t["Close"].rolling(20).mean().iloc[-1]
                if close_today > sma20:
                    bullish_nodes += 1
                total_nodes += 1
                
                heatmap_data.append({
                    "symbol": ticker.replace(".NS", ""),
                    "pct": pct_change,
                    "txt": "#00e87a" if pct_change >= 0 else "#ff3355",
                    "bg": "rgba(0, 232, 122, 0.15)" if pct_change >= 0 else "rgba(255, 51, 85, 0.15)"
                })
            except:
                continue

    # OPTIMIZATION B: LIVE SECTORAL HEATMAP INTERFACE MIGRATION
    with c_left:
        st.markdown("<h3 style='font-size:15px;'>🎨 DYNAMIC MARKET HEATMAP MATRIX</h3>", unsafe_allow_html=True)
        if heatmap_data:
            h_cols = st.columns(4)
            for idx, item in enumerate(heatmap_data[:16]): # Limit grid items to fit space
                target_col = h_cols[idx % 4]
                target_col.markdown(
                    f"""
                    <div style='background: {item["bg"]}; border: 1px solid {item["txt"]}44; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 10px;'>
                        <div style='font-family: "Orbitron", sans-serif; font-size: 13px; font-weight: 900;'>{item["symbol"]}</div>
                        <div style='font-family: "Space Mono", monospace; font-size: 11px; margin-top: 4px; color: {item["txt"]};'>{item["pct"]:+.2f}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
    # OPTIMIZATION C: DYNAMIC MARKET FEAR & GREED SENTIMENT QUOTIENT GAUGE
    with c_right:
        st.markdown("<h3 style='font-size:15px;'>📊 SENTIMENT QUOTIENT</h3>", unsafe_allow_html=True)
        sentiment_score = int((bullish_nodes / total_nodes) * 100) if total_nodes > 0 else 50
        
        if sentiment_score >= 70: label, hue = "EXTREME GREED", "#00e87a"
        elif sentiment_score >= 55: label, hue = "TACTICAL GREED", "#00c8ff"
        elif sentiment_score >= 45: label, hue = "NEUTRAL BIAS", "#ffcc00"
        else: label, hue = "FEAR CORRECTION", "#ff3355"
        
        st.markdown(
            f"""
            <div class="premium-card" style="text-align: center;">
                <p style="font-family: 'Space Mono', monospace; font-size: 10px; color:#4a7090; margin:0;">BREADTH MOMENTUM INDEX</p>
                <h1 style="color: {hue}; font-size: 48px; margin: 10px 0;">{sentiment_score}</h1>
                <div style="font-family: 'Space Mono', monospace; font-size: 12px; color: {hue}; letter-spacing: 2px;">{label}</div>
                <div style="width: 100%; background: rgba(255,255,255,0.05); height: 6px; border-radius: 3px; margin-top:15px; overflow:hidden;">
                    <div style="width: {sentiment_score}%; background: linear-gradient(90deg, #ff3355, {hue}); height:100%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
