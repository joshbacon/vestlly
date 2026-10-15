import json
from evaluate import analyze_stock
from genome import Genome
from data import load_local_data
import pandas as pd
import csv

# want ot evaluate a stock base don the latest genome

tickers = [
    "BMO.TO",   "RY.TO",    "TD.TO",    "BNS.TO",   "CM.TO",
    "MFC.TO",   "POW.TO",   "TF.TO",    "CNQ.TO",   "SU.TO",
    "PXT.TO",   "BTE.TO",   "ENB.TO",   "WCP.TO",   "CJ.TO",
    "T.TO",     "BCE.TO",   "RUS.TO",   "IMG.TO",   "TXG.TO",
    "AGI.TO",   "OLA.TO",   "PPTA.TO",  "DPM.TO",   "SKE.TO",
    "FTS.TO",   "PPL.TO",   "NA.TO",    "TRP.TO",   "SLF.TO",
    "X.TO"
]

TICKERS = []
with open('./data/labeled.csv', 'r') as f:
    for row in csv.DictReader(f):
        TICKERS.append({
            "ticker": row["ticker"],
            "date": row["date"],
            "label": row["label"],
            "info": eval(row["info"]),
            "currentPrice": float(row["currentPrice"]),
            "history": pd.DataFrame([float(p.lstrip()) for p in row["history"].replace('[', '').replace(']', '').split(",")])
        })

with open('./output/_genome.json') as f:
    data = json.load(f)
    ge = Genome.__new__(Genome)
    ge.indicator_weights = data['indicator_weights']
    ge.indicator_penalty_scales = data['indicator_penalty_scales']
    ge.reversion_window = data['reversion_window']
    ge.reversion_weight = data['reversion_weight']
    ge.signal_threshold = data['signal_threshold']
    for t in TICKERS:
        print(analyze_stock(t, ge))

# with open(f"output/_genome.json", "r") as f:
#     data = json.load(f)

# ge = Genome.__new__(Genome)
# ge.indicator_weights = data['indicator_weights']
# ge.indicator_penalty_scales = data['indicator_penalty_scales']
# ge.reversion_window = data['reversion_window']
# ge.reversion_weight = data['reversion_weight']
# ge.signal_threshold = data['signal_threshold']

# print(ge)

# tickers = [
#     "BMO.TO",   "RY.TO",    "TD.TO",    "BNS.TO",   "CM.TO",
#     "MFC.TO",   "POW.TO",   "TF.TO",    "CNQ.TO",   "SU.TO",
#     "PXT.TO",   "BTE.TO",   "ENB.TO",   "WCP.TO",   "CJ.TO",
#     "T.TO",     "BCE.TO",   "RUS.TO",   "IMG.TO",   "TXG.TO",
#     "AGI.TO",   "OLA.TO",   "PPTA.TO",  "DPM.TO",   "SKE.TO",
#     "FTS.TO",   "PPL.TO",   "NA.TO",    "TRP.TO",   "SLF.TO",
#     "X.TO"
# ]

