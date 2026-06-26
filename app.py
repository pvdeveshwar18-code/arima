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
            "company": ["Reliance Industries Ltd", "Tata Consultancy Services", "HDFC Bank Ltd", "Infosys Ltd", "State Bank of India", "ICICI Bank Ltd", "ITC Ltd", "Larsen & Toubro Ltd", "Bharti Airtel Ltd", "Hindustan Unilever Ltd", "Tata Motors Ltd", "Zomato Ltd", "Swiggy Ltd"],
            "symbol": ["RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN", "ICICIBANK", "ITC", "LT", "BHARTIARTL", "HINDUNILVR", "TATAMOTORS", "ZOMATO", "SWIGGY"],
            "ticker": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "SBIN.NS", "ICICIBANK.NS", "ITC.NS", "LT.NS", "BHARTIARTL.NS", "HINDUNILVR.NS", "TATAMOTORS.NS", "ZOMATO.NS", "SWIGGY.NS"],
            "exchange": ["NSE"] * 13
        }
        frames.append(pd.DataFrame(fallback_data))

    uni = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["ticker"])
    uni["display"] = uni["company"].fillna(uni["symbol"]).astype(str) + " | " + uni["exchange"].astype(str) + " | " + uni["ticker"].astype(str)
    return uni.sort_values(["company", "exchange"]).reset_index(drop=True)

universe = load_stock_universe()

# --- INITIALIZE APP STATES ---
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

# Helper functions for processing metrics
def add_indicators(df):
    out = df.copy()
    if len(out) < 2:
        return out
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
    
    m = out["Close"].rolling(20).mean()
    s = out["Close"].rolling(20).std()
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
    except:
        pass
    return pd.DataFrame()

# --- SIDEBAR INTERFACE & NAVIGATION MENU ---
with st.sidebar:
    st.header("📌 Navigation")
    # This acts as the tab system inside the sidebar
    app_mode = st.radio("Go to view:", ["🔍 Asset Deep-Dive", "🎯 Buy Recommendations Scanner"])
    
    st.markdown("---")
    st.header("Parameters")
    period = st.selectbox("History", ["5y", "3y", "2y", "1y"], index=0)
    interval = st.selectbox("Interval", ["1d", "1wk"], index=0)
    
    if app_mode == "🔍 Asset Deep-Dive":
        forecast_days = st.slider("Forecast horizon (trading days)", 5, 252, 60)
    
    st.markdown("---")
    st.markdown("⚙️ **Advanced Strategic Parameters**")
    allocated_capital = st.number_input("Total Trade Capital (₹)", min_value=1000, value=100000, step=5000)
    risk_per_trade = st.slider("Max Capital Risk Per Trade (%)", 0.5, 5.0, 1.5, step=0.1)
    risk_reward_ratio = st.slider("Target Risk-to-Reward Ratio (1:X)", 1.5, 4.0, 2.0, step=0.5)
    
    if app_mode == "🔍 Asset Deep-Dive":
        backtest_split = st.slider("Backtest split (%)", 60, 90, 80)
        show_raw = st.checkbox("Show raw data", value=False)


