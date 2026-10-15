# run the yfinance info and record it daily

import json, os, io
import yfinance as yf
from datetime import datetime

tickers = [
    "BMO.TO",   "RY.TO",    "TD.TO",    "BNS.TO",   "CM.TO",
    "MFC.TO",   "POW.TO",   "TF.TO",    "CNQ.TO",   "SU.TO",
    "PXT.TO",   "BTE.TO",   "ENB.TO",   "WCP.TO",   "CJ.TO",
    "T.TO",     "BCE.TO",   "RUS.TO",   "IMG.TO",   "TXG.TO",
    "AGI.TO",   "OLA.TO",   "PPTA.TO",  "DPM.TO",   "SKE.TO",
    "FTS.TO",   "PPL.TO",   "NA.TO",    "TRP.TO",   "SLF.TO",
    "X.TO"
]

def store_data(ticker: str):
    stock = yf.Ticker(ticker)
    info = stock.info
    with io.open(os.path.join("history",f"{ticker.split('.')[0].lower()}_{datetime.today().strftime('%Y-%m-%d')}.json"), 'w') as f:
        f.write(json.dumps({}))
    with open(f"history/{ticker.split('.')[0].lower()}_{datetime.today().strftime('%Y-%m-%d')}.json", "w") as f:
        json.dump(info, f, indent=2)

for t in tickers:
    store_data(t)