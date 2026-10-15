"""
Data source abstraction.

The rest of the pipeline only depends on the `DataSource` interface, not on
any particular vendor. This is what lets you develop and test the entire
fitting pipeline today with `SyntheticDataSource`, and later swap in
`EODHDDataSource` (or any other vendor) without touching Stage 1/5/6/7 code.
"""

from __future__ import annotations

import abc
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class OHLCV:
    """Container for a single ticker's daily OHLCV history."""
    ticker: str
    frame: pd.DataFrame  # columns: date, open, high, low, close, volume


class DataSource(abc.ABC):
    """Abstract interface every data provider implementation must satisfy."""

    @abc.abstractmethod
    def get_sector_universe(self, sector: str, market: str) -> list[str]:
        """
        Return tickers belonging to `sector` in `market` ("US" or "CA").

        Implementations for markets without point-in-time membership
        (currently CA) should return *current* constituents and rely on
        the caller to tag the resulting fit with the appropriate
        UniverseConfig (see config.py) so the limitation is visible
        downstream, not silently absorbed here.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_daily_ohlcv(self, ticker: str, start: str, end: str) -> OHLCV:
        """Return daily OHLCV history for `ticker` between start/end dates
        (YYYY-MM-DD, inclusive)."""
        raise NotImplementedError


class EODHDDataSource(DataSource):
    """
    EODHD-backed implementation. Requires EODHD_API_KEY in the environment.

    NOTE: this is a thin, intentionally minimal implementation to establish
    the integration surface. Point-in-time constituent reconstruction for
    the S&P family (per the design discussion) is not yet implemented here
    -- `get_sector_universe` currently returns current constituents for any
    market, and callers are responsible for tagging the resulting fit with
    UniverseConfig.survivorship_bias_free = False until that's built out.
    """

    BASE_URL = "https://eodhd.com/api"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("EODHD_API_KEY")
        if not self.api_key:
            raise ValueError(
                "EODHD_API_KEY not set. Pass api_key= explicitly or set "
                "the environment variable."
            )

    def get_sector_universe(self, sector: str, market: str) -> list[str]:
        import requests  # local import: optional dependency, only needed here

        if market == "US":
            # Placeholder: current constituents of GSPC.INDX, filtered by
            # sector. Point-in-time historical=1 snapshots (per design
            # discussion) should be wired in here before this is used for
            # a real fit that needs survivorship-bias-free history.
            url = f"{self.BASE_URL}/fundamentals/GSPC.INDX"
            params = {"api_token": self.api_key, "fmt": "json"}
        elif market == "CA":
            # Current constituents only -- known, accepted limitation.
            url = f"{self.BASE_URL}/exchange-symbol-list/TO"
            params = {"api_token": self.api_key, "fmt": "json"}
        else:
            raise ValueError(f"Unsupported market: {market}")

        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # Real implementation would parse `data` into a ticker list
        # filtered by `sector`; left as a TODO since it depends on the
        # exact response shape EODHD returns for your subscription tier.
        raise NotImplementedError(
            "Parse EODHD response into a sector-filtered ticker list here."
        )

    def get_daily_ohlcv(self, ticker: str, start: str, end: str) -> OHLCV:
        import requests

        url = f"{self.BASE_URL}/eod/{ticker}"
        params = {
            "api_token": self.api_key,
            "fmt": "json",
            "from": start,
            "to": end,
            "period": "d",
        }
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        rows = resp.json()
        frame = pd.DataFrame(rows)
        frame["date"] = pd.to_datetime(frame["date"])
        frame = frame.rename(columns={"adjusted_close": "close"})
        frame = frame[["date", "open", "high", "low", "close", "volume"]]
        return OHLCV(ticker=ticker, frame=frame.sort_values("date").reset_index(drop=True))


class SyntheticDataSource(DataSource):
    """
    Generates plausible synthetic OHLCV data with a mild, known
    mean-reverting relationship baked in, so the fitting pipeline has
    *something* real to find and you can sanity-check that Stage 1
    actually recovers a sensible-looking curve.

    Not intended to represent real market dynamics -- purely for
    exercising the pipeline end-to-end during development.
    """

    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)

    def get_sector_universe(self, sector: str, market: str) -> list[str]:
        n = 30 if market == "US" else 15
        prefix = "US" if market == "US" else "CA"
        return [f"{prefix}_{sector}_{i:03d}" for i in range(n)]

    def get_daily_ohlcv(self, ticker: str, start: str, end: str) -> OHLCV:
        dates = pd.bdate_range(start=start, end=end)
        n = len(dates)

        # Deterministic per-ticker seed so re-fetching the same ticker is
        # stable within a run, but differs across tickers.
        ticker_seed = abs(hash(ticker)) % (2**32)
        rng = np.random.default_rng(ticker_seed)

        # Simulate a random walk in log-price with a mild mean-reverting
        # nudge: when a synthetic "RSI-like" oscillator (derived from
        # recent returns) is extreme, nudge future drift back toward the
        # mean. This bakes in a *recoverable* signal for Stage 1 to find,
        # without hardcoding the exact shape of the curve it should fit.
        drift = rng.normal(0.0003, 0.0001)
        vol = rng.uniform(0.01, 0.03)
        log_returns = rng.normal(drift, vol, n)

        window = 14
        for t in range(window, n):
            recent = log_returns[t - window:t]
            gains = recent[recent > 0].sum()
            losses = -recent[recent < 0].sum()
            rs = gains / losses if losses > 1e-9 else 10.0
            rsi_like = 100 - 100 / (1 + rs)
            # Mean-reversion nudge: push drift opposite to extremes.
            if rsi_like > 70:
                log_returns[t] -= 0.004
            elif rsi_like < 30:
                log_returns[t] += 0.004

        start_price = rng.uniform(10, 300)
        prices = start_price * np.exp(np.cumsum(log_returns))

        high = prices * (1 + rng.uniform(0, 0.01, n))
        low = prices * (1 - rng.uniform(0, 0.01, n))
        open_ = prices * (1 + rng.normal(0, 0.003, n))
        volume = rng.integers(1_000_00, 5_000_000, n)

        frame = pd.DataFrame({
            "date": dates,
            "open": open_,
            "high": high,
            "low": low,
            "close": prices,
            "volume": volume,
        })
        return OHLCV(ticker=ticker, frame=frame)
