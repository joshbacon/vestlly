

import yfinance as yf
from typing import Optional
from tqdm import tqdm
import pandas as pd
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════════════
#  Fetch stock data in window
# ══════════════════════════════════════════════════════════════════════════════

def fetch_stock_data(ticker: str, local: bool) -> Optional[dict]:
    try:
        config = {
            "period":       "20d",
            "default_eps":  0.0,
            "default_peg":  10.0,
            "default_ptb":  5.0,
            "default_dte":  5.0,
            "default_pts":  5.0,
        }
        stock = yf.Ticker(ticker)
        info  = stock.info
        if (local):
            folder = Path("backdata")
            hist = [pd.read_csv(f) for f in folder.glob(f"{ticker}.csv")][0]
        else:
            hist = stock.history(period=config['period'])
            hist.to_csv(f"backdata/{ticker}.csv")

        ###      *** Get historic data ***       ###
        if hist.empty:
            return None

        hist = hist[["Close"]].dropna().reset_index()
        prices = hist["Close"].values.astype(float)
        if "Date" in hist.columns:
            raw_dates = hist["Date"]
            # Convert to plain Python date objects for matplotlib
            dates_dt = [d.date() if hasattr(d, "date") else d for d in raw_dates]
            dates_str = [str(d) for d in dates_dt]
        else:
            dates_dt = list(hist.index)
            dates_str = [str(d) for d in dates_dt]

        ###      *** Get relevant indicator values ***       ###
        eps = info.get("epsCurrentYear") or info.get("forwardEps") or info.get("trailingEps")
        if eps and float(eps) > 0:
            eps = float(eps)
        else:
            eps = config["default_eps"]

        peg = info.get("pegRatio")
        if peg and float(peg) > 0:
            peg = float(peg)
        else:
            peg = config["default_peg"]

        pts = info.get("priceToSalesTrailing12Months")
        if pts and float(pts) > 0:
            pts = float(pts)
        else:
            pts = config["default_pts"]

        ptb = info.get("priceToBook")
        if ptb and float(ptb) > 0:
            ptb = float(ptb)
        else:
            ptb = config["default_ptb"]

        dte = info.get("debtToEquity")
        if dte and float(dte) > 0:
            dte = float(dte)
        else:
            dte = config["default_dte"]

        return {
            "ticker":    ticker,
            "sector":    info.get("sectorKey"),
            "name":      info.get("longName"),
            "prices":    prices,
            "dates_str": dates_str,
            "dates_dt":  dates_dt,
            "eps":       eps,
            "peg":       peg,
            "pts":       dte,
            "ptb":       ptb,
            "dte":       dte,
        }
    
    except Exception as exc:
        return None


def fetch_all_stocks(tickers: list[str], local: bool) -> list[dict]:
    results = []
    for ticker in tqdm(
        tickers,
        desc=f"Loading Stocks",
        colour="magenta",
        ncols=95,
        unit="stocks"
    ):
        data = fetch_stock_data(ticker, local)
        if data:
            results.append(data)
    return results


## TODO: create a database or something to hold
# decision making data to display on the app

# Indicators
## List of indicators to optimize for each sector
# TODO: run the GAs for each indicator on each sector (already have the GA for PEG... and maybe EPS....)
indicators = [
    {
        "title": "EPS",
        "ideal": 3.0,
        "entry_stds": {
            "financial-services": 2.451,
            "energy": 1.0,
            "communication-services": 1.0,
            "industrials": 1.0,
            "basic-materials": 1.0,
        },
        "exit_stds": {
            "financial-services": 3.5,
            "energy": 1.0,
            "communication-services": 1.0,
            "industrials": 1.0,
            "basic-materials": 1.0,
        },
    },
    {
        "title": "PEG",
        "ideal": 1.0,
        "entry_stds": {
            "financial-services": 2.585,
            "energy": 1.0,
            "communication-services": 1.0,
            "industrials": 1.0,
            "basic-materials": 1.0,
        },
        "exit_stds": {
            "financial-services": 3.411,
            "energy": 1.0,
            "communication-services": 1.0,
            "industrials": 1.0,
            "basic-materials": 1.0,
        },
    },
    {
        "title": "P/S",
        "ideal": 1.0,
        "entry_stds": {
            "financial-services": 1.0,
            "energy": 1.0,
            "communication-services": 1.0,
            "industrials": 1.0,
            "basic-materials": 1.0,
        },
        "exit_stds": {
            "financial-services": 1.0,
            "energy": 1.0,
            "communication-services": 1.0,
            "industrials": 1.0,
            "basic-materials": 1.0,
        },
    },
    {
        "title": "P/B",
        "ideal": 1.0,
        "entry_stds": {
            "financial-services": 1.0,
            "energy": 1.0,
            "communication-services": 1.0,
            "industrials": 1.0,
            "basic-materials": 1.0,
        },
        "exit_stds": {
            "financial-services": 1.0,
            "energy": 1.0,
            "communication-services": 1.0,
            "industrials": 1.0,
            "basic-materials": 1.0,
        },
    },
    {
        "title": "D/E",
        "ideal": 1.0,
        "entry_stds": {
            "financial-services": 1.0,
            "energy": 1.0,
            "communication-services": 1.0,
            "industrials": 1.0,
            "basic-materials": 1.0,
        },
        "exit_stds": {
            "financial-services": 1.0,
            "energy": 1.0,
            "communication-services": 1.0,
            "industrials": 1.0,
            "basic-materials": 1.0,
        },
    }
]
