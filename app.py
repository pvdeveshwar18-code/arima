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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

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

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

div[data-testid="stMetric"] {
    background: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 14px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.18);
}

div[data-baseweb="tab-list"] {
    gap: 10px;
}

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
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-bottom: 1rem;">
    <h1 style="margin:0; font-size:2.3rem; font-weight:800; background: linear-gradient(90deg,#00d4aa,#38bdf8,#a78bfa); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
        Indian Stocks Forecast Pro
    </h1>
    <p style="margin:0.25rem 0 0 0; color: rgba(229,231,235,.65);">
        Clean forecasting, trend signals, backtesting, and comparison for Indian stocks
    </p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Controls")
    tickers_input = st.text_area("Indian stock tickers (one per line)", value="TCS.NS\nINFY.NS\nRELIANCE.NS")
    tickers = [t.strip().upper() for t in tickers_input.splitlines() if t.strip()]

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
    for order in [(5,1,0), (2,1,2), (1,1,1)]:
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

if run_btn:
    if not tickers:
        st.error("Add at least one ticker.")
        st.stop()

    main_ticker = tickers[0]
    base = download_stock(main_ticker, period, interval)
    if base.empty:
        st.error(f"No valid price data returned for {main_ticker}. Try INFY.NS or RELIANCE.NS.")
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

    backtested, strat_ret, bh_ret, trades, win_days, loss_days = backtest_crossover(base)
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

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Last Close", f"{last_close:,.2f}")
    c2.metric("YTD Return", f"{ytd_return:.2f}%")
    c3.metric("20D Volatility", f"{annual_vol:.2%}" if pd.notna(annual_vol) else "N/A")
    c4.metric("Signal", signal)

    t1, t2, t3, t4 = st.tabs(["Overview", "Forecast", "Strategy", "Compare"])

    with t1:
        st.subheader("Price action")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=base["Date"], y=base["Close"], name="Close", line=dict(color="#60a5fa", width=2)))
        fig.add_trace(go.Scatter(x=base["Date"], y=base["SMA_20"], name="SMA 20", line=dict(color="#f59e0b", width=1.5)))
        fig.add_trace(go.Scatter(x=base["Date"], y=base["SMA_50"], name="SMA 50", line=dict(color="#10b981", width=1.5)))
        fig.update_layout(height=500, template="plotly_dark", legend_orientation="h")
        st.plotly_chart(fig, use_container_width=True)

        colA, colB = st.columns(2)
        colA.metric("Market Sentiment", sentiment)
        colB.metric("Backtest Return", f"{strat_ret:.2%}" if pd.notna(strat_ret) else "N/A")

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=base["Date"], y=base["RSI_14"], name="RSI 14", line=dict(color="#a78bfa", width=2)))
        fig2.add_hline(y=70, line_dash="dash", line_color="red")
        fig2.add_hline(y=30, line_dash="dash", line_color="green")
        fig2.update_layout(height=300, template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

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

    with t3:
        st.subheader("Strategy and signal panel")
        s1, s2, s3 = st.columns(3)
        s1.metric("Signal", signal)
        s2.metric("Sentiment", sentiment)
        s3.metric("Trades", trades)

        st.write(f"Buy/Hold/Exit logic is based on SMA20 vs SMA50 and RSI. Current view: **{signal}**.")
        st.write(f"Backtest return: **{strat_ret:.2%}** | Buy & Hold: **{bh_ret:.2%}** | Winning days: **{win_days}** | Losing days: **{loss_days}**")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=backtested["Date"], y=backtested["Equity"], name="Strategy Equity", line=dict(color="#00d4aa", width=3)))
        fig.add_trace(go.Scatter(x=backtested["Date"], y=backtested["BuyHold"], name="Buy & Hold", line=dict(color="#38bdf8", width=2, dash="dot")))
        fig.update_layout(height=500, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with t4:
        st.subheader("Compare selected stocks")
        rows = []
        for t in tickers[:10]:
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

    st.success("Analysis completed.")
