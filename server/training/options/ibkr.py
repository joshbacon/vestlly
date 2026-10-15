# Use snaptrade connection to interactive broker
# automate 0 DTE iron butterflies on the SPX

# considerations
# - time of day (do high volatility trades during opening (short iron condor), and low volatility trades during lunch)

# Iron Butterfly:
# - low volitility is good
# - time decay (probably want a lot, but it's 0DTE so this is kinda as solved as it can be?)
# - implied volatility: inflates premiums
# - theta == good (theta IS time decay)
# - no big events coming up (don't trade on earnings days for market makers)
# - trading in strong support/resistace zone (what is this exactly?)

# wider vs taller: buying wider wings increases profit & risk but also break-even points (want them at least 2% out)


# find an option backtester (https://optionstradingtoolbox.com/blog/10-best-options-backtesting-tools-for-2025-free-paid)






from time import sleep
from snaptrade_client import SnapTrade
import webbrowser


# Moving Average Crossover
# - Use as an indicator to buy a put or call (ATM?)

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

small_window = 10
large_window = 31
hist = pd.read_csv("spx_hist.csv")

hist['shortSMA'] = hist['Close'].rolling(window=small_window).mean()
hist['longSMA'] = hist['Close'].rolling(window=large_window).mean()
hist['SMAdiff'] = hist['shortSMA'] - hist['longSMA']
hist['SMAoverunder'] = ["over" if b > 0 else "under" for b in hist['SMAdiff']]
hist['sma_ou_shift'] = hist['SMAoverunder'].shift(1)
signals = []
for i, b in enumerate(hist['SMAoverunder']):
    if b == 'over' and hist['sma_ou_shift'].iloc[i] == 'under':
        signals.append('buy')
    elif b == 'under' and hist['sma_ou_shift'].iloc[i] == 'over':
        signals.append('sell')
    else:
        signals.append('hold')
hist['SMAsignal'] = signals
to_drop = hist[hist['SMAsignal'] == 'hold'].index
hist.drop(to_drop, inplace=True)
hist['SMAdollardiff'] = hist['Close'] - hist['Close'].shift(1)
hist = hist[hist['SMAsignal'] != 'hold']


outputPath = 'MAcrossover/output1031.txt'
print(hist[::-1], file=open(outputPath, "a"))

data = hist[::-1]


fig, ax = plt.subplots()

ax.plot(data['Date'], data['Close'])
plt.xticks(rotation=45)


total = 0
currEntry = 0
for i, s in enumerate(data['SMAsignal']):
    if s == "buy":
        currEntry = data.iloc[i]['Close']
    if s == "sell":
        total += data.iloc[i]['Close'] - currEntry
        print(f"Closing ${currEntry} entry position at ${data.iloc[i]['Close']} (${(data.iloc[i]['Close'] - currEntry):2f} profit)", file=open(outputPath, "a"))
        currEntry = 0

print(f"Total return: ${total:2f}", file=open(outputPath, "a"))


plt.show()



# EMA (Exponential Moving Average) which gives more weight to recent values and reacts faster to changes.
# hist['shortEMA'] = hist['Close'].ewm(span=small_window).mean()
# hist['longEMA'] = hist['Close'].ewm(span=large_window).mean()
# hist['EMAdiff'] = hist['shortEMA'] - hist['longEMA']
# hist['EMAoverunder'] = ["over" if e > 0 else "under" for e in hist['EMAdiff']]
# hist['ema_ou_shift'] = hist['EMAoverunder'].shift(1)
# signals = []
# for i, b in enumerate(hist['EMAoverunder']):
#     if b == 'over' and hist['ema_ou_shift'].iloc[i] == 'under':
#         signals.append('buy')
#     elif b == 'under' and hist['ema_ou_shift'].iloc[i] == 'over':
#         signals.append('sell')
#     else:
#         signals.append('hold')
# hist['EMAsignal'] = signals
# to_drop = hist[hist['EMAsignal'] == 'hold'].index
# hist.drop(to_drop, inplace=True)
# hist['EMAdollardiff'] = hist['Close'] - hist['Close'].shift(1)
# hist = hist[hist['EMAsignal'] == 'sell']

# print(hist)
