import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go

# Professional App Identity preserved
st.set_page_config(page_title="Indian Stocks Forecast Pro", page_icon="📈", layout="wide")

# ==========================================================
# TAILORED SYSTEM STYLING — VISUAL ACCENTS
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

# App Core Title Line
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
# DATA GENERATION UNIVERSE & CALCULATIONS (YOUR ORIGINAL LOGIC)
# ==========================================================
@st.cache_data(ttl=86400)
def load_stock_universe():
    # The absolute top high-liquidity stock engines of the Indian indices
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
# SIDEBAR CONTROLS
# ==========================================================
with st.sidebar:
    st.markdown("<h3 style='color: #00d4aa; font-size: 14px; margin-top:0;'>🛡️ RISK PARAMETERS</h3>", unsafe_allow_html=True)
    allocated_capital = st.number_input("Capital Pool (₹)", min_value=1000, value=100000, step=5000)
    risk_per_trade = st.slider("Max Sizing Risk (%)", 0.5, 5.0, 1.5, step=0.1)
    risk_reward_ratio = st.slider("Risk-Reward Ratio (1:X)", 1.5, 4.0, 2.0, step=0.5)
    
    st.markdown("---")
    period = st.selectbox("Historical Window", ["3y", "1y"], index=1)
    interval = st.selectbox("Interval", ["1d", "1wk"], index=0)

# ==========================================================
# INTERFACE MAIN TABS
# ==========================================================
view_tab, scan_tab, summary_tab = st.tabs(["🔍 ASSET VIEW", "🎯 QUANT SCANNER", "📊 BENCHMARK METRICS"])

# TAB 1: INDIVIDUAL STOCK FOCUS CHART ENGINE
with view_tab:
    selected_display = st.selectbox("Select Target Security", options=universe["display"].tolist(), index=0)
    ticker_symbol = universe[universe["display"] == selected_display].iloc[0]["ticker"]
    
    with st.spinner(f"Pulling fresh live data for {ticker_symbol}..."):
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
                    font=dict(color="#e2e8f0"), height=380,
                    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"), yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Empty financial frame received.")
        except Exception as e:
            st.error(f"Error compiling asset chart data: {e}")

# TAB 2: PORTFOLIO RISK SCANNER ENGINE (WITH DISCOVERY SUB-TABS RESTORED)
with scan_tab:
    st.markdown("<h3 style='font-size:16px;'>🚀 WHOLE-MARKET POSITION EVALUATION MATRIX</h3>", unsafe_allow_html=True)
    
    if st.button("🚀 EXECUTE BROAD SCAN", use_container_width=True):
        all_tickers = universe["ticker"].tolist()
        scan_results = []
        
        scan_bar = st.progress(0, text="Iterating market universe arrays safely...")
        
        for idx, ticker in enumerate(all_tickers):
            try:
                # Safe individual queries protect the app against complete throttling failure blocks
                tk_df = yf.download(ticker, period="6mo", interval="1d", auto_adjust=False, progress=False)
                if tk_df is NULL or tk_df.empty: continue
                
                if isinstance(tk_df.columns, pd.MultiIndex):
                    tk_df.columns = [c[0] for c in tk_df.columns]
                tk_df = tk_df.reset_index()
                
                calc_df = add_indicators(tk_df)
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
                    "Take-Profit": f"₹{tp_val:,.2f}",
                    "raw_signal": sig
                })
            except:
                continue
            scan_bar.progress((idx + 1) / len(all_tickers), text=f"Processed asset: {ticker}")
            
        if scan_results:
            df_final = pd.DataFrame(scan_results)
            
            # Sub tabs completely restored here
            t_buy, t_sell, t_all = st.tabs(["🟢 ACTIVE BUYS", "🔴 ACTIVE EXITS", "🌐 FULL UNIVERSE FRAME"])
            with t_buy:
                buys = df_final[df_final["raw_signal"] == "BUY"].drop(columns=["raw_signal"])
                if not buys.empty: st.dataframe(buys, use_container_width=True, hide_index=True)
                else: st.info("No active structural buy triggers found in this pass.")
            with t_sell:
                sells = df_final[df_final["raw_signal"] == "SELL"].drop(columns=["raw_signal"])
                if not sells.empty: st.dataframe(sells, use_container_width=True, hide_index=True)
                else: st.info("No active short/exit flags tripped.")
            with t_all:
                st.dataframe(df_final.drop(columns=["raw_signal"]), use_container_width=True, hide_index=True)
        else:
            st.error("Data synchronization dropped. Please re-run scan cycle.")

# TAB 3: SYSTEM METRICS SUMMARY
with summary_tab:
    st.info("Run the broad scan engine inside the 'Quant Scanner' tab to automatically feed real-time breadth metrics here.")
