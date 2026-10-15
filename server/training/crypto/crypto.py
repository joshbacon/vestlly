import pandas as pd


# crypto trading botttttttt

btc_hist = pd.read_csv("data/bitcoin.csv")
eth_hist = pd.read_csv("data/ethereum.csv")


# write an evaluation function for mean reversion (GA???)
# look at short, medium, and long range; correlate with weights
small_window = 50
large_window = 200


# print(btc_hist)

# write an evaluation function for moving average cross-over
# try some different spread combos (GA probablement)
# when the short MA crosses above the slower MA, it's bullish
# when the short MA crosses below the slower MA, it's bearish

#  Try both of these just to see:
# SMA (Simple Moving Average) using a 5 day rolling window to average recent prices.
btc_hist['shortMA'] = btc_hist['Close'].rolling(window=small_window).mean()
btc_hist['longMA'] = btc_hist['Close'].rolling(window=large_window).mean()
btc_hist['MAdiff'] = btc_hist['shortMA'] - btc_hist['longMA']
btc_hist['overunder'] = ["over" if b > 0 else "under" for b in btc_hist['MAdiff']]
btc_hist['ou_shift'] = btc_hist['overunder'].shift(1)
signals = []
for i, b in enumerate(btc_hist['overunder']):
    if b == 'over' and btc_hist['ou_shift'].iloc[i] == 'under':
        signals.append('buy')
    elif b == 'under' and btc_hist['ou_shift'].iloc[i] == 'over':
        signals.append('sell')
    else:
        signals.append('hold')
btc_hist['signal'] = signals
to_drop = btc_hist[btc_hist['signal'] == 'hold'].index
btc_hist.drop(to_drop, inplace=True)
btc_hist['dollardiff'] = btc_hist['Close'] - btc_hist['Close'].shift(1)
btc_hist = btc_hist[btc_hist['signal'] == 'sell']
# EMA (Exponential Moving Average) which gives more weight to recent values and reacts faster to changes.
eth_hist['shortMA'] = eth_hist['Close'].ewm(span=small_window).mean()
eth_hist['longMA'] = eth_hist['Close'].ewm(span=large_window).mean()
eth_hist['MAdiff'] = eth_hist['shortMA'] - eth_hist['longMA']
eth_hist['overunder'] = ["over" if e > 0 else "under" for e in eth_hist['MAdiff']]
eth_hist['ou_shift'] = eth_hist['overunder'].shift(1)
signals = []
for i, b in enumerate(eth_hist['overunder']):
    if b == 'over' and eth_hist['ou_shift'].iloc[i] == 'under':
        signals.append('buy')
    elif b == 'under' and eth_hist['ou_shift'].iloc[i] == 'over':
        signals.append('sell')
    else:
        signals.append('hold')
eth_hist['signal'] = signals
to_drop = eth_hist[eth_hist['signal'] == 'hold'].index
eth_hist.drop(to_drop, inplace=True)
eth_hist['dollardiff'] = eth_hist['Close'] - eth_hist['Close'].shift(1)
eth_hist = eth_hist[eth_hist['signal'] == 'sell']

print(btc_hist)
print(eth_hist)

# [... find some more strategies to implement]

# backtest the strategies to fine-tune

# implement functions to submit a trade to the crypto account through snaptrade


# live crypto data from here: https://coinmarketcap.com/api/pricing/
# 15K call credits/month, can make a call like every 5 minutes so we gucci

