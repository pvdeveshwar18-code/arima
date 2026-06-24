# Indian Stocks Forecast Pro

A modern Streamlit dashboard for Indian stock analysis using Yahoo Finance data, technical indicators, ARIMA forecasting, Exponential Smoothing, backtesting, and market structure analysis.

## Features

- Historical stock data from Yahoo Finance.
- Supports Indian tickers like `TCS.NS`, `INFY.NS`, `RELIANCE.NS`, and more.
- Trend analysis using SMA 20, SMA 50, EMA 20, and RSI 14.
- Forecasting with:
  - ARIMA
  - Exponential Smoothing
- Backtesting against a simple moving-average crossover strategy.
- Buy / Hold / Exit signal panel.
- Market Structure tab with:
  - Anchored VWAP
  - Volume Profile
  - Liquidity Sweep detection
  - FVG / IFVG-style imbalance zones
  - AMD regime label
  - Combined context score
- Dark premium UI with Streamlit theme configuration.
- CSV download for forecast results.

## Important note

This app is for educational and analytical purposes only. Forecasts are not guaranteed, and the market can behave unpredictably. Use proper risk management and do your own research before making trading decisions.

## Tech Stack

- Python
- Streamlit
- yfinance
- Pandas
- NumPy
- Plotly
- Statsmodels
- scikit-learn

## Project Structure

```txt
your-repo-name/
├── app.py
├── requirements.txt
├── README.md
└── .streamlit/
    └── config.toml
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

1. Enter one or more Indian stock tickers, one per line.
2. Choose the history range, interval, and forecast horizon.
3. Click **Run analysis**.
4. Review:
   - overview charts
   - forecast chart
   - strategy backtest
   - comparison table
   - market structure tab

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

1. Push the repository to GitHub.
2. Make sure `app.py`, `requirements.txt`, and `.streamlit/config.toml` are in the repository.
3. Go to [Streamlit Community Cloud](https://share.streamlit.io/).
4. Connect your GitHub account.
5. Click **New app**.
6. Select your repository, branch, and `app.py` as the main file.
7. Deploy the app.

## Troubleshooting

### No data returned
- Check that the ticker is valid.
- Use `.NS` for NSE symbols.
- Try a major ticker like `INFY.NS` or `RELIANCE.NS`.

### App fails on Streamlit Cloud
- Make sure `requirements.txt` is in the repository root.
- Ensure `.streamlit/config.toml` is inside the `.streamlit` folder.
- Re-deploy after updating dependencies.

### Forecast looks weak or empty
- Use a longer history range like `5y`.
- Some stocks may not have enough data for ARIMA or backtesting.
- Try the daily interval instead of weekly for more detail.

## License

For educational use only.
