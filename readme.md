# Indian Stocks Forecast Dashboard

A modern Streamlit dashboard for Indian stock analysis using Yahoo Finance data, ARIMA forecasting, Exponential Smoothing, technical indicators, backtesting, and buy/hold/exit signals.

## Features

- Fetches historical stock data from Yahoo Finance using `yfinance`.
- Supports Indian tickers such as `TCS.NS`, `INFY.NS`, `RELIANCE.NS`, and other NSE/BSE symbols.
- Forecasts future price movement using:
  - ARIMA
  - Exponential Smoothing
- Displays:
  - Historical price charts
  - Forecast charts with confidence interval
  - RSI and moving averages
  - Market sentiment
  - Buy / Hold / Exit signal panel
  - Backtest comparison against buy-and-hold
  - Cross-stock comparison table
- Modern dark UI designed for easy reading and analysis.
- Downloadable forecast CSV.

## Why this project

This project is built for:
- Swing trading analysis
- Long-term holding analysis
- Educational forecasting and dashboarding
- Portfolio comparison of Indian stocks

## Important note

This app is for educational and analytical use only. Stock forecasts are not guaranteed, and no model can predict markets with certainty. Use risk management and your own judgment before making trading decisions.

## Tech Stack

- Python
- Streamlit
- Yahoo Finance (`yfinance`)
- Pandas
- NumPy
- Plotly
- Statsmodels
- Scikit-learn

## Project Structure

```txt
your-repo/
├── app.py
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Run locally

```bash
streamlit run app.py
```

## How to use

1. Open the app in your browser.
2. Enter one or more Indian stock tickers, one per line.
3. Choose the history range and forecast horizon.
4. Click **Run analysis**.
5. Review:
   - price chart
   - forecast chart
   - signal panel
   - backtest results
   - comparison table

## Example tickers

```txt
TCS.NS
INFY.NS
RELIANCE.NS
HDFCBANK.NS
SBIN.NS
ICICIBANK.NS
ITC.NS
LT.NS
```

## Deployment on Streamlit Cloud

1. Push this project to GitHub.
2. Make sure `app.py` and `requirements.txt` are in the repo root.
3. Go to [Streamlit Community Cloud](https://share.streamlit.io/).
4. Connect your GitHub account.
5. Click **New app**.
6. Select your repository, branch, and `app.py` as the main file.
7. Click **Deploy**.

## Requirements

Your `requirements.txt` should include:

```txt
streamlit>=1.30.0
yfinance>=0.2.40
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
statsmodels>=0.14.0
scikit-learn>=1.3.0
```

## Troubleshooting

### No data returned
- Make sure the ticker is valid.
- Use `.NS` for NSE stocks.
- Try another ticker like `INFY.NS` or `RELIANCE.NS`.

### App crashes on Streamlit Cloud
- Confirm `requirements.txt` exists in the repo root.
- Re-deploy after every file change.
- Check the Streamlit app logs for package or data issues.

### Forecast looks empty
- Some tickers may not have enough history for ARIMA or backtesting.
- Try a longer history range like `5y`.

## License

For educational use only.