# ==========================================================
# VIEW 1: INDIVIDUAL ASSET DEEP DIVE
# ==========================================================
if app_mode == "🔍 Asset Deep-Dive":
    # Top Search Bar
    st.markdown("### 🔍 Search Symbol")
    search_col1, search_col2 = st.columns([0.8, 0.2])

    with search_col1:
        search_text = st.text_input("Type company name or exchange symbol", value="", placeholder="🔍 Symbol, company... (e.g. TCS, RELIANCE, SWIGGY)", label_visibility="collapsed")
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

    cleaned_input = search_text.strip().upper()
    if cleaned_input.endswith(".NS") or cleaned_input.endswith(".BO"):
        st.session_state.main_ticker = cleaned_input
        st.session_state.selected_company = cleaned_input.split(".")[0]
        st.session_state.selected_exchange = cleaned_input.split(".")[1]

    if run_pressed:
        raw_text = search_text.strip().upper()
        if raw_text and not (raw_text.endswith(".NS") or raw_text.endswith(".BO")):
            st.session_state.main_ticker = f"{raw_text}.NS"
            st.session_state.selected_company = raw_text
            st.session_state.selected_exchange = "NSE"
        st.session_state.trigger_analysis = True
        st.rerun()

    st.markdown(
        f"<div style='margin-bottom: 1.5rem;'>Active Asset Focus: <strong>{st.session_state.selected_company}</strong> "
        f"<span class='badge'>{st.session_state.selected_exchange}</span> "
        f"<span class='badge'>{st.session_state.main_ticker}</span></div>",
        unsafe_allow_html=True,
    )

    if st.session_state.trigger_analysis:
        main_ticker = st.session_state.main_ticker
        base = download_stock(main_ticker, period, interval)
        
        @st.cache_data(ttl=86400)
        def fetch_fundamentals(ticker):
            try:
                t = yf.Ticker(ticker)
                inf = t.info
                return {
                    "pe": inf.get("trailingPE", np.nan),
                    "pb": inf.get("priceToBook", np.nan),
                    "beta": inf.get("beta", np.nan),
                    "summary": inf.get("longBusinessSummary", "No summary indexed available.")
                }
            except:
                return {"pe": np.nan, "pb": np.nan, "beta": np.nan, "summary": "No metrics available."}
        
        f_metrics = fetch_fundamentals(main_ticker)
        
        if base.empty:
            st.error(f"No valid price history fetched for {main_ticker}.")
        else:
            base = add_indicators(base)
            last_close = float(base["Close"].iloc[-1])
            ytd_return = float((base["Close"].iloc[-1] / base["Close"].iloc[0] - 1) * 100)
            annual_vol = float(base["Volatility_20"].iloc[-1]) if pd.notna(base["Volatility_20"].iloc[-1]) else 0.0
            signal = signal_label(base)
            
            # Crossover logic metrics
            def backtest_crossover(df):
                d = df.dropna(subset=["SMA_20", "SMA_50"]).copy()
                if d.empty: return df.copy(), 0, 0, 0, 0
                d["Signal"] = 0
                d.loc[d["SMA_20"] > d["SMA_50"], "Signal"] = 1
                d["Position"] = d["Signal"].diff().fillna(0)
                d["Strategy_Return"] = d["Return"] * d["Signal"].shift(1).fillna(0)
                d["Equity"] = (1 + d["Strategy_Return"].fillna(0)).cumprod()
                d["BuyHold"] = (1 + d["Return"].fillna(0)).cumprod()
                max_dd = float(((d["Equity"] - d["Equity"].cummax()) / d["Equity"].cummax()).min())
                return d, d["Equity"].iloc[-1]-1, d["BuyHold"].iloc[-1]-1, int((d["Position"] == 1).sum()), max_dd

            backtested, strat_ret, bh_ret, trades, max_dd = backtest_crossover(base)
            steps = forecast_days if interval == "1d" else max(4, forecast_days // 5)
            
            def forecast_arima(series, steps):
                clean = series.dropna()
                if len(clean) < 30: return None
                try: return ARIMA(clean, order=(1,1,1)).fit().get_forecast(steps=steps).predicted_mean
                except: return None
            
            def forecast_ets(series, steps):
                clean = series.dropna()
                if len(clean) < 30: return None
                try: return ExponentialSmoothing(clean, trend="add").fit(optimized=True).forecast(steps)
                except: return None

            arima_pred = forecast_arima(base["Close"], steps)
            ets_pred = forecast_ets(base["Close"], steps)

            # Core KPIs
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Last Close", f"₹{last_close:,.2f}", "Live Engine")
            c2.metric("Period Return", f"{ytd_return:+.2f}%", "Historical Baseline")
            c3.metric("Annual Volatility", f"{annual_vol:.2%}", "Risk Standard", delta_color="inverse")
            c4.metric("Tactical Bias", signal, "Quant Rules")

            t1, t2, t3, t4 = st.tabs(["📊 Advanced Analytics", "🤖 Predictive Intelligence", "🧪 Strategy & Risk Sizing", "🧬 Fundamental Profile"])
            
            with t1:
                st.markdown("<h4 style='color:#38bdf8;'>Price Action Overlays</h4>", unsafe_allow_html=True)
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.7, 0.3])
                fig.add_trace(go.Scatter(x=base["Date"], y=base["Close"], name="Close Price", line=dict(color="#00d4aa")), row=1, col=1)
                fig.add_trace(go.Scatter(x=base["Date"], y=base["SMA_20"], name="SMA 20", line=dict(color="#38bdf8", dash="dash")), row=1, col=1)
                fig.add_trace(go.Scatter(x=base["Date"], y=base["SMA_50"], name="SMA 50", line=dict(color="#a78bfa")), row=1, col=1)
                fig.add_trace(go.Scatter(x=base["Date"], y=base["RSI_14"], name="RSI", line=dict(color="#fbbf24")), row=2, col=1)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#e5e7eb"), height=500, margin=dict(l=10,r=10,t=10,b=10))
                st.plotly_chart(fig, use_container_width=True)

            with t2:
                st.markdown("<h4 style='color:#38bdf8;'>Statistical Projections Spectrum</h4>", unsafe_allow_html=True)
                fc_idx = pd.bdate_range(base["Date"].iloc[-1] + pd.Timedelta(days=1), periods=steps)
                fig_fc = go.Figure()
                fig_fc.add_trace(go.Scatter(x=base["Date"].tail(90), y=base["Close"].tail(90), name="Historical Anchor", line=dict(color="#64748b")))
                if arima_pred is not None: fig_fc.add_trace(go.Scatter(x=fc_idx, y=arima_pred.values, name="ARIMA Regression", line=dict(color="#ef4444")))
                if ets_pred is not None: fig_fc.add_trace(go.Scatter(x=fc_idx, y=ets_pred.values, name="ETS Smoothing", line=dict(color="#00d4aa", dash="dot")))
                fig_fc.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#e5e7eb"), margin=dict(l=10,r=10,t=10,b=10))
                st.plotly_chart(fig_fc, use_container_width=True)

            with t3:
                st.markdown("<h4 style='color:#38bdf8;'>Strategy Execution Targets</h4>", unsafe_allow_html=True)
                current_atr = base["ATR_14"].iloc[-1] if pd.notna(base["ATR_14"].iloc[-1]) else (last_close * 0.02)
                allowed_rupees_at_risk = allocated_capital * (risk_per_trade / 100.0)
                stop_loss_distance = current_atr * 1.5
                recommended_shares = int(allowed_rupees_at_risk // stop_loss_distance) if stop_loss_distance > 0 else 0
                
                stop_loss_price = last_close - stop_loss_distance
                target_profit_price = last_close + (stop_loss_distance * risk_reward_ratio)
                
                rc1, rc2, rc3 = st.columns(3)
                rc1.metric("Strategy Return", f"{strat_ret:.2%}", f"vs Bench {bh_ret:.2%}")
                rc2.metric("Max Drawdown", f"{max_dd:.2%}")
                rc3.metric("Position Allocation", f"{recommended_shares} Units", f"Risk Budget: ₹{allowed_rupees_at_risk:,.2f}")
                
                st.markdown("🎯 **Active Execution Directives**")
                tc1, tc2, tc3 = st.columns(3)
                tc1.metric("🧱 Entry Threshold anchor", f"₹{last_close:,.2f}")
                tc2.metric("🛑 Technical Stop-Loss", f"₹{stop_loss_price:,.2f}")
                tc3.metric("🎁 Take-Profit Target", f"₹{target_profit_price:,.2f}")

            with t4:
                st.markdown("<h4 style='color:#38bdf8;'>Corporate Fundamental Snapshot</h4>", unsafe_allow_html=True)
                st.write(f"**Company Profile:** {f_metrics['summary']}")


# ==========================================================
# VIEW 2: AUTOMATED BUY RECOMMENDATIONS SCANNER
# ==========================================================
elif app_mode == "🎯 Buy Recommendations Scanner":
    st.markdown("### ⚡ Algorithmic Market Scanner Engine")
    st.caption("Scanning core Indian structural listings against fast-momentum technical rules...")
    
    # Standard batch selection to track signals quickly
    scan_universe = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "SBIN.NS", "ICICIBANK.NS", "ITC.NS", "LT.NS", "BHARTIARTL.NS", "TATAMOTORS.NS", "ZOMATO.NS", "SWIGGY.NS"]
    
    if st.button("🚀 Execute Full Market Scan", use_container_width=True):
        results = []
        progress_bar = st.progress(0)
        
        for idx, ticker in enumerate(scan_universe):
            df_raw = download_stock(ticker, period, interval)
            if not df_raw.empty and len(df_raw) > 50:
                df_calc = add_indicators(df_raw)
                last_row = df_calc.iloc[-1]
                bias = signal_label(df_calc)
                
                # Math calculations for bracket rules
                current_price = last_row["Close"]
                atr = last_row["ATR_14"] if pd.notna(last_row["ATR_14"]) else (current_price * 0.02)
                sl_dist = atr * 1.5
                sl_price = current_price - sl_dist
                tp_price = current_price + (sl_dist * risk_reward_ratio)
                
                # Allocation units calculation mapping
                rupees_at_risk = allocated_capital * (risk_per_trade / 100.0)
                shares_to_buy = int(rupees_at_risk // sl_dist) if sl_dist > 0 else 0
                
                results.append({
                    "Ticker Symbol": ticker.replace(".NS", ""),
                    "Current Price": f"₹{current_price:,.2f}",
                    "RSI (14)": f"{last_row['RSI_14']:.1f}",
                    "Technical Recommendation": bias,
                    "Suggested Capital Sizing": f"{shares_to_buy} Units",
                    "Calculated Stop-Loss": f"₹{sl_price:,.2f}",
                    "Profit Target Price": f"₹{tp_price:,.2f}"
                })
            progress_bar.progress((idx + 1) / len(scan_universe))
            
        df_scan = pd.DataFrame(results)
        
        # Color Highlighter Rules based on signal category
        def highlight_signals(row):
            colors = []
            for val in row:
                if val == "Buy":
                    colors.append("background-color: rgba(34, 197, 94, 0.25); color: #22c55e; font-weight: bold;")
                elif val == "Exit":
                    colors.append("background-color: rgba(239, 68, 68, 0.25); color: #ef4444; font-weight: bold;")
                else:
                    colors.append("")
            return colors

        st.markdown("---")
        st.markdown("### 📋 Filtered Operational Recommendation List Matrix")
        
        # Display sorted buys immediately
        buys_only = df_scan[df_scan["Technical Recommendation"] == "Buy"]
        exits_only = df_scan[df_scan["Technical Recommendation"] == "Exit"]
        holds_only = df_scan[df_scan["Technical Recommendation"] == "Hold"]
        
        tab_buy, tab_exit, tab_all = st.tabs([f"🟢 Active Buys ({len(buys_only)})", f"🔴 Active Exits ({len(exits_only)})", "🌐 Entire Market Tracker Grid"])
        
        with tab_buy:
            if not buys_only.empty:
                st.dataframe(buys_only, use_container_width=True, hide_index=True)
            else:
                st.info("No active crossover buy signals discovered within this timeframe constraint asset list.")
                
        with tab_exit:
            if not exits_only.empty:
                st.dataframe(exits_only, use_container_width=True, hide_index=True)
            else:
                st.info("No explicit structural breakout exits found.")
                
        with tab_all:
            st.dataframe(df_scan.style.apply(highlight_signals, axis=1), use_container_width=True, hide_index=True)
    else:
        st.info("💡 Click the button above to execute a real-time automated sweep of the asset matrix list.")
