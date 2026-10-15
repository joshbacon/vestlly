## Fetch all the data, the price history but also alll the indicator values
## store it in a formatted json file the other scripts can read in

import json, os, io
import pandas as pd
import yfinance as yf

def load_local_data(ticker: str) -> dict:
    data = {"ticker": ticker, "info": {}, "history": None, "currentPrice": None}
    with open(f"output/{ticker.split('.')[0].lower()}.json", "r") as f:
        info = json.load(f)
    if info['info'] is None:
        print(f"{ticker} - No info")
        return data
    data['info'] = info
    data['history'] = pd.read_csv(f"output/{ticker.split('.')[0].lower()}.csv", index_col="Date")
    return data


def load_local_set(tickers: list[str]) -> list[dict]:
    results = []
    for t in tickers:
        results.append(load_local_data(t))
    return results


def fetch_stock_data(ticker: str) -> dict:
    # Fetch fundamentals and recent price history for a stock
    stock = yf.Ticker(ticker)
    info = stock.info

    data = {"ticker": ticker, "info": info, "history": None, "currentPrice": None}

    # Price history for mean reversion (2 year)
    hist = stock.history(period="2y")
    if not hist.empty:
        data["currentPrice"] = float(hist["Close"].iloc[-1])
        with io.open(os.path.join('output',f'{ticker.split(".")[0].lower()}.json'), 'w') as f:
            f.write(json.dumps({}))
        with open(f"output/{ticker.split('.')[0].lower()}.json", "w") as f:
            json.dump(data, f, indent=2)
        data["history"] = hist["Close"]
        data['history'].to_csv(f"output/{ticker.split('.')[0].lower()}.csv")
    elif "currentPrice" in info:
        data["currentPrice"] = float(info["currentPrice"])
    elif "regularMarketPrice" in info:
        data["currentPrice"] = float(info["regularMarketPrice"])

    return data


def fetch_set(tickers: list[str]) -> list[dict]:
    results = []
    for t in tickers:
        results.append(fetch_stock_data(t))


def load_labeled_sample(record: dict) -> dict:
    ticker = record["ticker"]
    label  = record["label"]        # ground truth

    # Fetch full history; we'll slice it to the snapshot date
    sd = load_local_data(ticker)   # still uses cache
    history = sd["history"]

    # Slice history up to (not past) the snapshot date so we don't leak
    # future prices into the mean-reversion signal
    history.index = pd.to_datetime(history.index, utc=True).tz_localize(None)
    snapshot_date = pd.Timestamp(record["date"])
    if history is not None:
        history = history[history.index <= snapshot_date]

    currentPrice = float(history.iloc[-1]) if history is not None and not history.empty else None

    # Build an info dict from the record's indicator columns
    key_map = [
        "epsCurrentYear",
        "pegRatio",
        "priceToSalesTrailing12Months",
        "priceToBook",
        "debtToEquity",
        "bookValue",
        "targetMeanPrice",
        "freeCashflow",
        "returnOnEquity",
    ]
    info = {k: record[k] for k in key_map if k in record}

    return {
        "ticker":        ticker,
        "label":         label,
        "info":          info,
        "history":       history,
        "currentPrice":  currentPrice,
    }