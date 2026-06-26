import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go

# 1. App Identity Config
st.set_page_config(page_title="Indian Stocks Forecast Pro", page_icon="📈", layout="wide")

# ==========================================================
# CUSTOM STYLING SYSTEM
# ==========================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Space+Mono&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(180deg, #030914 0%, #0a1124 100%) !important;
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] {
    background: rgba(6, 11, 26, 0.85) !important;
    border-right: 1px solid rgba(0, 212, 170, 0.1) !important;
}
.accent-card {
    background: #0d162d;
    border: 1px solid rgba(0, 212, 170, 0.15);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
div[data-baseweb="tab-list"] { gap: 8px; }
button[data-baseweb="tab"] {
    border-radius: 6px !important;
    padding: 0.5rem 1.2rem !important;
    background: #0d162d !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    border-color: #00d4aa !important;
    color: #00d4aa !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# Main Structural Title
st.markdown(
    """
<div style="margin-bottom: 1.5rem; border-bottom: 1px solid rgba(0, 212, 170, 0.15); padding-bottom: 0.75rem;">
    <h1 style="margin:0; font-size:2.2rem; font-weight:800; background: linear-gradient(90deg, #00d4aa, #38bdf8); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
        Indian Stocks Forecast Pro
    </h1>
    <p style="margin:0.2rem 0 0 0; color: #94a3b8; font-size: 0.95rem;">
        Advanced algorithmic position evaluation & whole-market risk scanning.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================================================
# ALGORITHMIC LOGIC CALCULATIONS
# ==========================================================
@st.cache_data(ttl=86400)
def load_stock_universe():
    nse_symbols = [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN", "ICICIBANK", "BHARTIARTL", "LTIM", "ITC", "LT",
        "HINDUNILVR", "BAJFINANCE", "TATAMOTORS", "AXISBANK", "WIPRO", "HCLTECH", "SUNPHARMA", "NTPC"
    ]
    data = {
        "company": [f"{sym} Traded Equity" for sym in nse_symbols],
        "symbol": nse_symbols,
        "ticker": [f"{sym}.NS" for sym in nse_symbols],
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
# INITIALIZE GLOBAL SCAN MEMORY POOL
# ==========================================================
if "last_scan_data" not in st.session_state:
    st.session_state.last_scan_data = None

# ==========================================================
# SIDEBAR SYSTEM CONTROLS & MULTI-STOCK WORKFLOWS
# ==========================================================
with st.sidebar:
    st.markdown("<h3 style='color: #00d4aa; font-size: 14px; margin-top:0;'>🛡️ RISK PARAMETERS</h3>", unsafe_allow_html=True)
    allocated_capital = st.number_input("Capital Pool (₹)", min_value=1000, value=100000, step=5000)
    risk_per_trade = st.slider("Max Sizing Risk (%)", 0.5, 5.0, 1.5, step=0.1)
    risk_reward_ratio = st.slider("Risk-Reward Ratio (1:X)", 1.5, 4.0, 2.0, step=0.5)
    
    st.markdown("---")
    period = st.selectbox("Historical Window", ["3y", "1y"], index=1)
    interval = st.selectbox("Interval Lookback Frame", ["1d", "1wk"], index=0)
    
    st.markdown("---")
    st.markdown("<h3 style='color: #00d4aa; font-size: 14px;'>📡 MULTI-STOCK SCANNER</h3>", unsafe_allow_html=True)
    
    # Quantitative calculation triggered inside the control panel
    if st.button("🚀 RUN BULK SYSTEM SCAN", use_container_width=True):
        all_tickers = universe["ticker"].tolist()
        scan_results = []
        scan_bar = st.progress(0, text="Iterating market frames...")
        
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
            scan_bar.progress((idx + 1) / len(all_tickers), text=f"Scanning: {ticker}")
            
        if scan_results:
            st.session_state.last_scan_data = scan_results
            st.sidebar.success("Scan complete!")

# ==========================================================
# RESTRUCTURED MAIN APPLICATION VIEW TABS
# ==========================================================
view_tab, backtest_tab, paper_tab = st.tabs([
    "🔍 SINGLE ASSET ANALYSIS", 
    "📈 BACKTESTING ENGINE",
    "💵 REAL-TIME PAPERTREADING"
])

# ----------------------------------------------------------
# TAB 1: INDIVIDUAL CHART TERMINAL
# ----------------------------------------------------------
with view_tab:
    selected_display = st.selectbox("Select Target Security", options=universe["display"].tolist(), index=0)
    ticker_symbol = universe[universe["display"] == selected_display].iloc[0]["ticker"]
    
    with st.spinner(f"Querying financial databases for {ticker_symbol}..."):
        try:
            df_asset = yf.download(ticker_symbol, period=period, interval=interval, auto_adjust=False, progress=False)
            if df_asset is not None and not df_asset.empty:
                if isinstance(df_asset.columns, pd.MultiIndex):
                    df_asset.columns = [c[0] for c in df_asset.columns]
                df_asset = df_asset.reset_index()
                
                df = add_indicators(df_asset)
                last_row = df.iloc[-1]
                last_close = float(last_row["Close"])
                signal = get_signal(df)
                
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.markdown(f'<div class="accent-card"><p style="color:#64748b; font-size:11px; margin:0;">LAST PRICE</p><h3 style="color:#f8fafc; margin:4px 0 0 0;">₹{last_close:,.2f}</h3></div>', unsafe_allow_html=True)
                with m2:
                    st.markdown(f'<div class="accent-card"><p style="color:#64748b; font-size:11px; margin:0;">RSI (14)</p><h3 style="color:#38bdf8; margin:4px 0 0 0;">{last_row["RSI_14"]:.1f}</h3></div>', unsafe_allow_html=True)
                with m3:
                    color_map = {"BUY": "#00d4aa", "SELL": "#f43f5e", "HOLD": "#eab308"}
                    st.markdown(f'<div class="accent-card"><p style="color:#64748b; font-size:11px; margin:0;">BIAS</p><h3 style="color:{color_map.get(signal)}; margin:4px 0 0 0;">{signal}</h3></div>', unsafe_allow_html=True)
                with m4:
                    vol = last_row["Volatility_20"] if pd.notna(last_row["Volatility_20"]) else 0.0
                    st.markdown(f'<div class="accent-card"><p style="color:#64748b; font-size:11px; margin:0;">ANNUALIZED VOLATILITY</p><h3 style="color:#a78bfa; margin:4px 0 0 0;">{vol:.1%}</h3></div>', unsafe_allow_html=True)
                    
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Close", line=dict(color="#00d4aa", width=2)))
                if "SMA_20" in df.columns:
                    fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA_20"], name="SMA 20", line=dict(color="#38bdf8", width=1.5, dash="dash")))
                fig.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e2e8f0"), height=360,
                    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"), yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error compiling asset chart data: {e}")

    # Display the results of the background multi-stock matrix underneath the main viewer if active
    if st.session_state.last_scan_data is not None:
        st.markdown("---")
        st.markdown("<h3 style='font-size:18px; color:#00d4aa;'>🎯 LIVE SCREENER RESULTS MATRIX</h3>", unsafe_allow_html=True)
        
        df_final = pd.DataFrame(st.session_state.last_scan_data)
        t_buy, t_sell, t_all, t_heatmap = st.tabs(["🟢 ACTIVE BUY SETUPS", "🔴 ACTIVE EXITS", "🌐 COMPLETE MATRIX", "📊 HEATMAP INDEX"])
        
        with t_buy:
            buys = df_final[df_final["raw_signal"] == "BUY"].drop(columns=["raw_signal", "pct_change", "above_trend"])
            if not buys.empty: st.dataframe(buys, use_container_width=True, hide_index=True)
            else: st.info("No tickers match active structural trend buy filters.")
        with t_sell:
            sells = df_final[df_final["raw_signal"] == "SELL"].drop(columns=["raw_signal", "pct_change", "above_trend"])
            if not sells.empty: st.dataframe(sells, use_container_width=True, hide_index=True)
            else: st.info("No tracking assets currently flag structural exit targets.")
        with t_all:
            st.dataframe(df_final.drop(columns=["raw_signal", "pct_change", "above_trend"]), use_container_width=True, hide_index=True)
        with t_heatmap:
            c_left, c_right = st.columns([2, 1])
            cached_list = st.session_state.last_scan_data
            bullish_nodes = sum(1 for x in cached_list if x["above_trend"])
            total_nodes = len(cached_list)
            
            with c_left:
                h_cols = st.columns(4)
                for idx, item in enumerate(cached_list[:12]):
                    target_col = h_cols[idx % 4]
                    color_hue = "#00d4aa" if item["pct_change"] >= 0 else "#f43f5e"
                    bg_hue = "rgba(0, 212, 170, 0.1)" if item["pct_change"] >= 0 else "rgba(244, 63, 94, 0.1)"
                    target_col.markdown(
                        f"<div style='background: {bg_hue}; border: 1px solid {color_hue}33; padding: 12px; border-radius: 6px; text-align: center; margin-bottom: 8px;'><div style='font-weight: 700; font-size: 13px;'>{item['Ticker']}</div><div style='font-family: \"Space Mono\", monospace; font-size: 11px; margin-top: 2px; color: {color_hue};'>{item['pct_change']:+.2f}%</div></div>",
                        unsafe_allow_html=True
                    )
            with c_right:
                sentiment_score = int((bullish_nodes / total_nodes) * 100) if total_nodes > 0 else 50
                st.markdown(
                    f'<div class="accent-card" style="text-align: center;"><p style="font-family: \'Space Mono\', monospace; font-size: 10px; color:#64748b; margin:0;">PERCENTAGE OVER 20 SMA</p><h1 style="color: #38bdf8; font-size: 42px; margin: 8px 0;">{sentiment_score}%</h1><div style="width: 100%; background: rgba(255,255,255,0.05); height: 6px; border-radius: 3px; overflow:hidden;"><div style="width: {sentiment_score}%; background: #00d4aa; height:100%;"></div></div></div>',
                    unsafe_allow_html=True
                )

# ----------------------------------------------------------
# TAB 2: BACKTESTING ENGINE
# ----------------------------------------------------------
with backtest_tab:
    st.markdown("<h3 style='font-size:16px; color:#00d4aa;'>📈 ALGORITHMIC BACKTEST ENGINE</h3>", unsafe_allow_html=True)
    st.info("Historical verification environment loaded. Ready to compile strategy performance rules against historical ticks.")

# ----------------------------------------------------------
# TAB 3: REAL-TIME PAPER TRADING
# ----------------------------------------------------------
with paper_tab:
    st.markdown("<h3 style='font-size:16px; color:#00d4aa;'>💵 VIRTUAL ACCOUNT SANDBOX EXECUTIONS</h3>", unsafe_allow_html=True)
    st.info("Simulated terminal routing configuration online. Ready to evaluate structural trade parameters in real time.")
