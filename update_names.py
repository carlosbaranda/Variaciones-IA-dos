
import yfinance as yf
import json
from tickers import TICKERS_BY_MARKET

def get_company_names(tickers):
    names = {}
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            names[ticker] = info.get("shortName", ticker)
        except Exception:
            names[ticker] = ticker
    return names

if __name__ == "__main__":
    all_tickers = set()
    for tickers in TICKERS_BY_MARKET.values():
        all_tickers.update(tickers)

    names_dict = get_company_names(list(all_tickers))

    with open("company_names.json", "w", encoding="utf-8") as f:
        json.dump(names_dict, f, ensure_ascii=False, indent=2)

    print(f"Guardado {len(names_dict)} nombres en company_names.json")
