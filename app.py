import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go

# Keeping your original professional app title
st.set_page_config(page_title="Indian Stocks Forecast Pro", page_icon="📈", layout="wide")

# ==========================================================
# TAILORED DESIGN SYSTEM: PREMIUM ACCENTS ONLY
# ==========================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Space+Mono&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Elegant Custom Cyber-Dark Canvas background */
.stApp {
    background: linear-gradient(180deg, #030914 0%, #0a1124 100%) !important;
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] {
    background: rgba(6, 11, 26, 0.85) !important;
    border-right: 1px solid rgba(0, 212, 170, 0.1) !important;
}

/* Premium custom card layouts to replace stock text components */
.accent-card {
    background: #0d162d;
    border: 1px solid rgba(0, 212, 170, 0.15);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

/* Tab Bar Adjustments */
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

# ==========================================================
# APP APPLICATION MAIN HEADER
# ==========================================================
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
# PERSISTENT STORAGE LAYER & DATA UTILITIES
# ==========================================================
if "cached_batch_data" not in st.session_state:
    st.session_state.cached_batch_data = None
if "cached_timestamp" not in st.session_state:
    st.session_state.cached_timestamp = None

@st.cache_data(ttl=86400)
def load_stock_universe():
    nse_symbols = [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN", "ICICIBANK", "BHARTIARTL", "LTIM", "ITC", "LT",
        "HINDUNILVR", "BAJFINANCE", "TATAMOTORS", "AXISBANK", "WIPRO", "HCLTECH", "SUNPHARMA", "NTPC"
    ]
    data = {
        "company": [f"{sym} Listing" for sym in nse_symbols],
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
# SIDEBAR CONTROL PANEL
# ==========================================================
with st.sidebar:
    st.markdown("<h3 style='color: #00d4aa; font-size: 14px; margin-top:0;'>🛡️ RISK PARAMETERS</h3>", unsafe_allow_html=True)
    allocated_capital = st.number_input("Capital Pool (₹)", min_value=1000, value=100000, step=5000)
    risk_per_trade = st.slider("Max Sizing Risk (%)", 0.5, 5.0, 1.5, step=0.1)
    risk_reward_ratio = st.slider("Risk-Reward Ratio (1:X)", 1.5, 4.0, 2.0, step=0.5)
    
    st.markdown("---")
    period = st.selectbox("Historical Window", ["3y", "1y"], index=1)
    interval = st.selectbox("Interval", ["1d", "1wk"], index=0)

# --- BACKGROUND DATA SYNC (FIXED: replaced NULL with None) ---
all_tickers = universe["ticker"].tolist()
if st.session_state.cached_batch_data is None or st.sidebar.button("🔄 Sync Market Data"):
    with st.spinner("Downloading updated asset feeds..."):
        try:
            st.session_state.cached_batch_data = yf.download(all_tickers, period="1y", interval="1d", group_by='ticker', auto_adjust=False, progress=False)
            st.session_state.cached_timestamp = time.strftime("%H:%M:%S")
        except Exception as e:
            st.error(f"Sync error: {e}")

# ==========================================================
# MAIN INTERFACE TABS
# ==========================================================
view_tab, scan_tab, summary_tab = st.tabs(["🔍 ASSET VIEW", "🎯 QUANT SCANNER", "📊 BENCHMARK METRICS"])

# TAB 1: ASSET DEEP DIVE
with view_tab:
    selected_display = st.selectbox("Select Target Security", options=universe["display"].tolist(), index=0)
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
                
                # Balanced Metric Panels with soft green accents
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
                fig.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e2e8f0"), height=380,
                    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"), yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error compiling asset chart data: {e}")

# TAB 2: PORTFOLIO QUANT SCANNER
with scan_tab:
    if st.session_state.cached_timestamp:
        st.markdown(f"<p style='font-size:11px; color:#64748b; font-family:\"Space Mono\";'>Session cache active. Last update: {st.session_state.cached_timestamp}</p>", unsafe_allow_html=True)
        
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
                    "Ticker": ticker.replace(".NS", ""),
                    "Price": f"₹{c_price:,.2f}",
                    "RSI": f"{last_s_row['RSI_14']:.1f}",
                    "Signal": sig,
                    "Target Size": f"{units} Units",
                    "Stop-Loss": f"₹{sl_val:,.2f}",
                    "Take-Profit": f"₹{tp_val:,.2f}"
                })
            except:
                continue
                
        if scan_results:
            df_final = pd.DataFrame(scan_results)
            st.dataframe(df_final, use_container_width=True, hide_index=True)

# TAB 3: DYNAMIC SECTOR METRICS (Preserving Heatmaps & Market Breadth)
with summary_tab:
    c_left, c_right = st.columns([2, 1])
    raw_batch = st.session_state.cached_batch_data
    
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
                close_today = float(df_t["Close"].iloc[-1])
                close_yesterday = float(df_t["Close"].iloc[-2])
                pct_change = ((close_today - close_yesterday) / close_yesterday) * 100
                
                sma20 = df_t["Close"].rolling(20).mean().iloc[-1]
                if close_today > sma20:
                    bullish_nodes += 1
                total_nodes += 1
                
                heatmap_data.append({
                    "symbol": ticker.replace(".NS", ""),
                    "pct": pct_change,
                    "txt": "#00d4aa" if pct_change >= 0 else "#f43f5e",
                    "bg": "rgba(0, 212, 170, 0.1)" if pct_change >= 0 else "rgba(244, 63, 94, 0.1)"
                })
            except:
                continue

    with c_left:
        st.markdown("<h3 style='font-size:15px; color:#00d4aa;'>🎨 LIQUIDITY PERFORMANCE MATRIX</h3>", unsafe_allow_html=True)
        if heatmap_data:
            h_cols = st.columns(4)
            for idx, item in enumerate(heatmap_data[:12]):
                target_col = h_cols[idx % 4]
                target_col.markdown(
                    f"""
                    <div style='background: {item["bg"]}; border: 1px solid {item["txt"]}33; padding: 12px; border-radius: 6px; text-align: center; margin-bottom: 8px;'>
                        <div style='font-weight: 700; font-size: 13px;'>{item["symbol"]}</div>
                        <div style='font-family: "Space Mono", monospace; font-size: 11px; margin-top: 2px; color: {item["txt"]};'>{item["pct"]:+.2f}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
    with c_right:
        st.markdown("<h3 style='font-size:15px; color:#00d4aa;'>📊 MARKET BREADTH INDEX</h3>", unsafe_allow_html=True)
        sentiment_score = int((bullish_nodes / total_nodes) * 100) if total_nodes > 0 else 50
        
        st.markdown(
            f"""
            <div class="accent-card" style="text-align: center;">
                <p style="font-family: 'Space Mono', monospace; font-size: 10px; color:#64748b; margin:0;">STOCKS OVER 20 SMA</p>
                <h1 style="color: #38bdf8; font-size: 42px; margin: 8px 0;">{sentiment_score}%</h1>
                <div style="width: 100%; background: rgba(255,255,255,0.05); height: 6px; border-radius: 3px; overflow:hidden;">
                    <div style="width: {sentiment_score}%; background: #00d4aa; height:100%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