# urls = [
#     "https://www.marketbeat.com/img/logos/thumbnail/bank-of-montreal-logo.jpg?s=thumb",
#     "https://www.marketbeat.com/img/logos/thumbnail/royal-bank-of-canada-logo.png?s=thumb",
#     "https://www.marketbeat.com/img/logos/thumbnail/toronto-dominion-bank-logo.png?s=thumb",
#     "https://www.marketbeat.com/img/logos/thumbnail/the-bank-of-nova-scotia-logo.jpg?s=thumb",
#     "https://www.marketbeat.com/img/logos/thumbnail/canadian-imperial-bank-of-commerce-logo.png?s=thumb",
#     "https://www.marketbeat.com/img/logos/thumbnail/manulife-financial-corp-logo.png?s=thumb",
#     "https://www.marketbeat.com/img/logos/thumbnail/power-co-of-canada-logo.png?s=thumb&v=20240530114932",
#     "https://www.marketbeat.com/img/logos/thumbnail/timbercreek-financial-corp-logo.png?s=thumb&v=20241015074430",
#     "https://www.marketbeat.com/img/logos/thumbnail/canadian-natural-resources-limited-logo.jpg?s=thumb",
#     "https://www.marketbeat.com/img/logos/thumbnail/suncor-energy-inc-logo.jpg?s=thumb&v=20240529142631",
#     "https://www.marketbeat.com/img/logos/thumbnail/parex-resources-inc-logo.png?s=thumb&v=20241015095328",
#     "https://www.marketbeat.com/img/logos/thumbnail/baytex-energy-logo.jpg?s=thumb",
#     "https://www.marketbeat.com/img/logos/thumbnail/enbridge-logo.jpg?s=thumb",
#     "https://www.marketbeat.com/img/logos/thumbnail/whitecap-resources-inc-logo.png?s=thumb&v=20221110155833",
#     "https://www.marketbeat.com/img/logos/thumbnail/cardinal-energy-ltd-logo.png?s=thumb&v=20240605081722",
#     "https://www.marketbeat.com/img/logos/thumbnail/telus-logo.jpg?s=thumb",
#     "https://www.marketbeat.com/img/logos/thumbnail/bce-inc-logo.jpg?s=thumb",
#     "https://www.marketbeat.com/img/logos/thumbnail/russel-metals-inc-logo.png?s=thumb&v=20221128144953",
#     "https://www.marketbeat.com/img/logos/thumbnail/iamgold-co-logo.png?s=thumb&v=20240605074343",
#     "https://www.marketbeat.com/img/logos/thumbnail/torex-gold-resources-inc-logo.png?s=thumb&v=20240605075314",
#     "https://www.marketbeat.com/img/logos/thumbnail/alamos-gold-inc-logo.jpg?s=thumb",
#     "https://www.marketbeat.com/img/logos/thumbnail/orla-mining-ltd-logo.jpg?s=thumb&v=20210803142230",
#     "https://www.marketbeat.com/img/logos/thumbnail/perpetua-resources-corp-logo.jpg?s=thumb&v=20221219140617",
#     "https://www.marketbeat.com/img/logos/thumbnail/dundee-precious-metals-inc-logo.jpg?s=thumb&v=20240604154022",
#     "https://www.marketbeat.com/img/logos/thumbnail/skeena-resources-limited-logo.png?s=thumb&v=20240606112414",
#     "https://www.marketbeat.com/img/logos/thumbnail/fortis-inc-logo.png?s=thumb&v=20240529140936",
#     "https://www.marketbeat.com/img/logos/thumbnail/pembina-pipeline-logo.jpg?s=thumb",
#     "https://www.marketbeat.com/img/logos/thumbnail/national-bank-of-canada-logo.png?s=thumb",
#     "https://www.marketbeat.com/img/logos/thumbnail/transcanada-logo.jpg?s=thumb",
#     "https://www.marketbeat.com/img/logos/thumbnail/sun-life-financial-inc-logo.png?s=thumb&v=20221101143208",
#     "https://www.marketbeat.com/img/logos/thumbnail/tmx-group-inc-logo.png?s=thumb",
# ]
# for t in tickers:
#     print(f"https://www.marketbeat.com/stocks/TSE/{t.split('.')[0]}/")
# for i, url in enumerate(urls):
#     print(f"UPDATE stocks SET img = '{url}' where sid = {i};")
#     # anal = analyze_stock(t, ge)
    # print(load_local_data(t))
    # with open(f"output/{t.split('.')[0].lower()}.json", "r") as f:
    #     data = json.load(f)["info"]
    #     dte = 1.5
    #     pts = 2.0
    #     try:
    #         dte = data['debtToEquity']
    #     except:
    #         pass
    #     try:
    #         pts = data['priceToSalesTrailing12Months']
    #     except:
    #         pass
    #     peg = data['trailingPegRatio']
    #     if not peg:
    #         peg = "NULL"
        # print(f"INSERT INTO stocks (sid, ticker, score, action, eps, peg, pts, ptb, dte, meanstd, img) VALUES ({i}, \"{t}\", {anal['score']}, \"{anal['signal']}\", {data['epsCurrentYear']}, {peg}, {pts}, {data['priceToBook']}, {dte}, {data['fiftyDayAverageChangePercent']}, );")
