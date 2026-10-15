"""
Read in the history folder and generate a list of dicts that holds:
    ticker,
    date,
    label,  [BUY|SELL|HOLD]
    eps,
    peg,
    pts,
    ptb,
    dte,
    bv,
    target,
    fcf,
    roe

Write this file to the training directory
"""

import os
import json
import pandas as pd
import yfinance as yf

labeled = []

for e in os.scandir("./history"):
    if e.is_file():
        with open(e.path, "r") as f:
            data = json.load(f)
            stock = yf.Ticker(data["symbol"])
            hist = stock.history(period="2y")["Close"]
            labeled.append({
                "ticker": data["symbol"],
                "date": e.name.split(".")[0].split("_")[1],
                "label": "BUY" if data["dayHigh"] > data["previousClose"] * 1.013 else "HOLD" if data["dayHigh"] > data["previousClose"] else "SELL",
                "info": {
                    "epsCurrentYear": data["epsCurrentYear"] if "epsCurrentYear" in data else None,
                    "pegRatio": data["pegRatio"] if "pegRatio" in data else None,
                    "priceToSalesTrailing12Months": data["priceToSalesTrailing12Months"] if "priceToSalesTrailing12Months" in data else None,
                    "priceToBook": data["priceToBook"] if "priceToBook" in data else None,
                    "debtToEquity": data["debtToEquity"] if "debtToEquity" in data else None,
                    "bookValue": data["bookValue"] if "bookValue" in data else None,
                    "targetMeanPrice": data["targetMeanPrice"] if "targetMeanPrice" in data else None,
                    "freeCashflow": data["freeCashflow"] if "freeCashflow" in data else None,
                    "returnOnEquity": data["returnOnEquity"] if "returnOnEquity" in data else None,
                    "marketCap": data["marketCap"] if "marketCap" in data else None
                },
                "currentPrice": data["currentPrice"],
                "history": hist.to_list()
            })


# print(labeled)
pd.DataFrame(labeled).to_csv("../training/data/labeled.csv", index=False)