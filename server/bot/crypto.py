# This file contains functions to evaluate mean reversion and MA crossover

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def _rolling_mean(arr: np.ndarray, w: int) -> np.ndarray:
    n = len(arr)
    cumsum = np.cumsum(np.insert(arr, 0, 0.0))
    out = np.full(n, np.nan)
    out[w - 1:] = (cumsum[w:] - cumsum[:-w]) / w
    return out


def _rolling_std(arr: np.ndarray, w: int) -> np.ndarray:
    n = len(arr)
    cumsum2 = np.cumsum(np.insert(arr ** 2, 0, 0.0))
    rm2 = np.full(n, np.nan)
    rm2[w - 1:] = (cumsum2[w:] - cumsum2[:-w]) / w
    rm = _rolling_mean(arr, w)
    return np.sqrt(np.maximum(rm2 - rm ** 2, 0.0))

def plot_signals(df: pd.DataFrame,
                 date_col: str = "Date",
                 price_col: str = "Close",
                 signal_col: str = "signal") -> None:
    """
    Plot closing price over time with BUY / SELL markers.
 
    Parameters
    ----------
    df         : DataFrame containing date, price, and signal columns.
    date_col   : Name of the date column.
    price_col  : Name of the closing-price column.
    signal_col : Name of the signal column ('BUY' | 'SELL' | 'HOLD').
    """
    df = df.copy()#[::-1]
    # print(df)
    df[date_col] = pd.to_datetime(df[date_col])
 
    buys  = df[df[signal_col].str.contains("BUY", na=False)]
    sells = df[df[signal_col].str.contains("SELL", na=False)]
 
    fig, ax = plt.subplots(figsize=(14, 6))
 
    # Price line
    ax.plot(df[date_col], df[price_col],
            color="#4C72B0", linewidth=1.8, label="Close Price", zorder=2)
 
    # BUY markers (green triangles pointing up)
    ax.scatter(buys[date_col], buys[price_col],
               marker="^", color="#2ca02c", s=120, zorder=4,
               label=buys[signal_col], edgecolors="white", linewidths=0.6)
 
    # SELL markers (red triangles pointing down)
    ax.scatter(sells[date_col], sells[price_col],
               marker="v", color="#d62728", s=120, zorder=4,
               label=sells[signal_col], edgecolors="white", linewidths=0.6)
 
    # Annotate each BUY point
    for _, row in buys.iterrows():
        ax.annotate(row[signal_col],
                    xy=(row[date_col], row[price_col]),
                    xytext=(0, 12), textcoords="offset points",
                    ha="center", va="bottom",
                    fontsize=8, fontweight="bold", color="#2ca02c")
 
    # Annotate each SELL point
    for _, row in sells.iterrows():
        ax.annotate(row[signal_col],
                    xy=(row[date_col], row[price_col]),
                    xytext=(0, -14), textcoords="offset points",
                    ha="center", va="top",
                    fontsize=8, fontweight="bold", color="#d62728")
 
    # Formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    fig.autofmt_xdate(rotation=45)
 
    ax.set_title("Closing Price with BUY / SELL Signals", fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Price", fontsize=11)
    ax.legend(fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.4)
 
    plt.tight_layout()
 
 
def evaluate_mean_reversion(
    df: pd.DataFrame,
    lookback: int,
    entry_zscore: float,
    exit_zscore: float,
) -> dict:
    ### The graph for this one is looks like we should do this;
    ## each buy signal, allocates 10% of the budget for this coin
    ## each sell signal only sells one 'share' (10% of budget chunk)
    ### would this result in having leftover crypto each sale? (taking out 10% of original budget will be less than the (hopefully) higher sale price of the coin)
    close = df["Close"].to_numpy(dtype=np.float64)
    # print(df)
    rm    = _rolling_mean(close, lookback)
    rstd  = _rolling_std(close, lookback)

    with np.errstate(invalid="ignore", divide="ignore"):
        zscore = np.where(rstd > 0, (close - rm) / rstd, np.nan)
    zscore[:lookback] = np.nan

    signals = []
    for z in zscore:
        result = {
            "action": "HOLD",
            "score": 1 - abs(z / entry_zscore),
        }
        if z < -entry_zscore:
            result = {
                "action": "BUY",
                "score": abs(z / entry_zscore),
            }
        elif z > -exit_zscore:
            result = {
                "action": "SELL",
                "score": abs(z / exit_zscore),
            }
        signals.append(f"{result['action']} ({result['score']:1.2f})")
    df['signal'] = signals
    print(df)
    plot_signals(df)
    return result


def evaluate_sma_crossover(
    df: pd.DataFrame,
    small_window: int,
    large_window: int,
) -> dict:
    close = df["Close"].to_numpy(dtype=np.float64)

    short_sma  = _rolling_mean(close, small_window)
    long_sma   = _rolling_mean(close, large_window)

    is_above = short_sma[0] > long_sma[0]

    shifted = np.roll(close, 1)
    prev_short_sma = _rolling_mean(shifted, small_window)
    prev_long_sma = _rolling_mean(shifted, large_window)
    
    was_above = prev_short_sma[0] > prev_long_sma[0]

    result = {
        "action": "HOLD",
        "score": 0.0,
    }
    if is_above and not was_above:
        result = {
            "action": "BUY",
            "score": 1.0,
        }
    elif was_above and not is_above:
        result = {
            "action": "SELL",
            "score": -1.0,
        }
    return result


# def evaluate_coin(ge: dict, df: pd.DataFrame):
    """
    TODO: Read in the genome from the database
        - also need to fill in the table for each stock
    ge = {
        # Mean Reversion parameters
        lookback: 9,
        entry_zscore: 0.70,
        exit_zscore: 0.40,
        # Moving Average Crossover parameters
        small_window: 31,
        large_window: 36,
    }
    """
data = pd.read_csv("bitcoin.csv")[5281:5646]
print(f"Mean Reversion: {evaluate_mean_reversion(data, 15, 0.7, 0.4)}")
# print(f"MA Crossover: {evaluate_sma_crossover(data, 31, 36)}")
plt.show()
