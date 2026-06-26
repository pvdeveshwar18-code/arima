import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go

# ==========================================================
# 1. PREMIUM GLASSMORPHISM SYSTEM DESIGN (THEME NAME: XERCES)
# ==========================================================
st.set_page_config(page_title="XERCES // ENGINE", page_icon="⚡", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Space+Mono&family=Inter:wght@300;400;500;600&display=swap');

/* Main Framework Core Styles */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: radial-gradient(circle at 50% 0%, #0a192f 0%, #020813 100%) !important;
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] {
    background-color: rgba(3, 11, 24, 0.85) !important;
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(0, 200, 255, 0.12) !important;
}

/* Premium Sci-Fi Header UI */
.xerces-title {
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: 2.5rem;
    color: #00c8ff;
    letter-spacing: 4px;
    margin: 0;
    background: linear-gradient(90deg, #00c8ff, #00e87a);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 12px rgba(0, 200, 255, 0.3));
}
.telemetry-tag {
    font-family: 'Space Mono', monospace;
    color: #4a7090;
    font-size: 11px;
    letter-spacing: 1px;
}

/* Upgraded Glassmorphism Dashboard Cards */
.glass-card {
    background: rgba(7, 18, 32, 0.65);
    border: 1px solid rgba(0, 200, 255, 0.15);
    border-radius: 6px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    backdrop-filter: blur(4px);
}
.glass-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.7rem;
    font-weight: 700;
    margin-top: 4px;
}

/* High-Tech Custom Tabs */
div[data-baseweb="tab-list"] { gap: 6px; }
button[data-baseweb="tab"] {
    font-family: 'Space Mono', monospace !important;
    border-radius: 4px !important;
    background: rgba(10, 25, 40, 0.5) !important;
    color: #5a80a0 !important;
    border: 1px solid rgba(0, 200, 255, 0.08) !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.3s ease;
}
button[data-baseweb="tab"]:hover {
    color: #00c8ff !important;
    border-color: rgba(0, 200, 255, 0.3) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    border-color: #00c8ff !important;
    color: #00c8ff !important;
    background: rgba(13, 32, 53, 0.8) !important;
    box-shadow: 0 0 10px rgba(0, 200, 255, 0.15);
}
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================================
# 2. BRANDING HEADER PANEL & LIVE TELEMETRY LOGS
# ==========================================================
col_title, col_clock = st.columns([2, 1])
with col_title:
    st.markdown('<h1 class="xerces-title">XERCES // CORE ENGINE</h1>', unsafe_allow_html=True)
    st.markdown('<p class="telemetry-tag">[ QUANT SUBSYSTEM STATUS: ONLINE // FIVE-FACTOR ANALYSIS CORES OPERATIONAL ]</p>', unsafe_allow_html=True)

with col_clock:
    current_time = datetime.datetime.now().strftime("%H:%M:%S UTC")
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    st.markdown(
        f"""
        <div style="text-align: right; font-family: 'Space Mono', monospace; font-size: 12px; color: #6a90aa; background: rgba(7,18,32,0.4); padding: 8px; border-radius: 4px; border: 1px solid rgba(0,200,255,0.05);">
            <div>SYSTEM CLOCK: <span style="color:#ffcc00; font-weight:bold;">{current_time}</span></div>
            <div>STATION VECTOR: <span style="color:#00c8ff;">{current_date}</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<hr style='border-color: rgba(0,200,255,0.15); margin: 0.85rem 0;'>", unsafe_allow_html=True)

# ==========================================================
# 3. CORE STRATEGY ALGORITHMIC MATHEMATICS
# ==========================================================
@st.cache_data(ttl=86400)
def load_stock_universe():
    nse_symbols = [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN", "ICICIBANK", "BHARTIARTL", "LTIM", "ITC", "LT"
    ]
    data = {
        "symbol": nse_symbols,
        "ticker": [f"{sym}.NS" for sym in nse_symbols],
    }
    return pd.DataFrame(data)

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

if "last_scan_data" not in st.session_state:
    st.session_state.last_scan_data = None

# ==========================================================
# 4. SIDEBAR PANEL: CONTROL HUB & MULTI-STOCK RUN ENGINE
# ==========================================================
with st.sidebar:
    st.markdown("<p class='telemetry-tag' style='color:#00c8ff; font-weight:700; margin-bottom:5px;'>[ 🛡️ RISK MATRIX MANAGEMENT ]</p>", unsafe_allow_html=True)
    allocated_capital = st.number_input("Capital Pool (₹)", min_value=1000, value=100000, step=5000)
    risk_per_trade = st.slider("Max Capital Risk per Unit (%)", 0.5, 5.0, 1.5, step=0.1)
    risk_reward_ratio = st.slider("Target Risk Vector Ratio (1:X)", 1.5, 4.0, 2.0, step=0.5)
    
    st.markdown("---")
    st.markdown("<p class='telemetry-tag' style='color:#00c8ff; font-weight:700; margin-bottom:5px;'>[ 📡 AGGREGATE SCREENING HUB ]</p>", unsafe_allow_html=True)
    
    if st.button("⚡ EXECUTE WHOLE-MARKET MATRIX SCAN", use_container_width=True):
        all_tickers = universe["ticker"].tolist()
        scan_results = []
        scan_bar = st.progress(0, text="Iterating core tickers...")
        
        for idx, ticker in enumerate(all_tickers):
            try:
                tk_df = yf.download(ticker, period="6mo", interval="1d", auto_adjust=False, progress=False)
                if tk_df is None or tk_df.empty: 
                    continue
                
                if isinstance(tk_df.columns, pd.MultiIndex):
                    tk_df.columns = [c[0] for c in tk_df.columns]
                tk_df = tk_df.reset_index()
                
                calc_df = add_indicators(tk_df)
                last_s_row = calc_df.iloc[-1]
                prev_s_row = calc_df.iloc[-2]
                
                sig = get_signal(calc_df)
                c_price = float(last_s_row["Close"])
                p_price = float(prev_s_row["Close"])
                pct_change = ((c_price - p_price) / p_price) * 100
                
                atr = last_s_row["ATR_14"] if pd.notna(last_s_row["ATR_14"]) else (c_price * 0.02)
                sl_val = c_price - (atr * 1.5)
                tp_val = c_price + ((atr * 1.5) * risk_reward_ratio)
                capital_at_risk = allocated_capital * (risk_per_trade / 100.0)
                units = int(capital_at_risk // (atr * 1.5)) if atr > 0 else 0
                
                above_trend = c_price > last_s_row["SMA_20"]
                
                scan_results.append({
                    "Ticker": ticker.replace(".NS", ""),
                    "Price": f"₹{c_price:,.2f}",
                    "RSI": f"{last_s_row['RSI_14']:.1f}",
                    "Signal": sig,
                    "Target Size": f"{units} Units",
                    "Stop-Loss": f"₹{sl_val:,.2f}",
                    "Take-Profit": f"₹{tp_val:,.2f}",
                    "raw_signal": sig,
                    "pct_change": pct_change,
                    "above_trend": above_trend
                })
            except:
                continue
            scan_bar.progress((idx + 1) / len(all_tickers), text=f"Analyzing data arrays: {ticker}")
            
        if scan_results:
            st.session_state.last_scan_data = scan_results
            st.sidebar.success("XERCES matrix updated completely.")

# ==========================================================
# 5. ALL 5 ORIGINAL PRIMARY WORKSPACE NAVIGATION TABS RESTORED
# ==========================================================
view_tab, backtest_tab, paper_tab, settings_tab, help_tab = st.tabs([
    "🔍 TERMINAL ANALYSIS", 
    "📈 BACKTEST ENGINE",
    "💵 REAL-TIME PAPER TRADING",
    "⚙️ STRATEGY SETTINGS",
    "❓ ENGINE CORE MANUAL"
])

# ----------------------------------------------------------
# TAB 1: ADVANCED INDIVIDUAL ASSET CHART TERMINAL
# ----------------------------------------------------------
with view_tab:
    selected_ticker = st.selectbox("SELECT RADAR PROBE ASSET TICKER", options=universe["symbol"].tolist(), index=0)
    full_ticker = f"{selected_ticker}.NS"
    
    with st.spinner("Decoding asset streams..."):
        try:
            df_asset = yf.download(full_ticker, period="1y", interval="1d", auto_adjust=False, progress=False)
            if df_asset is not None and not df_asset.empty:
                if isinstance(df_asset.columns, pd.MultiIndex):
                    df_asset.columns = [c[0] for c in df_asset.columns]
                df_asset = df_asset.reset_index()
                
                df = add_indicators(df_asset)
                last_row = df.iloc[-1]
                last_close = float(last_row["Close"])
                signal = get_signal(df)
                
                # Upgraded Glassmorphic Metrics Row
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.markdown(f'<div class="glass-card"><p class="telemetry-tag" style="margin:0;">[ LAST TICK PRICE ]</p><div class="glass-value" style="color:#ddeeff;">₹{last_close:,.2f}</div></div>', unsafe_allow_html=True)
                with m2:
                    st.markdown(f'<div class="glass-card"><p class="telemetry-tag" style="margin:0;">[ RSI MOMENTUM ]</p><div class="glass-value" style="color:#00c8ff;">{last_row["RSI_14"]:.1f}</div></div>', unsafe_allow_html=True)
                with m3:
                    color_map = {"BUY": "#00e87a", "SELL": "#ff3355", "HOLD": "#ffcc00"}
                    st.markdown(f'<div class="glass-card"><p class="telemetry-tag" style="margin:0;">[ MATCH ENGINE BIAS ]</p><div class="glass-value" style="color:{color_map.get(signal)};">{signal}</div></div>', unsafe_allow_html=True)
                with m4:
                    vol = last_row["Volatility_20"] if pd.notna(last_row["Volatility_20"]) else 0.0
                    st.markdown(f'<div class="glass-card"><p class="telemetry-tag" style="margin:0;">[ SIGMA VOLATILITY ]</p><div class="glass-value" style="color:#7c4dff;">{vol:.1%}</div></div>', unsafe_allow_html=True)
                
                # Plotly Chart Frame Accent
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Close Value", line=dict(color="#00c8ff", width=2)))
                if "SMA_20" in df.columns:
                    fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA_20"], name="SMA 20 Core", line=dict(color="#00e87a", width=1.5, dash="dash")))
                fig.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#ddeeff", family="Space Mono"), height=350,
                    xaxis=dict(gridcolor="rgba(0,200,255,0.05)"), yaxis=dict(gridcolor="rgba(0,200,255,0.05)")
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error compiling asset chart data: {e}")

    # Background Multi-Stock Grid Display Block (Triggered via Sidebar)
    if st.session_state.last_scan_data is not None:
        st.markdown("<p class='telemetry-tag' style='color:#00c8ff; font-size:15px; font-weight:700; margin-top:25px;'>
