"""
Parity check, extended: generates a fixture containing a deterministic
synthetic OHLCV series plus the Python-computed indicator values for it.
The JS side (parity_check.js) recomputes indicators from the *same* OHLCV
values using the ported JS indicator functions and diffs against these
expected outputs, element by element.

This is the piece that closes the drift risk on indicator computation
itself (RSI smoothing convention, EWM adjust=False behavior, rolling
window min_periods, normalization), not just on the Stage 1/5 scoring
math (which the original level/trajectory fixture already covered).

Run this whenever indicators/compute.py changes, then re-run the JS side.
"""

import json

import numpy as np
import pandas as pd

from stock_eval.indicators.compute import compute_all_indicators
from stock_eval.pipeline.stage1_threshold import LookupTable, interpolate_level_score
from stock_eval.pipeline.stage5_trajectory import trajectory_multiplier


def build_deterministic_ohlcv(n: int = 200, seed: int = 123) -> pd.DataFrame:
    """
    Fixed, reproducible OHLCV series -- deliberately NOT using
    SyntheticDataSource (which seeds per-ticker via hash) so this fixture
    is byte-identical every time it's regenerated, independent of any
    changes elsewhere in the data layer.
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start="2023-01-02", periods=n)

    log_returns = rng.normal(0.0003, 0.015, n)
    prices = 100.0 * np.exp(np.cumsum(log_returns))

    high = prices * (1 + rng.uniform(0, 0.01, n))
    low = prices * (1 - rng.uniform(0, 0.01, n))
    open_ = prices * (1 + rng.normal(0, 0.003, n))
    volume = rng.integers(100_000, 2_000_000, n)

    return pd.DataFrame({
        "date": dates,
        "open": open_,
        "high": high,
        "low": low,
        "close": prices,
        "volume": volume,
    })


def series_to_json_list(s: pd.Series) -> list:
    """NaN -> None so JSON round-trips cleanly and JS can distinguish
    'not yet available' from an actual number."""
    return [None if pd.isna(v) else float(v) for v in s]


def build_fixture() -> dict:
    ohlcv = build_deterministic_ohlcv()
    indicators_df = compute_all_indicators(ohlcv)

    indicator_names = [c for c in indicators_df.columns if c not in ("date", "close")]

    fixture = {
        "ohlcv": [
            {
                "date": str(row.date.date()),
                "open": float(row.open),
                "high": float(row.high),
                "low": float(row.low),
                "close": float(row.close),
                "volume": int(row.volume),
            }
            for row in ohlcv.itertuples()
        ],
        "expected_indicators": {
            name: series_to_json_list(indicators_df[name]) for name in indicator_names
        },
    }

    # --- Also (re)include the Stage 1/5 scoring-math cases from before, so
    # this single fixture file covers indicator computation AND scoring
    # parity in one place. ---
    midpoints = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90], dtype=float)
    values = np.array([0.04, 0.03, 0.015, 0.01, 0.0, -0.005, -0.01, -0.02, -0.03])
    table = LookupTable(
        indicator_name="test_indicator",
        bin_edges=np.array([]),
        bin_midpoints=midpoints,
        bin_values=values,
        bin_counts=np.full(len(midpoints), 100),
    )
    fixture["lookup_table"] = [[float(x), float(y)] for x, y in zip(midpoints, values)]

    fixture["level_cases"] = [
        {"value": v, "expected_level_score": interpolate_level_score(table, v)}
        for v in [5.0, 10.0, 25.0, 33.3, 50.0, 65.0, 90.0, 120.0, -10.0]
    ]

    fixture["trajectory_cases"] = [
        {"slope": s, "gradient": g, "expected_multiplier": trajectory_multiplier(s, g)}
        for s, g in [
            (0.5, -0.002), (-0.5, -0.002), (0.0, -0.002),
            (2.0, 0.001), (-2.0, 0.001), (0.1, 0.0),
        ]
    ]

    return fixture


if __name__ == "__main__":
    fixture = build_fixture()
    with open("parity_fixture.json", "w") as f:
        json.dump(fixture, f, indent=2)
    n_indicators = len(fixture["expected_indicators"])
    n_rows = len(fixture["ohlcv"])
    print(f"Wrote parity_fixture.json: {n_rows} OHLCV rows, {n_indicators} indicators, "
          f"{len(fixture['level_cases'])} level cases, {len(fixture['trajectory_cases'])} trajectory cases.")
