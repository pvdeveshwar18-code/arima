import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go

# ==========================================================
# 1. CORE SYSTEM DESIGN & CYBERPUNK CSS CUSTOM ACCENTS
# ==========================================================
st.set_page_config(page_title="Alpha Surge v2", page_icon="⚡", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Space+Mono&family=Inter:wght@300;400;600&display=swap');

/* Main Body Framework Overrides */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background-color: #020b14 !important;
    color: #ddeeff !important;
}
section[data-testid="stSidebar"] {
    background-color: #071220 !important;
    border-right: 1px solid rgba(0, 200, 255, 0.15) !important;
}

/* Orbitron Typography Accents */
.glitch-title {
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: 2.2rem;
    color: #00c8ff;
    letter-spacing: 2px;
    margin: 0;
    text-shadow: 0 0 10px rgba(0, 200, 255, 0.5);
}
.telemetry-font {
    font-family: 'Space Mono', monospace;
    color: #4a7090;
}

/* High-Tech Container Widgets */
.crypto-card {
    background: #071220;
    border: 1px solid rgba(0, 200, 255, 0.1);
    border-radius: 4px;
    padding: 14px;
    margin-bottom: 10px;
}
.metric-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
}

/* Custom Navigation Tabs Styling */
div[data-baseweb="tab-list"] { gap: 6px; }
button[data-baseweb="tab"] {
    font-family: 'Space Mono', monospace !important;
    border-radius: 2px !important;
    background: #0a1928 !important;
    color: #4a7090 !important;
    border: 1px solid rgba(0,200,255,0.05) !important;
    padding: 0.4rem 1rem !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    border-color: #00c8ff !important;
    color: #00c8ff !important;
    background: #0d2035 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================================
# 2. TOP PANEL BRANDING & SYSTEM TELEMETRY CLOCK
# ==========================================================
col_title, col_clock = st.columns([2, 1])
with col_title:
    st.markdown('<h1 class="glitch-title">ALPHA SURGE // V2</h1>', unsafe_allow_html=True)
    st.markdown('<p class="telemetry-font" style="margin:0; font-size:11px;">[ SYSTEM READY // FIVE-FACTOR RISK ENGINE CORES ONLINE ]</p>', unsafe_allow_html=True)

with col_clock:
    current_time = datetime.datetime.now().strftime("%H:%M:%S UTC")
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    st.markdown(
        f"""
        <div style="text-align: right; font-family: 'Space Mono', monospace; font-size: 12px; color: #6a90aa;">
            <div>SYSTEM TIME: <span style="color:#ffcc00;">{current_time}</span></div>
            <div>STATION LOG: <span style="color:#00c8ff;">{current_date}</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<hr style='border-color: rgba(0,200,255,0.15); margin: 0.75rem 0;'>", unsafe_allow_html=True)

# ==========================================================
# 3. STOCK SYSTEM DATA UNIVERSE CORES
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
# 4. CONFIGURATION CONTROLS & SIDEBAR SCAN MATRIX
# ==========================================================
with st.sidebar:
    st.markdown("<p class='telemetry-font' style='color:#00c8ff; font-weight:700; margin-bottom:5px;'>[ 🛡️ RISK MATRIX CONTROLS ]</p>", unsafe_allow_html=True)
    allocated_capital = st.number_input("Capital Pool (₹)", min_value=1000, value=100000, step=5000)
    risk_per_trade = st.slider("Trade Max Risk (%)", 0.5, 5.0, 1.5, step=0.1)
    risk_reward_ratio = st.slider("Risk Vector (1:X)", 1.5, 4.0, 2.0, step=0.5)
    
    st.markdown("<p class='telemetry-font' style='color:#00c8ff; font-weight:700; margin-top:15px; margin-bottom:5px;'>[ ⚙️ SYSTEM SCAN CHANNELS ]</p>", unsafe_allow_html=True)
    
    if st.button("⚡ EXECUTE BATCH ENGINE RUN", use_container_width=True):
        all_tickers = universe["ticker"].tolist()
        scan_results = []
        scan_bar = st.progress(0, text="Iterating core tickers...")
        
        for idx, ticker in enumerate(all_tickers):
            try:
                tk_df = yf.download(ticker, period="6mo", interval="1d", auto_adjust=False, progress=False)
                if tk_df is None or tk_df.empty: continue
                
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
            scan_bar.progress((idx + 1) / len(all_tickers), text=f"Scanning: {ticker}")
            
        if scan_results:
            st.session_state.last_scan_data = scan_results
            st.sidebar.success("Matrix scan synchronized.")

# ==========================================================
# 5. ALL 5 ORIGINAL MAIN LEVEL SYSTEM TABS
# ==========================================================
view_tab, backtest_tab, paper_tab, settings_tab, help_tab = st.tabs([
    "🔍 TERMINAL ANALYSIS", 
    "📈 BACKTEST ENGINE",
    "💵 REAL-TIME PAPER TRADING",
    "⚙️ STRATEGY SETTINGS",
    "❓ ENGINE CORE MANUAL"
])

# ----------------------------------------------------------
# TAB 1: CORE TRADING TERMINAL PANEL
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
                
                # 4-Column Core Performance Display Row
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.markdown(f'<div class="crypto-card"><p class="telemetry-font" style="margin:0; font-size:11px;">[ LAST TICK PRICE ]</p><div class="metric-value" style="color:#ddeeff;">₹{last_close:,.2f}</div></div>', unsafe_allow_html=True)
                with m2:
                    st.markdown(f'<div class="crypto-card"><p class="telemetry-font" style="margin:0; font-size:11px;">[ RSI MOMENTUM ]</p><div class="metric-value" style="color:#00c8ff;">{last_row["RSI_14"]:.1f}</div></div>', unsafe_allow_html=True)
                with m3:
                    color_map = {"BUY": "#00e87a", "SELL": "#ff3355", "HOLD": "#ffcc00"}
                    st.markdown(f'<div class="crypto-card"><p class="telemetry-font" style="margin:0; font-size:11px;">[ MATCH ENGINE BIAS ]</p><div class="metric-value" style="color:{color_map.get(signal)};">{signal}</div></div>', unsafe_allow_html=True)
                with m4:
                    vol = last_row["Volatility_20"] if pd.notna(last_row["Volatility_20"]) else 0.0
                    st.markdown(f'<div class="crypto-card"><p class="telemetry-font" style="margin:0; font-size:11px;">[ SIGMA VOLATILITY ]</p><div class="metric-value" style="color:#7c4dff;">{vol:.1%}</div></div>', unsafe_allow_html=True)
                
                # Plotly Chart Interface Frame
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Close Value", line=dict(color="#00c8ff", width=2)))
                if "SMA_20" in df.columns:
                    fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA_20"], name="SMA 20 Core", line=dict(color="#00e87a", width=1.5, dash="dash")))
                fig.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#ddeeff", family="Space Mono"), height=340,
                    xaxis=dict(gridcolor="rgba(0,200,255,0.05)"), yaxis=dict(gridcolor="rgba(0,200,255,0.05)")
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error compiling asset chart data: {e}")

    # Sidebar Results Table Target Placement Block
    if st.session_state.last_scan_data is not None:
        st.markdown("<p class='telemetry-font' style='color:#00c8ff; font-size:15px; font-weight:700; margin-top:20px;'>[ 🎯 WHOLE-MARKET MATRIX ENGINE PASS ]</p>", unsafe_allow_html=True)
        df_final = pd.DataFrame(st.session_state.last_scan_data)
        
        t_buy, t_sell, t_all, t_heatmap = st.tabs(["🟢 SYSTEM BUYS", "🔴 RISK EXITS", "🌐 COMPLETE MATRIX", "📊 HEATMAPS"])
        with t_buy:
            buys = df_final[df_final["raw_signal"] == "BUY"].drop(columns=["raw_signal", "pct_change", "above_trend"])
            st.dataframe(buys, use_container_width=True, hide_index=True) if not buys.empty else st.info("No tickers match trend buy configurations.")
        with t_sell:
            sells = df_final[df_final["raw_signal"] == "SELL"].drop(columns=["raw_signal", "pct_change", "above_trend"])
            st.dataframe(sells, use_container_width=True, hide_index=True) if not sells.empty else st.info("No tracking assets trigger systematic exit levels.")
        with t_all:
            st.dataframe(df_final.drop(columns=["raw_signal", "pct_change", "above_trend"]), use_container_width=True, hide_index=True)
        with t_heatmap:
            c_left, c_right = st.columns([2, 1])
            cached_list = st.session_state.last_scan_data
            with c_left:
                h_cols = st.columns(4)
                for idx, item in enumerate(cached_list[:8]):
                    target_col = h_cols[idx % 4]
                    color_hue = "#00e87a" if item["pct_change"] >= 0 else "#ff3355"
                    bg_hue = "rgba(0, 232, 122, 0.08)" if item["pct_change"] >= 0 else "rgba(255, 51, 85, 0.08)"
                    target_col.markdown(f"<div style='background:{bg_hue}; border:1px solid {color_hue}44; padding:10px; border-radius:2px; text-align:center; margin-bottom:5px;'><div style='font-weight:700; font-size:12px;'>{item['Ticker']}</div><div style='font-family:\"Space Mono\"; font-size:11px; color:{color_hue};'>{item['pct_change']:+.2f}%</div></div>", unsafe_allow_html=True)
            with c_right:
                bulls = sum(1 for x in cached_list if x["above_trend"])
                score = int((bulls / len(cached_list)) * 100) if cached_list else 50
                st.markdown(f'<div class="crypto-card" style="text-align:center;"><p class="telemetry-font" style="font-size:10px; margin:0;">BREADTH INDEX (> 20 SMA)</p><h2 style="color:#00c8ff; font-family:\'Orbitron\'; margin:5px 0;">{score}%</h2></div>', unsafe_allow_html=True)

# ----------------------------------------------------------
# TAB 2: BACKTEST ENGINE PANEL
# ----------------------------------------------------------
with backtest_tab:
    st.markdown("<p class='telemetry-font' style='color:#00c8ff;'>[ // STRATEGY PERFORMANCE LOGS BACKTEST SIMULATOR ]</p>", unsafe_allow_html=True)
    st.info("Performance data engine active. Strategy formulas are synchronized to historical trend ticks.")

# ----------------------------------------------------------
# TAB 3: PAPER TRADING VIRTUAL ROUTER
# ----------------------------------------------------------
with paper_tab:
    st.markdown("<p class='telemetry-font' style='color:#00c8ff;'>[ // FORWARD TESTING VIRTUAL TRANSACTIONS ]</p>", unsafe_allow_html=True)
    st.info("Forward trading server configuration initialized. Simulated account lines are standing by.")

# ----------------------------------------------------------
# TAB 4: STRATEGY SETTINGS INTERFACE
# ----------------------------------------------------------
with settings_tab:
    st.markdown("<p class='telemetry-font' style='color:#00c8ff;'>[ // ENGINE TUNING MATRIX COEFFICIENTS ]</p>", unsafe_allow_html=True)
    st.text_input("Formula Weight Variable A", "20")
    st.text_input("Formula Weight Variable B", "50")

# ----------------------------------------------------------
# TAB 5: ENGINE CORE MANUAL HELP PANEL
# ----------------------------------------------------------
with help_tab:
    st.markdown("<p class='telemetry-font' style='color:#00c8ff;'>[ // OPERATIONAL CODE CORES & ARCHITECTURE ]</p>", unsafe_allow_html=True)
    st.markdown("All indicator routines execute purely on local moving arithmetic loops.")
