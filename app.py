import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

st.markdown(
    """
<div style="margin-bottom: 1.5rem;">
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
    search_text = st.text_input("Type company name or symbol", value="", placeholder="e.g. Swiggy, Reliance, TCS")

    matches = suggestion_matches(search_text)
    if search_text.strip() != "" and not matches.empty:
        st.markdown('<div class="suggestion-box">', unsafe_allow_html=True)
        for _, row in matches.iterrows():
            if st.button(row["display"], key=f"sel_{row['ticker']}", use_container_width=True):
                set_selected(row["display"])
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    elif search_text.strip() != "":
        st.caption("✨ Custom Ticker detected. Press 'Run Analysis' to process across Indian markets.")

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
    
    st.markdown("---")
    st.markdown("⚙️ **Advanced Strategic Parameters**")
    allocated_capital = st.number_input("Total Trade Capital (₹)", min_value=1000, value=100000, step=5000)
    risk_per_trade = st.slider("Max Capital Risk Per Trade (%)", 0.5, 5.0, 1.5, step=0.1)
    
    backtest_split = st.slider("Backtest split (%)", 60, 90, 80)
    show_raw = st.checkbox("Show raw data", value=False)
    
    if st.button("Run Analysis", use_container_width=True):
        raw_text = search_text.strip().upper()
        if raw_text and not (raw_text.endswith(".NS") or raw_text.endswith(".BO")):
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
    except Exception:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=86400)
def fetch_fundamentals(ticker):
    try:
        t = yf.Ticker(ticker)
        inf = t.info
        return {
            "pe": inf.get("trailingPE", np.nan),
            "pb": inf.get("priceToBook", np.nan),
            "beta": inf.get("beta", np.nan),
            "cap": inf.get("marketCap", np.nan),
            "summary": inf.get("longBusinessSummary", "No corporate profile summary indexed summary available.")
        }
    except:
        return {"pe": np.nan, "pb": np.nan, "beta": np.nan, "cap": np.nan, "summary": "No fundamental metrics resolved."}

def add_indicators(df):
    out = df.copy()
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

def backtest_crossover(df):
    d = df.dropna(subset=["SMA_20", "SMA_50"]).copy()
    if d.empty:
        return df.copy(), 0, 0, 0, 0
    d["Signal"] = 0
    d.loc[d["SMA_20"] > d["SMA_50"], "Signal"] = 1
    d["Position"] = d["Signal"].diff().fillna(0)
    d["Strategy_Return"] = d["Return"] * d["Signal"].shift(1).fillna(0)
    d["Equity"] = (1 + d["Strategy_Return"].fillna(0)).cumprod()
    d["BuyHold"] = (1 + d["Return"].fillna(0)).cumprod()
    
    # Calculate Max Drawdown
    cum_max = d["Equity"].cummax()
    d["Drawdown"] = (d["Equity"] - cum_max) / cum_max
    max_dd = float(d["Drawdown"].min())
    
    total_return = d["Equity"].iloc[-1] - 1 if len(d) > 0 else 0
    bh_return = d["BuyHold"].iloc[-1] - 1 if len(d) > 0 else 0
    trades = int((d["Position"] == 1).sum())
    return d, total_return, bh_return, trades, max_dd

def forecast_arima(series, steps):
    clean = series.dropna()
    if len(clean) < 30: return None
    for order in [(1, 1, 1), (2, 1, 0)]:
        try:
            model = ARIMA(clean, order=order).fit()
            return model.get_forecast(steps=steps).predicted_mean
        except: continue
    return None

def forecast_ets(series, steps):
    clean = series.dropna()
    if len(clean) < 30: return None
    try:
        model = ExponentialSmoothing(clean, trend="add", seasonal=None).fit(optimized=True)
        return model.forecast(steps)
    except: return None

if st.session_state.trigger_analysis:
    main_ticker = st.session_state.main_ticker
    base = download_stock(main_ticker, period, interval)
    f_metrics = fetch_fundamentals(main_ticker)
    
    if base.empty:
        st.error(f"No valid price history fetched for {main_ticker}. Verify symbol parameter accuracy.")
    else:
        base = add_indicators(base)
        last_close = float(base["Close"].iloc[-1])
        ytd_return = float((base["Close"].iloc[-1] / base["Close"].iloc[0] - 1) * 100)
        annual_vol = float(base["Volatility_20"].iloc[-1]) if pd.notna(base["Volatility_20"].iloc[-1]) else 0.0
        
        signal = signal_label(base)
        backtested, strat_ret, bh_ret, trades, max_dd = backtest_crossover(base)
        
        steps = forecast_days if interval == "1d" else max(4, forecast_days // 5)
        arima_pred = forecast_arima(base["Close"], steps)
        ets_pred = forecast_ets(base["Close"], steps)

        # Primary Core Metric Dashboard Rows
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            with st.container(border=True):
                st.metric(label="Last Close", value=f"₹{last_close:,.2f}", delta="Live Feed Engine")
        with c2:
            with st.container(border=True):
                st.metric(label="Period Return", value=f"{ytd_return:+.2f}%", delta="Historical Baseline")
        with c3:
            with st.container(border=True):
                st.metric(label="Annual Volatility", value=f"{annual_vol:.2%}", delta="Risk Standard", delta_color="inverse")
        with c4:
            with st.container(border=True):
                st.metric(label="Tactical Bias", value=signal, delta="Quant Crossover Rules")

        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

        # Navigation Pipeline Tabs
        t1, t2, t3, t4 = st.tabs([
            "📊 Advanced Analytics", 
            "🤖 Predictive Intelligence", 
            "🧪 Strategy & Risk Sizing", 
            "🧬 Fundamental Profile"
        ])

        with t1:
            st.markdown("<h4 style='color:#38bdf8; font-weight:700;'>Price Action & Momentum Overlays</h4>", unsafe_allow_html=True)
            show_bb = st.checkbox("Overlay Bollinger Volatility Bands (20, 2)", value=True)
            
            # Subplot Configuration: Panel 1 = Price/MA, Panel 2 = RSI Matrix
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.7, 0.3])
            
            fig.add_trace(go.Scatter(x=base["Date"], y=base["Close"], name="Close Price", line=dict(color="#00d4aa", width=2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=base["Date"], y=base["SMA_20"], name="Fast (SMA 20)", line=dict(color="#38bdf8", width=1.5, dash="dash")), row=1, col=1)
            fig.add_trace(go.Scatter(x=base["Date"], y=base["SMA_50"], name="Slow (SMA 50)", line=dict(color="#a78bfa", width=1.5)), row=1, col=1)
            
            if show_bb and "BB_Upper" in base.columns:
                fig.add_trace(go.Scatter(x=base["Date"], y=base["BB_Upper"], name="BB Upper Band", line=dict(color="rgba(239,68,68,0.35)", width=1)), row=1, col=1)
                fig.add_trace(go.Scatter(x=base["Date"], y=base["BB_Lower"], name="BB Lower Band", line=dict(color="rgba(239,68,68,0.35)", width=1), fill='tonexty'), row=1, col=1)

            # RSI Lower Subplot
            fig.add_trace(go.Scatter(x=base["Date"], y=base["RSI_14"], name="RSI (14)", line=dict(color="#fbbf24", width=1.5)), row=2, col=1)
            fig.add_shape(type="line", x0=base["Date"].iloc[0], x1=base["Date"].iloc[-1], y0=70, y1=70, line=dict(color="rgba(239,68,68,0.5)", dash="dot"), row=2, col=1)
            fig.add_shape(type="line", x0=base["Date"].iloc[0], x1=base["Date"].iloc[-1], y0=30, y1=30, line=dict(color="rgba(34,197,94,0.5)", dash="dot"), row=2, col=1)
            
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e5e7eb", family="Inter"), hovermode="x unified",
                margin=dict(l=10, r=10, t=10, b=10), height=550,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", side="right", row=1, col=1)
            fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", side="right", range=[10, 90], row=2, col=1)
            fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        with t2:
            st.markdown("<h4 style='color:#38bdf8; font-weight:700;'>Statistical Projections Spectrum</h4>", unsafe_allow_html=True)
            fc_idx = pd.bdate_range(base["Date"].iloc[-1] + pd.Timedelta(days=1), periods=steps)
            
            fig_fc = go.Figure()
            fig_fc.add_trace(go.Scatter(x=base["Date"].tail(90), y=base["Close"].tail(90), name="Historical Anchor", line=dict(color="#64748b", width=2)))
            
            if arima_pred is not None:
                fig_fc.add_trace(go.Scatter(x=fc_idx, y=arima_pred.values, name="ARIMA Regression ML", line=dict(color="#ef4444", width=2.5)))
            if ets_pred is not None:
                fig_fc.add_trace(go.Scatter(x=fc_idx, y=ets_pred.values, name="ETS Exponential Smooth Matrix", line=dict(color="#00d4aa", width=2.5, dash="dot")))
                
            fig_fc.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e5e7eb", family="Inter"), hovermode="x unified",
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig_fc.update_yaxes(gridcolor="rgba(255,255,255,0.05)", side="right")
            fig_fc.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
            st.plotly_chart(fig_fc, use_container_width=True, config={'displayModeBar': False})

        with t3:
            st.markdown("<h4 style='color:#38bdf8; font-weight:700;'>Strategy Optimization & Position Risk Sizer</h4>", unsafe_allow_html=True)
            
            # Position Sizing Logic Calculations
            current_atr = base["ATR_14"].iloc[-1] if pd.notna(base["ATR_14"].iloc[-1]) else (last_close * 0.02)
            allowed_rupees_at_risk = allocated_capital * (risk_per_trade / 100.0)
            stop_loss_distance = current_atr * 1.5
            
            if stop_loss_distance > 0:
                recommended_shares = int(allowed_rupees_at_risk // stop_loss_distance)
            else:
                recommended_shares = 0
                
            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                st.metric("Strategy Historical Return", f"{strat_ret:.2%}", delta=f"vs Bench {bh_ret:.2%}")
            with rc2:
                st.metric("Maximum Backtest Drawdown", f"{max_dd:.2%}", delta="Peak-to-Trough Pain Factor", delta_color="inverse")
            with rc3:
                st.metric("Recommended Share Execution Size", f"{recommended_shares} Units", f"Risk Target: ₹{allowed_rupees_at_risk:,.2f}")
                
            st.caption(f"ℹ️ **Position Sizing Engine Logic:** Risking {risk_per_trade}% of total capital with a technical Stop-Loss placed 1.5x ATR below your execution point.")
            
            fig_bt = go.Figure()
            fig_bt.add_trace(go.Scatter(x=backtested["Date"], y=backtested["Equity"], name="Strategy Momentum Equity Curve", line=dict(color="#00d4aa", width=2)))
            fig_bt.add_trace(go.Scatter(x=backtested["Date"], y=backtested["BuyHold"], name="Benchmark Buy & Hold Track", line=dict(color="#38bdf8", dash="dash")))
            fig_bt.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e5e7eb", family="Inter"), margin=dict(l=10, r=10, t=10, b=10)
            )
            fig_bt.update_yaxes(gridcolor="rgba(255,255,255,0.05)", side="right")
            st.plotly_chart(fig_bt, use_container_width=True, config={'displayModeBar': False})

        with t4:
            st.markdown("<h4 style='color:#38bdf8; font-weight:700;'>Corporate Fundamental Snapshot</h4>", unsafe_allow_html=True)
            
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                st.metric("Trailing P/E Ratio", f"{f_metrics['pe']:.2f}" if pd.notna(f_metrics['pe']) else "N/A")
            with fc2:
                st.metric("Price-to-Book (P/B)", f"{f_metrics['pb']:.2f}" if pd.notna(f_metrics['pb']) else "N/A")
            with fc3:
                st.metric("Historical Asset Beta", f"{f_metrics['beta']:.2f}" if pd.notna(f_metrics['beta']) else "N/A")
                
            st.markdown(f"**Corporate Background Summary Profile:**\n\n>{f_metrics['summary']}")
            
            if show_raw:
                st.markdown("---")
                st.dataframe(base.tail(30), use_container_width=True)
else:
    st.info("👈 Set system variables inside the panel matrix settings on the left sidebar and select 'Run Analysis'.")
