"""
Stage 1: threshold fitting via binned lookup table.

For each indicator: bin historical values into ~LOOKUP_TABLE_BINS buckets,
compute the mean forward return per bucket on the fit set, smooth lightly,
and store as a lookup table. Bins with too few samples are pulled toward
their smoothed neighbors rather than trusted outright (MIN_SAMPLES_PER_BIN).

This directly implements the "lookup table over parametric function"
decision: no functional-form assumption, captures whatever the empirical
indicator-vs-forward-return relationship actually looks like.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from stock_eval.config import LOOKUP_TABLE_BINS, LOOKUP_TABLE_SMOOTHING_WINDOW, MIN_SAMPLES_PER_BIN


@dataclass(frozen=True)
class LookupTable:
    """A fitted Stage 1 curve: bin midpoints -> mean forward return."""
    indicator_name: str
    bin_edges: np.ndarray       # length = LOOKUP_TABLE_BINS + 1
    bin_midpoints: np.ndarray   # length = LOOKUP_TABLE_BINS
    bin_values: np.ndarray      # smoothed mean forward return per bin
    bin_counts: np.ndarray      # raw sample count per bin (for diagnostics)

    def to_points(self) -> list[list[float]]:
        """Serialize as [[x, y], ...] for the JSON artifact."""
        return [[float(x), float(y)] for x, y in zip(self.bin_midpoints, self.bin_values)]


def fit_lookup_table(
    indicator_values: pd.Series,
    forward_returns: pd.Series,
    indicator_name: str,
    n_bins: int = LOOKUP_TABLE_BINS,
) -> LookupTable:
    """
    Fit a Stage 1 lookup table from paired (indicator_value, forward_return)
    observations, already restricted to the fit set and already
    non-overlapping-sampled (see pipeline.splits).
    """
    mask = indicator_values.notna() & forward_returns.notna()
    x = indicator_values[mask].to_numpy()
    y = forward_returns[mask].to_numpy()

    if len(x) < n_bins * MIN_SAMPLES_PER_BIN:
        raise ValueError(
            f"Not enough clean observations ({len(x)}) to reliably fit "
            f"{n_bins} bins at >= {MIN_SAMPLES_PER_BIN} samples/bin for "
            f"indicator '{indicator_name}'. Reduce n_bins, gather more "
            f"history, or pool more tickers."
        )

    bin_edges = np.quantile(x, np.linspace(0, 1, n_bins + 1))
    # Guard against degenerate (duplicate) edges from heavily-clustered data.
    bin_edges = np.unique(bin_edges)
    actual_bins = len(bin_edges) - 1

    bin_indices = np.digitize(x, bin_edges[1:-1], right=False)

    raw_means = np.full(actual_bins, np.nan)
    counts = np.zeros(actual_bins, dtype=int)
    midpoints = np.zeros(actual_bins)

    for b in range(actual_bins):
        in_bin = bin_indices == b
        counts[b] = in_bin.sum()
        if counts[b] > 0:
            raw_means[b] = y[in_bin].mean()
        midpoints[b] = 0.5 * (bin_edges[b] + bin_edges[b + 1])

    smoothed = _smooth_with_sparse_bin_handling(raw_means, counts)

    return LookupTable(
        indicator_name=indicator_name,
        bin_edges=bin_edges,
        bin_midpoints=midpoints,
        bin_values=smoothed,
        bin_counts=counts,
    )


def _smooth_with_sparse_bin_handling(
    raw_means: np.ndarray,
    counts: np.ndarray,
    window: int = LOOKUP_TABLE_SMOOTHING_WINDOW,
    min_samples: int = MIN_SAMPLES_PER_BIN,
) -> np.ndarray:
    """
    Rolling-average smoothing, with sparse bins (count < min_samples)
    weighted down in favor of their neighbors so a handful of rare extreme
    readings don't produce a wild, untrustworthy point in the table.
    """
    n = len(raw_means)
    # Fill any fully-empty bins with a linear interpolation first so the
    # rolling window has something to average over.
    filled = pd.Series(raw_means).interpolate(limit_direction="both").to_numpy()

    weights = np.clip(counts / min_samples, 0.1, 1.0)

    smoothed = np.zeros(n)
    half = window // 2
    for i in range(n):
        lo, hi = max(0, i - half), min(n, i + half + 1)
        local_vals = filled[lo:hi]
        local_weights = weights[lo:hi]
        smoothed[i] = np.average(local_vals, weights=local_weights)

    return smoothed


def interpolate_level_score(table: LookupTable, value: float, score_range: tuple[float, float] = (-1.0, 1.0)) -> float:
    """
    Runtime-equivalent evaluation used during Python-side validation
    (Stage 5/7): linear interpolation on the lookup table, clamped at the
    edges, then calibrated onto score_range.

    NOTE: the JS runtime implementation must match this logic exactly
    (interpolation + clamping + calibration) -- see the cross-check
    guidance in the README about Python/JS formula drift.
    """
    x = table.bin_midpoints
    y_raw = table.bin_values

    if value <= x[0]:
        raw = y_raw[0]
    elif value >= x[-1]:
        raw = y_raw[-1]
    else:
        raw = float(np.interp(value, x, y_raw))

    return _calibrate_to_range(raw, y_raw, score_range)


def _calibrate_to_range(raw_value: float, all_raw_values: np.ndarray, score_range: tuple[float, float]) -> float:
    """Min-max calibration of a raw forward-return value onto score_range,
    based on the observed range of the fitted table itself."""
    lo, hi = float(all_raw_values.min()), float(all_raw_values.max())
    if hi - lo < 1e-12:
        return 0.0
    normalized = (raw_value - lo) / (hi - lo)  # 0..1
    out_lo, out_hi = score_range
    return out_lo + normalized * (out_hi - out_lo)
