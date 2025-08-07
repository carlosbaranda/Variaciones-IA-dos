
import yfinance as yf
import pandas as pd

def load_data_for_market(tickers):
    all_data = []
    for ticker in tickers:
        try:
            data = yf.Ticker(ticker).history(period="1y")
            data["Ticker"] = ticker
            all_data.append(data)
        except:
            continue
    if not all_data:
        return pd.DataFrame()
    return pd.concat(all_data).reset_index()
