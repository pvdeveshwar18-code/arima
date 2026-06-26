import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go

# ==========================================================
# 1. XERCES PREMIUM SYSTEM STYLE CONFIGURATION
# ==========================================================
st.set_page_config(page_title="XERCES // QUANT ENGINE", page_icon="⚡", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Space+Mono&family=Inter:wght@300;400;500;600&display=swap');

/* Main Body Framework Styling */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: radial-gradient(circle at 50% 0%, #0a192f 0%, #020813 100%) !important;
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] {
    background-color: rgba(3, 11, 24, 0.9) !important;
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(0, 200, 255, 0.15) !important;
}

/* XERCES Visual Typography Branding */
.xerces-title {
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: 2.3rem;
    color: #00c8ff;
    letter-spacing: 3px;
    margin: 0;
    background: linear-gradient(90deg, #00c8ff, #00e87a);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 10px rgba(0, 200, 255, 0.25));
}
.telemetry-tag {
    font-family: 'Space Mono', monospace;
    color: #4a7090;
    font-size: 11px;
    letter-spacing: 1px;
}
.section-header {
    font-family: 'Orbitron', sans-serif;
    color: #00c8ff;
    font-size: 13px;
    letter-spacing: 1px;
    margin-top: 15px;
    margin-bottom: 10px;
}

/* Glassmorphism Structural Cards */
.glass-card {
    background: rgba(7, 18, 32, 0.65);
    border: 1px solid rgba(0, 200, 255, 0.15);
    border-radius: 4px;
    padding: 12px 16px;
    margin-bottom: 10px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(4px);
}
.glass-label {
    font-family: 'Space Mono', monospace;
    color: #6a90aa;
    font-size: 10px;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.glass-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    margin-top: 2px;
}

/* Upgraded Functional Navigation Matrix */
div[data-baseweb="tab-list"] { gap: 4px; }
button[data-baseweb="tab"] {
    font-family: 'Space Mono', monospace !important;
    border-radius: 4px !important;
    background: rgba(10, 25, 40, 0.4) !important;
    color: #5a80a0 !important;
    border: 1px solid rgba(0, 200, 255, 0.05) !important;
    padding: 0.4rem 1rem !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    border-color: #00c8ff !important;
    color: #00c8ff !important;
    background: rgba(13, 32, 53, 0.75) !important;
}
</style>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# 2. APPLICATION HEADER CORE TELEMETRY CLOCK
# ==========================================================
col_title, col_clock = st.columns([2, 1])
with col_title:
    st.markdown('<h1 class="xerces-title">XERCES // QUANT CORES</h1>', unsafe_allow_html=True)
    st.markdown('<p class="telemetry-tag">[ RADAR PROBE: ACTIVE // TELEMETRY FRAME INTEGRATED ]</p>', unsafe_allow_html=True)

with col_clock:
    current_time = datetime.datetime.now().strftime("%H:%M:%S UTC")
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    st.markdown(
        f"""
        <div style="text-align: right; font-family: 'Space Mono', monospace; font-size: 11px; color: #6a90aa; background: rgba(7,18,32,0.5); padding: 6px; border-radius: 4px; border: 1px solid rgba(0,200,255,0.08);">
            <div>CLOCK LOG: <span style="color:#ffcc00; font-weight:bold;">{current_time}</span></div>
            <div>STATION VECTOR: <span style="color:#00c8ff;">{current_date}</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<hr style='border-color: rgba(0,200,255,0.12); margin: 0.65rem 0;'>", unsafe_allow_html=True)

# ==========================================================
# 3. MATHEMATICAL STRATEGY CORES
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
# 4. SIDEBAR CONFIGURATION HUB & SYSTEM ENGINE
# ==========================================================
with st.sidebar:
    st.markdown("<p class='telemetry-tag' style='color:#00c8ff; font-weight:700; margin-bottom:5px;'>[ 🛡️ RISK MATRIX CONTROLS ]</p>", unsafe_allow_html=True)
    allocated_capital = st.number_input("Capital Pool (₹)", min_value=1000, value=100000, step=5000)
    risk_per_trade = st.slider("Max Sizing Risk (%)", 0.5, 5.0, 1.5, step=0.1)
    risk_reward_ratio = st.slider("Risk Vector (1:X)", 1.5, 4.0, 2.0, step=0.5)
    
    st.markdown("---")
    st.markdown("<p class='telemetry-tag' style='color:#00c8ff; font-weight:700; margin-bottom:5px;'>[ 📡 MULTI-STOCK RUN ENGINE ]</p>", unsafe_allow_html=True)
    
    if st.button("⚡ EXECUTE MATRIX BULK SCAN", use_container_width=True):
        all_tickers = universe["ticker"].tolist()
        scan_results = []
        scan_bar = st.progress(0, text="Iterating core arrays...")
        
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
            scan_bar.progress((idx + 1) / len(all_tickers), text=f"Syncing: {ticker}")
            
        if scan_results:
            st.session_state.last_scan_data = scan_results
            st.sidebar.success("XERCES matrix updated completely.")

# ==========================================================
# 5. CORE INTERFACE NAVIGATION WINDOWS
# ==========================================================
view_tab, backtest_tab, paper_tab, settings_tab, help_tab = st.tabs([
    "🔍 TERMINAL ANALYSIS", 
    "📈 BACKTEST ENGINE",
    "💵 REAL-TIME PAPER TRADING",
    "⚙️ STRATEGY SETTINGS",
    "❓ ENGINE CORE MANUAL"
])

# ----------------------------------------------------------
# TAB 1: TERMINAL ARCHITECTURE PANEL
# ----------------------------------------------------------
with view_tab:
    # RESTORED SEARCH / SELECTION MATRIX TO PREVENT EMPTY TAB BLANKOUT
    selected_ticker = st.selectbox("SELECT TERMINAL SEARCH ASSET PROBE TARGET", options=universe["symbol"].tolist(), index=0)
    full_ticker = f"{selected_ticker}.NS"
    
    with st.spinner("Decoding asset telemetry lines..."):
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
                
                # Top Row Financial Accounts Position Matrix
                n1, n2, n3, n4 = st.columns(4)
                with n1:
                    st.markdown(f'<div class="glass-card"><p class="glass-label">[ Total Cash Pool ]</p><div class="glass-value" style="color:#ddeeff;">₹{allocated_capital:,.2f}</div></div>', unsafe_allow_html=True)
                with n2:
                    st.markdown(f'<div class="glass-card"><p class="glass-label">[ Stock Invested ]</p><div class="glass-value" style="color:#00e87a;">₹0.00</div></div>', unsafe_allow_html=True)
                with n3:
                    st.markdown(f'<div class="glass-card"><p class="glass-label">[ Unallocated Cash ]</p><div class="glass-value" style="color:#ffcc00;">₹{allocated_capital:,.2f}</div></div>', unsafe_allow_html=True)
                with n4:
                    st.markdown(f'<div class="glass-card"><p class="glass-label">[ Net Total Wealth ]</p><div class="glass-value" style="color:#00c8ff;">₹{allocated_capital:,.2f}</div></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                
                # Split Dashboard Framework Core Layout
                left_panel, right_panel = st.columns([2.2, 1])
                
                with left_panel:
                    st.markdown(f'<p class="section-header">[ 📊 ACTIVE PLOT INTERFACE FOR {selected_ticker} ]</p>', unsafe_allow_html=True)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Close Value", line=dict(color="#00c8ff", width=2)))
                    if "SMA_20" in df.columns:
                        fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA_20"], name="SMA 20 Core", line=dict(color="#00e87a", width=1.5, dash="dash")))
                    fig.update_layout(
                        margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#ddeeff", family="Space Mono"), height=380,
                        xaxis=dict(gridcolor="rgba(0,200,255,0.04)"), yaxis=dict(gridcolor="rgba(0,200,255,0.04)")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                with right_panel:
                    st.markdown('<p class="section-header">[ ⚡ ASSET ENGINE PROFILE ]</p>', unsafe_allow_html=True)
                    
                    st.markdown(f'<div class="glass-card"><p class="glass-label">[ Last Close Price ]</p><div class="glass-value" style="color:#ddeeff;">₹{last_close:,.2f}</div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="glass-card"><p class="glass-label">[ RSI Momentum Index ]</p><div class="glass-value" style="color:#00c8ff;">{last_row["RSI_14"]:.1f}</div></div>', unsafe_allow_html=True)
                    
                    color_map = {"BUY": "#00e87a", "SELL": "#ff3355", "HOLD": "#ffcc00"}
                    st.markdown(f'<div class="glass-card"><p class="glass-label">[ Structural Signal Bias ]</p><div class="glass-value" style="color:{color_map.get(signal)};">{signal}</div></div>', unsafe_allow_html=True)
                    
                    vol = last_row["Volatility_20"] if pd.notna(last_row["Volatility_20"]) else 0.0
                    st.markdown(f'<div class="glass-card"><p class="glass-label">[ Annualized Sigma Volatility ]</p><div class="glass-value" style="color:#7c4dff;">{vol:.1%}</div></div>', unsafe_allow_html=True)
                    
        except Exception as e:
            st.error(f"Error drawing telemetry layout matrix: {e}")

    # Bottom Multi-Stock Background Scanner Output Section
    if st.session_state.last_scan_data is not None:
        st.markdown("---")
        st.markdown('<p class="section-header">[ 📡 MULTI-STOCK SCANNED MARKET MATRIX ]</p>', unsafe_allow_html=True)
        
        df_final = pd.DataFrame(st.session_state.last_scan_data)
        grid_filter = st.radio("FILTER RADAR VIEW TARGETS", ["🟢 ACTIVE BUYS", "🔴 RISK EXITS", "🌐 COMPLETE ANALYSIS MATRIX", "📊 HEATMAP GRID"], horizontal=True)
        
        if grid_filter == "🟢 ACTIVE BUYS":
            buys = df_final[df_final["raw_signal"] == "BUY"].drop(columns=["raw_signal", "pct_change", "above_trend"])
            if not buys.empty: st.dataframe(buys, use_container_width=True, hide_index=True)
            else: st.info("No tickers match active structural trend buy filters.")
        elif grid_filter == "🔴 RISK EXITS":
            sells = df_final[df_final["raw_signal"] == "SELL"].drop(columns=["raw_signal", "pct_change", "above_trend"])
            if not sells.empty: st.dataframe(sells, use_container_width=True, hide_index=True)
            else: st.info("No tracking assets currently flag structural exit targets.")
        elif grid_filter == "🌐 COMPLETE ANALYSIS MATRIX":
            st.dataframe(df_final.drop(columns=["raw_signal", "pct_change", "above_trend"]), use_container_width=True, hide_index=True)
        elif grid_filter == "📊 HEATMAP GRID":
            c_left, c_right = st.columns([2, 1])
            cached_list = st.session_state.last_scan_data
            with c_
