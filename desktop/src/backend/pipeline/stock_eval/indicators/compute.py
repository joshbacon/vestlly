"""
Indicator computation.

Each function takes a daily OHLCV DataFrame and returns a pandas Series
aligned to the same index. Scale-dependent indicators are normalized here
(as % of price, or similar) so that pooling across stocks of different
price levels in Stage 1 produces a meaningful lookup table -- this is the
fix for the cross-sectional comparability issue flagged during design.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from stock_eval.config import INDICATOR_SPECS, ScaleType


def rsi_14(df: pd.DataFrame) -> pd.Series:
    close = df["close"]
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.rename("rsi_14")


def stoch_k_14(df: pd.DataFrame) -> pd.Series:
    low_min = df["low"].rolling(14).min()
    high_max = df["high"].rolling(14).max()
    denom = (high_max - low_min).replace(0, np.nan)
    k = 100 * (df["close"] - low_min) / denom
    return k.rename("stoch_k_14")


def bb_percent_b_20(df: pd.DataFrame) -> pd.Series:
    close = df["close"]
    sma = close.rolling(20).mean()
    std = close.rolling(20).std()
    upper = sma + 2 * std
    lower = sma - 2 * std
    denom = (upper - lower).replace(0, np.nan)
    pct_b = (close - lower) / denom
    return pct_b.rename("bb_percent_b_20")


def macd_hist_norm(df: pd.DataFrame) -> pd.Series:
    close = df["close"]
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal = macd_line.ewm(span=9, adjust=False).mean()
    hist = macd_line - signal
    # Scale-dependent -> normalize by price (per config classification)
    # before this indicator is pooled across stocks.
    normalized = hist / close
    return normalized.rename("macd_hist_norm")


def sma_dist_50(df: pd.DataFrame) -> pd.Series:
    close = df["close"]
    sma = close.rolling(50).mean()
    # Scale-dependent -> normalize as % distance from price, not raw
    # price-unit distance, before pooling.
    dist_pct = (close - sma) / sma
    return dist_pct.rename("sma_dist_50")


_REGISTRY = {
    "rsi_14": rsi_14,
    "stoch_k_14": stoch_k_14,
    "bb_percent_b_20": bb_percent_b_20,
    "macd_hist_norm": macd_hist_norm,
    "sma_dist_50": sma_dist_50,
}


def compute_indicator(name: str, df: pd.DataFrame) -> pd.Series:
    if name not in _REGISTRY:
        raise KeyError(
            f"No indicator function registered for '{name}'. "
            f"Known indicators: {list(_REGISTRY)}"
        )
    return _REGISTRY[name](df)


def compute_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Compute every indicator declared in config.INDICATOR_SPECS, aligned
    into a single DataFrame indexed the same way as `df`."""
    out = pd.DataFrame(index=df.index)
    out["date"] = df["date"]
    out["close"] = df["close"]
    for spec in INDICATOR_SPECS:
        out[spec.name] = compute_indicator(spec.name, df)
    return out


def forward_return(df: pd.DataFrame, horizon_days: int) -> pd.Series:
    """Forward return over `horizon_days` trading days, aligned so that
    row t holds the return from t to t+horizon. Rows without enough future
    data get NaN and should be dropped before fitting."""
    close = df["close"]
    fwd = close.shift(-horizon_days) / close - 1
    return fwd.rename(f"fwd_return_{horizon_days}d")


def assert_normalization_is_scale_appropriate() -> None:
    """
    Lightweight self-check: confirms every SCALE_DEPENDENT indicator's
    computation function actually divides by a price-like quantity, so a
    forgotten normalization doesn't silently reach Stage 1. This is a
    naming/heuristic check, not a proof -- treat it as a guardrail, not a
    guarantee.
    """
    scale_dependent_names = {
        s.name for s in INDICATOR_SPECS if s.scale_type == ScaleType.SCALE_DEPENDENT
    }
    import inspect

    for name in scale_dependent_names:
        src = inspect.getsource(_REGISTRY[name])
        if "/ close" not in src and "/ sma" not in src and "/close" not in src:
            raise AssertionError(
                f"Indicator '{name}' is marked SCALE_DEPENDENT in config "
                f"but its implementation doesn't appear to normalize by "
                f"price. Check compute.py."
            )
