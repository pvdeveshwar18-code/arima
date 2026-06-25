import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_error, mean_squared_error
from math import sqrt

st.set_page_config(page_title="Indian Stocks Forecast Pro", page_icon="📈", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background:
        radial-gradient(circle at top left, rgba(0,212,170,0.10), transparent 25%),
        radial-gradient(circle at top right, rgba(56,189,248,0.10), transparent 20%),
        linear-gradient(180deg, #050816 0%, #0b1020 100%);
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1220 0%, #070b15 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
div[data-testid="stMetric"] {
    background: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 14px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.18);
}
div[data-baseweb="tab-list"] { gap: 10px; }
button[data-baseweb="tab"] {
    border-radius: 999px !important;
    padding: 0.45rem 1rem !important;
    background: rgba(15, 23, 42, 0.55) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(90deg, rgba(0,212,170,0.35), rgba(56,189,248,0.35)) !important;
    border: 1px solid rgba(0,212,170,0.40) !important;
}
.stButton > button {
    background: linear-gradient(90deg, #00d4aa, #38bdf8) !important;
    color: #03111f !important;
    border: none !important;
    border-radius: 999px !important;
    font-weight: 700 !important;
    padding: 0.6rem 1.2rem !important;
}
.stTextInput input, .stTextArea textarea, .stSelectbox div, .stMultiSelect div {
    background: rgba(15, 23, 42, 0.85) !important;
    color: #e5e7eb !important;
}
::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 999px; }
.suggestion-box {
    background: rgba(15, 23, 42, 0.92);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 0.35rem;
    margin-top: 0.35rem;
}
.suggestion-item {
    width: 100%;
    text-align: left;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(30, 41, 59, 0.7);
    color: #e5e7eb;
    padding: 0.5rem 0.75rem;
    border-radius: 10px;
    margin-bottom: 0.35rem;
    cursor: pointer;
}
.suggestion-item:hover {
    border-color: rgba(56,189,248,0.45);
    background: rgba(56,189,248,0.12);
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
<div style="margin-bottom: 1rem;">
    <h1 style="margin:0; font-size:2.3rem; font-weight:800; background: linear-gradient(90deg,#00d4aa,#38bdf8,#a78bfa); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
        Indian Stocks Forecast Pro
    </h1>
    <p style="margin:0.25rem 0 0 0; color: rgba(229,231,235,.65);">
        Forecasts, indicators, backtesting, market structure, and swing-trade context
    </p>
</div>
""",
    unsafe_allow_html=True,
)

@st.cache_data(ttl=24 * 60 * 60)
def load_stock_universe():
    frames = []

    try:
        nse = pd.read_csv("https://nsearchives.nseindia.com/content/equities/sec_list.csv")
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

    try:
        bse = pd.read_csv("https://www.bseindia.com/download/BhavCopy/eqiscrip.csv")
        bse.columns = [c.strip() for c in bse.columns]
        cols = {c.lower(): c for c in bse.columns}
        if "security code" in cols and "security name" in cols:
            tmp = pd.DataFrame()
            tmp["company"] = bse[cols["security name"]].astype(str).str.strip()
            tmp["symbol"] = bse[cols["security code"]].astype(str).str.strip()
            tmp["ticker"] = tmp["symbol"] + ".BO"
            tmp["exchange"] = "BSE"
            frames.append(tmp)
    except Exception:
        pass

    if not frames:
        return pd.DataFrame(columns=["company", "symbol", "ticker", "exchange"])

    uni = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["ticker"])
    uni = uni.sort_values(["company", "exchange"]).reset_index(drop=True)
    return uni

@st.cache_data(ttl=24 * 60 * 60)
def load_ticker_map():
    uni = load_stock_universe().copy()
    if uni.empty:
        return uni
    uni["display"] = uni["company"].fillna(uni["symbol"]).astype(str) + " | " + uni["exchange"].astype(str) + " | " + uni["ticker"].astype(str)
    return uni

universe = load_ticker_map()

if "search_text" not in st.session_state:
    st.session_state.search_text = ""
if "selected_display" not in st.session_state:
    st.session_state.selected_display = ""
if "main_ticker" not in st.session_state:
    st.session_state.main_ticker = "TCS.NS"
if "selected_company" not in st.session_state:
    st.session_state.selected_company = "TCS"
if "selected_exchange" not in st.session_state:
    st.session_state.selected_exchange = "NSE"

def set_selected(display):
    st.session_state.selected_display = display
    match = universe[universe["display"] == display].head(1)
    if not match.empty:
        st.session_state.main_ticker = match["ticker"].iloc[0]
        st.session_state.selected_company = match["company"].iloc[0]
        st.session_state.selected_exchange = match["exchange"].iloc[0]

def suggestion_matches(query):
    if universe.empty:
        return pd.DataFrame()
    q = (query or "").lower().strip()
    if not q:
        return universe.head(12)
    mask = (
        universe["company"].astype(str).str.lower().str.contains(q, na=False)
        | universe["symbol"].astype(str).str.lower().str.contains(q, na=False)
        | universe["ticker"].astype(str).str.lower().str.contains(q, na=False)
    )
    return universe.loc[mask].head(12)

with st.sidebar:
    st.header("Search stock")
    st.text_input(
        "Type company name, symbol, or ticker",
        key="search_text",
        placeholder="e.g. Reliance, TCS, 500325, INFY.NS",
        label_visibility="collapsed",
    )

    matches = suggestion_matches(st.session_state.search_text)

    if not matches.empty:
        st.markdown('<div class="suggestion-box">', unsafe_allow_html=True)
        for _, row in matches.iterrows():
            label = f"{row['company']} | {row['exchange']} | {row['ticker']}"
            if st.button(label, key=f"sel_{row['ticker']}"):
                set_selected(row["display"])
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.caption("Type to see suggestions.")

    if st.session_state.selected_display:
        st.markdown(
            f"Selected: **{st.session_state.selected_company}** <span class='badge'>{st.session_state.selected_exchange}</span> <span class='badge'>{st.session_state.main_ticker}</span>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("Selected: **TCS** <span class='badge'>NSE</span> <span class='badge'>TCS.NS</span>", unsafe_allow_html=True)

    period = st.selectbox("History", ["5y", "3y", "2y", "1y"], index=0)
    interval = st.selectbox("Interval", ["1d", "1wk"], index=0)
    forecast_days = st.slider("Forecast horizon (trading days)", 5, 252, 60)
    use_case = st.radio("Use case", ["Swing trade", "Long term"])
    backtest_split = st.slider("Backtest split (%)", 60, 90, 80)
    show_raw = st.checkbox("Show raw data", value=False)
    compare_all = st.checkbox("Compare selected tickers", value=True)
    run_btn = st.button("Run analysis")

def download_stock(ticker, period, interval):
    try:
        df = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False, threads=False)
    except Exception:
        return pd.DataFrame()
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df.reset_index()
    if "Date" not in df.columns and "Datetime" in df.columns:
        df = df.rename(columns={"Datetime": "Date"})
    if "Date" not in df.columns:
        return pd.DataFrame()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "Close" not in df.columns:
        return pd.DataFrame()
    df = df.dropna(subset=["Close"])
    return df

def add_indicators(df):
    out = df.copy()
    out["Return"] = out["Close"].pct_change()
    out["SMA_20"] = out["Close"].rolling(20).mean()
    out["SMA_50"] = out["Close"].rolling(50).mean()
    out["EMA_20"] = out["Close"].ewm(span=20, adjust=False).mean()
    out["Volatility_20"] = out["Return"].rolling(20).std() * np.sqrt(252)
    delta = out["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
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
    last = df.iloc[-1]
    if pd.isna(last["SMA_20"]) or pd.isna(last["SMA_50"]) or pd.isna(last["RSI_14"]):
        return "Hold"
    if last["SMA_20"] > last["SMA_50"] and last["RSI_14"] < 70:
        return "Buy"
    if last["SMA_20"] < last["SMA_50"] and last["RSI_14"] > 30:
        return "Exit"
    return "Hold"

def sentiment_label(df):
    last = df.iloc[-1]
    score = 0
    if pd.notna(last["SMA_20"]) and pd.notna(last["SMA_50"]) and last["SMA_20"] > last["SMA_50"]:
        score += 1
    if pd.notna(last["RSI_14"]) and last["RSI_14"] < 60:
        score += 1
    if pd.notna(last["Volatility_20"]) and last["Volatility_20"] < 0.35:
        score += 1
    if score >= 2:
        return "Positive"
    if score == 1:
        return "Neutral"
    return "Weak"

def backtest_crossover(df):
    d = df.dropna(subset=["SMA_20", "SMA_50"]).copy()
    d["Signal"] = 0
    d.loc[d["SMA_20"] > d["SMA_50"], "Signal"] = 1
    d["Position"] = d["Signal"].diff().fillna(0)
    d["Strategy_Return"] = d["Return"] * d["Signal"].shift(1).fillna(0)
    d["Equity"] = (1 + d["Strategy_Return"].fillna(0)).cumprod()
    d["BuyHold"] = (1 + d["Return"].fillna(0)).cumprod()
    total_return = d["Equity"].iloc[-1] - 1 if len(d) else np.nan
    bh_return = d["BuyHold"].iloc[-1] - 1 if len(d) else np.nan
    trades = int((d["Position"] == 1).sum())
    win_days = int((d["Strategy_Return"] > 0).sum())
    loss_days = int((d["Strategy_Return"] < 0).sum())
    return d, total_return, bh_return, trades, win_days, loss_days

def forecast_arima(series, steps):
    clean = series.dropna()
    if len(clean) < 60:
        return None, None
    for order in [(5, 1, 0), (2, 1, 2), (1, 1, 1)]:
        try:
            model = ARIMA(clean, order=order).fit()
            fc = model.get_forecast(steps=steps)
            return fc.predicted_mean, fc.conf_int()
        except Exception:
            continue
    return None, None

def forecast_ets(series, steps):
    clean = series.dropna()
    if len(clean) < 60:
        return None
    try:
        model = ExponentialSmoothing(clean, trend="add", seasonal=None, initialization_method="estimated").fit(optimized=True)
        return model.forecast(steps)
    except Exception:
        return None

def forecast_metrics(actual, pred):
    a = pd.Series(actual).dropna()
    p = pd.Series(pred).dropna()
    n = min(len(a), len(p))
    if n < 5:
        return np.nan, np.nan, np.nan
    a = a.iloc[-n:].values
    p = p.iloc[-n:].values
    mae = mean_absolute_error(a, p)
    rmse = sqrt(mean_squared_error(a, p))
    mape = np.mean(np.abs((a - p) / np.where(a == 0, np.nan, a))) * 100
    return mae, rmse, mape

def anchored_vwap(df, anchor_idx=None):
    d = df.copy()
    if anchor_idx is None:
        anchor_idx = max(0, len(d) - 60)
    d = d.iloc[anchor_idx:].copy()
    if d.empty or "Volume" not in d.columns:
        return pd.Series(dtype=float)
    typical = (d["High"] + d["Low"] + d["Close"]) / 3
    avwap = (typical * d["Volume"]).cumsum() / d["Volume"].cumsum()
    avwap.index = d["Date"].values
    return avwap

def volume_profile(df, bins=24):
    d = df.copy()
    if d.empty or "Volume" not in d.columns:
        return pd.DataFrame()
    price_min = float(d["Low"].min())
    price_max = float(d["High"].max())
    if price_max <= price_min:
        return pd.DataFrame()
    edges = np.linspace(price_min, price_max, bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2
    bucket = pd.cut(d["Close"], bins=edges, include_lowest=True, labels=False)
    vol = d.groupby(bucket)["Volume"].sum().reindex(range(bins), fill_value=0).values
    vp = pd.DataFrame({"price": centers, "volume": vol})
    if vp["volume"].sum() > 0:
        poc = vp.loc[vp["volume"].idxmax(), "price"]
        total = vp["volume"].sum()
        vp_sorted = vp.sort_values("volume", ascending=False).copy()
        vp_sorted["cum"] = vp_sorted["volume"].cumsum()
        selected = vp_sorted[vp_sorted["cum"] <= total * 0.7]
        if selected.empty:
            selected = vp_sorted.head(1)
        vah = selected["price"].max()
        val = selected["price"].min()
    else:
        poc = vah = val = np.nan
    return vp.assign(POC=poc, VAH=vah, VAL=val)

def liquidity_sweep(df, lookback=20):
    d = df.copy()
    if len(d) < lookback + 2:
        return "None", None
    recent = d.iloc[-lookback - 1 : -1]
    last = d.iloc[-1]
    prev_high = recent["High"].max()
    prev_low = recent["Low"].min()
    bull_sweep = last["Low"] < prev_low and last["Close"] > prev_low
    bear_sweep = last["High"] > prev_high and last["Close"] < prev_high
    if bull_sweep:
        return "Bullish Sweep", float(prev_low)
    if bear_sweep:
        return "Bearish Sweep", float(prev_high)
    return "None", None

def fvg_zones(df):
    d = df.copy()
    zones = []
    if len(d) < 3:
        return zones
    for i in range(2, len(d)):
        c1 = d.iloc[i - 2]
        c3 = d.iloc[i]
        if c3["Low"] > c1["High"]:
            zones.append(("Bullish FVG", float(c1["High"]), float(c3["Low"]), d.iloc[i]["Date"]))
        elif c3["High"] < c1["Low"]:
            zones.append(("Bearish FVG", float(c3["High"]), float(c1["Low"]), d.iloc[i]["Date"]))
    return zones

def amd_state(df):
    d = df.copy()
    if len(d) < 30:
        return "Unknown"
    trend = d["Close"].iloc[-1] - d["Close"].iloc[10]
    vol = d["Volume"].iloc[-10:].mean() if "Volume" in d.columns else 0
    if trend > 0 and vol > 0:
        return "Distribution"
    if trend < 0 and vol > 0:
        return "Accumulation"
    return "Manipulation"

def context_score(df):
    d = df.copy().dropna(subset=["Close", "SMA_20", "SMA_50", "RSI_14"])
    if d.empty:
        return 0, "Weak"
    last = d.iloc[-1]
    score = 0
    if last["SMA_20"] > last["SMA_50"]:
        score += 2
    if last["Close"] > last["SMA_20"]:
        score += 1
    avwap = anchored_vwap(df)
    if not avwap.empty and last["Close"] > avwap.iloc[-1]:
        score += 1
    vp = volume_profile(df)
    if not vp.empty:
        poc = vp["POC"].iloc[0]
        vah = vp["VAH"].iloc[0]
        val = vp["VAL"].iloc[0]
        if last["Close"] >= val and last["Close"] <= vah:
            score += 1
        if pd.notna(poc) and poc != 0 and abs(last["Close"] - poc) / poc < 0.02:
            score += 1
    sweep, _ = liquidity_sweep(df)
    if sweep == "Bullish Sweep":
        score += 2
    if sweep == "Bearish Sweep":
        score -= 1
    if pd.notna(last["RSI_14"]) and 40 <= last["RSI_14"] <= 65:
        score += 1
    state = amd_state(df)
    if state == "Distribution" and score >= 5:
        score += 1
    if score >= 7:
        label = "Strong"
    elif score >= 5:
        label = "Good"
    elif score >= 3:
        label = "Neutral"
    else:
        label = "Weak"
    return score, label

def support_resistance(df):
    d = df.copy().dropna(subset=["High", "Low", "Close"])
    pivots = []
    for i in range(2, len(d) - 2):
        h = d["High"].iloc[i]
        l = d["Low"].iloc[i]
        if h == d["High"].iloc[i - 2 : i + 3].max():
            pivots.append(("Resistance", float(h), d["Date"].iloc[i]))
        if l == d["Low"].iloc[i - 2 : i + 3].min():
            pivots.append(("Support", float(l), d["Date"].iloc[i]))
    return pd.DataFrame(pivots, columns=["Type", "Level", "Date"]) if pivots else pd.DataFrame(columns=["Type", "Level", "Date"])

if run_btn:
    main_ticker = st.session_state.main_ticker
    base = download_stock(main_ticker, period, interval)
    if base.empty:
        st.error(f"No valid price data returned for {main_ticker}.")
        st.stop()

    base = add_indicators(base)
    if base["Close"].dropna().empty:
        st.error(f"Close price data is missing for {main_ticker}.")
        st.stop()

    last_close = float(base["Close"].dropna().iloc[-1])
    ytd_return = float((base["Close"].iloc[-1] / base["Close"].iloc[0] - 1) * 100)
    annual_vol = float(base["Return"].rolling(20).std().iloc[-1] * np.sqrt(252)) if pd.notna(base["Return"].rolling(20).std().iloc[-1]) else np.nan
    signal = signal_label(base)
    sentiment = sentiment_label(base)
    score, score_label = context_score(base)

    backtested, strat_ret, bh_ret, trades, win_days, loss_days = backtest_crossover(base)
    split_idx = int(len(base) * backtest_split / 100)
    test_base = base.iloc[split_idx:].copy()

    mae = rmse = mape = np.nan
    steps = forecast_days if interval == "1d" else max(4, forecast_days // 5)
    arima_pred, arima_ci = forecast_arima(base.set_index("Date")["Close"], steps)
    ets_pred = forecast_ets(base.set_index("Date")["Close"], steps)

    if arima_pred is not None:
        idx = pd.bdate_range(base["Date"].iloc[-1] + pd.Timedelta(days=1), periods=len(arima_pred))
        arima_pred.index = idx
        if arima_ci is not None:
            arima_ci.index = idx
    if ets_pred is not None:
        ets_pred.index = pd.bdate_range(base["Date"].iloc[-1] + pd.Timedelta(days=1), periods=len(ets_pred))

    if len(test_base) > 10:
        try:
            train_series = base["Close"].iloc[:split_idx]
            test_series = base["Close"].iloc[split_idx:]
            eval_model = ARIMA(train_series.dropna(), order=(2, 1, 2)).fit()
            eval_fc = eval_model.get_forecast(steps=len(test_series))
            pred_eval = pd.Series(eval_fc.predicted_mean.values, index=test_series.index)
            mae, rmse, mape = forecast_metrics(test_series.values, pred_eval.values)
        except Exception:
            pass

    final_bias = "Hold"
    if signal == "Buy" and score >= 5:
        final_bias = "Buy"
    elif signal == "Exit" and score <= 3:
        final_bias = "Exit"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Last Close", f"{last_close:,.2f}")
    c2.metric("YTD Return", f"{ytd_return:.2f}%")
    c3.metric("20D Volatility", f"{annual_vol:.2%}" if pd.notna(annual_vol) else "N/A")
    c4.metric("Final Bias", final_bias)

    t1, t2, t3, t4, t5 = st.tabs(["Overview", "Forecast", "Strategy", "Compare", "Market Structure"])

    with t1:
        st.subheader("Price action")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=base["Date"], y=base["Close"], name="Close", line=dict(color="#60a5fa", width=2)))
        fig.add_trace(go.Scatter(x=base["Date"], y=base["SMA_20"], name="SMA 20", line=dict(color="#f59e0b", width=1.5)))
        fig.add_trace(go.Scatter(x=base["Date"], y=base["SMA_50"], name="SMA 50", line=dict(color="#10b981", width=1.5)))
        fig.add_trace(go.Scatter(x=base["Date"], y=base["EMA_20"], name="EMA 20", line=dict(color="#f97316", width=1.5, dash="dot")))
        fig.add_trace(go.Scatter(x=base["Date"], y=base["BB_Upper"], name="BB Upper", line=dict(color="rgba(167,139,250,0.75)", width=1), opacity=0.8))
        fig.add_trace(go.Scatter(x=base["Date"], y=base["BB_Lower"], name="BB Lower", line=dict(color="rgba(167,139,250,0.75)", width=1), fill="tonexty", fillcolor="rgba(167,139,250,0.08)", opacity=0.3))
        fig.update_layout(height=500, template="plotly_dark", legend_orientation="h")
        st.plotly_chart(fig, use_container_width=True)

        vol_fig = go.Figure()
        vol_fig.add_trace(go.Bar(x=base["Date"], y=base["Volume"], name="Volume", marker_color="rgba(56,189,248,0.6)"))
        vol_fig.update_layout(height=250, template="plotly_dark", yaxis_title="Volume")
        st.plotly_chart(vol_fig, use_container_width=True)

        colA, colB, colC = st.columns(3)
        colA.metric("Market Sentiment", sentiment)
        colB.metric("Context Score", f"{score} / 10", score_label)
        colC.metric("Signal", signal)

        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(x=base["Date"], y=base["RSI_14"], name="RSI 14", line=dict(color="#a78bfa", width=2)))
        rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
        rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
        rsi_fig.update_layout(height=280, template="plotly_dark")
        st.plotly_chart(rsi_fig, use_container_width=True)

        macd_fig = go.Figure()
        macd_fig.add_trace(go.Scatter(x=base["Date"], y=base["MACD"], name="MACD", line=dict(color="#22c55e", width=2)))
        macd_fig.add_trace(go.Scatter(x=base["Date"], y=base["MACD_Signal"], name="Signal", line=dict(color="#ef4444", width=2)))
        macd_fig.add_trace(go.Bar(x=base["Date"], y=base["MACD_Hist"], name="Histogram", marker_color="rgba(59,130,246,0.5)"))
        macd_fig.update_layout(height=300, template="plotly_dark")
        st.plotly_chart(macd_fig, use_container_width=True)

        if show_raw:
            st.dataframe(base.tail(50), use_container_width=True)

    with t2:
        st.subheader("Forecast")
        forecast_df = pd.DataFrame(index=pd.bdate_range(base["Date"].iloc[-1] + pd.Timedelta(days=1), periods=steps))
        if arima_pred is not None:
            forecast_df["ARIMA"] = arima_pred.values
            if arima_ci is not None:
                forecast_df["ARIMA_Lower"] = arima_ci.iloc[:, 0].values
                forecast_df["ARIMA_Upper"] = arima_ci.iloc[:, 1].values
        if ets_pred is not None:
            forecast_df["ETS"] = ets_pred.values

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=base["Date"], y=base["Close"], name="Historical", line=dict(color="#94a3b8", width=2)))
        if "ARIMA" in forecast_df.columns:
            fig.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df["ARIMA"], name="ARIMA", line=dict(color="#ef4444", width=3)))
        if "ETS" in forecast_df.columns:
            fig.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df["ETS"], name="ETS", line=dict(color="#22c55e", width=3, dash="dot")))
        if "ARIMA_Lower" in forecast_df.columns and "ARIMA_Upper" in forecast_df.columns:
            fig.add_trace(go.Scatter(
                x=forecast_df.index.tolist() + forecast_df.index[::-1].tolist(),
                y=forecast_df["ARIMA_Upper"].tolist() + forecast_df["ARIMA_Lower"][::-1].tolist(),
                fill="toself",
                fillcolor="rgba(239,68,68,0.16)",
                line=dict(color="rgba(255,255,255,0)"),
                name="ARIMA 95% CI"
            ))
        fig.update_layout(height=550, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(forecast_df.round(2), use_container_width=True)
        csv = forecast_df.reset_index().rename(columns={"index": "Date"}).to_csv(index=False).encode("utf-8")
        st.download_button("Download forecast CSV", csv, file_name=f"{main_ticker}_forecast.csv", mime="text/csv")
        st.write(f"Accuracy on holdout: MAE={mae:.2f} | RMSE={rmse:.2f} | MAPE={mape:.2f}%")

    with t3:
        st.subheader("Strategy and signal panel")
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Signal", signal)
        s2.metric("Sentiment", sentiment)
        s3.metric("Trades", trades)
        s4.metric("Context", score_label)

        st.write(f"Buy/Hold/Exit logic is based on SMA20 vs SMA50 and RSI. Current view: **{signal}**.")
        st.write(f"Backtest return: **{strat_ret:.2%}** | Buy & Hold: **{bh_ret:.2%}** | Winning days: **{win_days}** | Losing days: **{loss_days}**")
        st.write(f"Accuracy: MAE **{mae:.2f}** | RMSE **{rmse:.2f}** | MAPE **{mape:.2f}%**")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=backtested["Date"], y=backtested["Equity"], name="Strategy Equity", line=dict(color="#00d4aa", width=3)))
        fig.add_trace(go.Scatter(x=backtested["Date"], y=backtested["BuyHold"], name="Buy & Hold", line=dict(color="#38bdf8", width=2, dash="dot")))
        fig.update_layout(height=500, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with t4:
        st.subheader("Compare selected stocks")
        rows = []
        for t in [st.session_state.main_ticker]:
            d = download_stock(t, period, interval)
            if d.empty:
                continue
            d = add_indicators(d)
            rows.append({
                "Ticker": t,
                "Last Close": float(d["Close"].iloc[-1]),
                "YTD Return %": float((d["Close"].iloc[-1] / d["Close"].iloc[0] - 1) * 100),
                "Volatility %": float(d["Return"].rolling(20).std().iloc[-1] * np.sqrt(252) * 100) if pd.notna(d["Return"].rolling(20).std().iloc[-1]) else np.nan,
                "Signal": signal_label(d),
                "Sentiment": sentiment_label(d),
            })
        comp = pd.DataFrame(rows)
        st.dataframe(comp, use_container_width=True)

        if not comp.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=comp["Ticker"], y=comp["YTD Return %"], name="YTD Return %"))
            fig.update_layout(height=420, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

    with t5:
        st.subheader("Market Structure")
        avwap = anchored_vwap(base)
        vp = volume_profile(base)
        sweep, sweep_level = liquidity_sweep(base)
        zones = fvg_zones(base)
        amd = amd_state(base)
        sr = support_resistance(base)

        c1m, c2m, c3m = st.columns(3)
        c1m.metric("Context Score", f"{score} / 10", score_label)
        c2m.metric("Liquidity Sweep", sweep)
        c3m.metric("AMD State", amd)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=base["Date"], y=base["Close"], name="Close", line=dict(color="#60a5fa", width=2)))
        fig.add_trace(go.Scatter(x=base["Date"], y=base["SMA_20"], name="SMA 20", line=dict(color="#f59e0b", width=1.5)))
        fig.add_trace(go.Scatter(x=base["Date"], y=base["SMA_50"], name="SMA 50", line=dict(color="#10b981", width=1.5)))
        if not avwap.empty:
            fig.add_trace(go.Scatter(x=avwap.index, y=avwap.values, name="Anchored VWAP", line=dict(color="#a78bfa", width=2)))
        if sweep_level is not None:
            fig.add_hline(y=sweep_level, line_dash="dash", line_color="#f43f5e")
        if not sr.empty:
            for _, r in sr.tail(8).iterrows():
                fig.add_hline(y=float(r["Level"]), line_dash="dot", line_color="rgba(255,255,255,0.25)")
        fig.update_layout(height=520, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        if not vp.empty:
            st.write("Volume Profile")
            vp_fig = go.Figure()
            vp_fig.add_trace(go.Bar(x=vp["volume"], y=vp["price"], orientation="h", name="Volume"))
            vp_fig.update_layout(height=420, template="plotly_dark")
            st.plotly_chart(vp_fig, use_container_width=True)
            poc = vp["POC"].iloc[0]
            vah = vp["VAH"].iloc[0]
            val = vp["VAL"].iloc[0]
            st.write(f"POC: {poc:.2f} | VAH: {vah:.2f} | VAL: {val:.2f}")

        if zones:
            zone_df = pd.DataFrame(zones, columns=["Type", "Lower", "Upper", "Date"])
            st.dataframe(zone_df.tail(20), use_container_width=True)
        else:
            st.info("No recent FVG zones detected.")

        if not sr.empty:
            st.write("Support / Resistance")
            st.dataframe(sr.tail(20), use_container_width=True)

    st.success("Analysis completed.")
