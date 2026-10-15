"""
    This file holds functions necessary for evaluating a stock against the trained model
"""

import pandas as pd
import numpy as np

## Helper functions for mean reversion and moving average crossover

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


def evaluate_mean_reversion(
    df: pd.DataFrame,
    lookback: int,
    entry_zscore: float,
    exit_zscore: float,
) -> dict:
    close = df["Close"].to_numpy(dtype=np.float64)
    rm    = _rolling_mean(close, lookback)
    rstd  = _rolling_std(close, lookback)

    with np.errstate(invalid="ignore", divide="ignore"):
        zscore = np.where(rstd > 0, (close - rm) / rstd, np.nan)
    zscore[:lookback] = np.nan

    result = {
        "action": "HOLD",
        "score": zscore[-1],
    }
    if zscore[-1] < -entry_zscore:
        result = {
            "action": "BUY",
            "score": abs(zscore[-1] / entry_zscore),
        }
    elif zscore[-1] > -exit_zscore:
        result = {
            "action": "SELL",
            "score": abs(zscore[-1] / exit_zscore) *-1,
        }
    return result


def evaluate_sma_crossover(
    df: pd.DataFrame,
    short_window: int,
    long_window: int,
) -> dict:
    close = df["Close"].to_numpy(dtype=np.float64)

    short_sma  = _rolling_mean(close, short_window)
    long_sma   = _rolling_mean(close, long_window)

    above = short_sma[0] > long_sma[0]

    shifted = np.roll(close, 1)
    prev_short_sma = _rolling_mean(shifted, short_window)
    prev_long_sma = _rolling_mean(shifted, long_window)
    
    prev_above = prev_short_sma[0] > prev_long_sma[0]

    result = {
        "action": "HOLD",
        "score": 0.0,
    }
    if above and not prev_above:
        result = {
            "action": "BUY",
            "score": 1.0,
        }
    elif prev_above and not above:
        result = {
            "action": "SELL",
            "score": -1.0,
        }
    return result



def evaluate_symbol(df: pd.DataFrame, ge: dict):
    mean_reversion = evaluate_mean_reversion(df, ge['lookback'], ge['entry_zscore'], ge['exit_zscore'])
    sma_crossover = evaluate_sma_crossover(df, ge['short_window'], ge['long_window'])

