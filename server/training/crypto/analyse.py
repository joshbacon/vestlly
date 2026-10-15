import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

small_window = 31
large_window = 36
df = pd.read_csv("data/bitcoin.csv")

close = df["Close"].to_numpy(dtype=np.float64)
n = len(close)

# Vectorised SMAs using cumsum for O(n) computation
def rolling_mean(arr: np.ndarray, w: int) -> np.ndarray:
    cumsum = np.cumsum(np.insert(arr, 0, 0.0))
    out = np.full(n, np.nan)
    out[w - 1:] = (cumsum[w:] - cumsum[:-w]) / w
    return out

short_sma = rolling_mean(close, small_window)
long_sma  = rolling_mean(close, large_window)
diff      = short_sma - long_sma

# Crossover detection: +1 = crossed above (buy), -1 = crossed below (sell)
above      = (diff > 0).astype(np.int8)
above_prev = np.roll(above, 1)
above_prev[0] = above[0]          # no signal on first bar

buy_mask  = (above == 1) & (above_prev == 0)
sell_mask = (above == 0) & (above_prev == 1)

# Discard bars before both SMAs are valid
valid_from = large_window - 1
buy_mask[:valid_from]  = False
sell_mask[:valid_from] = False

buy_indices  = np.where(buy_mask)[0]
sell_indices = np.where(sell_mask)[0]

if len(buy_indices) == 0 or len(sell_indices) == 0:
    print("no buys OR no sells")
    exit()

# Match each buy to the next sell that follows it
total      = 0.0
in_position = False
entry_price = 0.0

motion = []

bi, si = 0, 0
while bi < len(buy_indices) and si < len(sell_indices):
    if not in_position:
        entry_price = close[buy_indices[bi]]
        motion.append({
            'Date': df['Date'][buy_indices[bi]],
            'Close': close[buy_indices[bi]]
        })
        in_position = True
        bi += 1
    else:
        # Advance sell pointer until it's after the entry bar
        entry_bar = buy_indices[bi - 1]
        while si < len(sell_indices) and sell_indices[si] <= entry_bar:
            si += 1
        if si >= len(sell_indices):
            break
        total      += close[sell_indices[si]] - entry_price
        motion.append({
            'Date': df['Date'][sell_indices[si]],
            'Close': close[sell_indices[si]]
        })
        in_position = False
        si += 1

print(total)

graph = pd.DataFrame(motion)
print(graph['Date'])


# fig, ax = plt.subplots()
# graph = pd.DataFrame(motion)
# ax.plot(graph['Date'], graph['Close'])
# plt.show()

