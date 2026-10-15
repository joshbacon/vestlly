"""
Stage 5: trajectory window (N) selection and validation.

For each indicator, test candidate slope windows on the N-search slice,
pick the best performer, then confirm the improvement holds on the
N-confirm slice before accepting it. This treats N-selection as its own
nested optimization with its own out-of-sample check, rather than a
single-pass test against the whole fit set -- otherwise "optimal N" is
just as exposed to overfitting as the Stage 1 thresholds it's meant to
complement.

The trajectory multiplier is built so it never flips the sign carried by
the level score (see design discussion): it's a positive multiplier,
>1 when the indicator is moving toward its fitted ideal, <1 when moving
away, derived from the slope's alignment with the direction implied by
the fitted curve rather than from the slope's raw sign.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

from stock_eval.config import CANDIDATE_N_WINDOWS, DEFAULT_FALLBACK_N
from stock_eval.pipeline.stage1_threshold import LookupTable, interpolate_level_score


@dataclass(frozen=True)
class TrajectoryFitResult:
    indicator_name: str
    chosen_n: int
    validated: bool  # False -> fell back to DEFAULT_FALLBACK_N
    search_correlation: float
    confirm_correlation: float
    level_only_correlation: float  # baseline to compare against


def compute_slope(series: pd.Series, n: int) -> pd.Series:
    """Simple slope over the last n periods: (value_t - value_{t-n}) / n."""
    return (series - series.shift(n)) / n


def trajectory_multiplier(
    slope: float,
    curve_local_gradient: float,
    sensitivity: float = 4.0,
    bounds: tuple[float, float] = (0.5, 1.5),
) -> float:
    """
    Convert a raw slope into a positive multiplier on the level score.

    `curve_local_gradient` is the sign of the fitted Stage 1 curve's slope
    at the current indicator value (i.e. "does higher-indicator mean
    higher or lower forward return here?"). Multiplying the raw slope by
    this tells us whether the indicator's recent movement is heading
    toward higher-scoring territory on the curve ("toward ideal") or away
    from it -- independent of the level score's own sign, so this can
    never flip it.
    """
    alignment = slope * curve_local_gradient  # >0 => moving toward ideal
    raw_multiplier = 1.0 + np.tanh(alignment * sensitivity) * 0.5
    return float(np.clip(raw_multiplier, bounds[0], bounds[1]))


def _score_n_candidate(
    df: pd.DataFrame,
    indicator_col: str,
    forward_return_col: str,
    table: LookupTable,
    n: int,
) -> float:
    """
    Correlation between (level_score * trajectory_multiplier) and forward
    returns for one candidate N -- the metric used to pick the best N and
    to confirm it generalizes.
    """
    slopes = compute_slope(df[indicator_col], n)

    # Local gradient of the fitted curve at each observation's indicator
    # value, via finite difference on the lookup table.
    grad_lookup = np.gradient(table.bin_values, table.bin_midpoints)

    level_scores = df[indicator_col].apply(lambda v: interpolate_level_score(table, v))
    local_grad = df[indicator_col].apply(
        lambda v: float(np.interp(v, table.bin_midpoints, grad_lookup))
    )

    multipliers = pd.Series(
        [
            trajectory_multiplier(s, g) if pd.notna(s) else np.nan
            for s, g in zip(slopes, local_grad)
        ],
        index=df.index,
    )

    combined = (level_scores * multipliers).clip(-1, 1)

    valid = combined.notna() & df[forward_return_col].notna()
    if valid.sum() < 30:
        return 0.0
    corr, _ = pearsonr(combined[valid], df[forward_return_col][valid])
    return float(corr) if np.isfinite(corr) else 0.0


def select_and_validate_n(
    n_search_df: pd.DataFrame,
    n_confirm_df: pd.DataFrame,
    indicator_col: str,
    forward_return_col: str,
    table: LookupTable,
    candidates: list[int] = CANDIDATE_N_WINDOWS,
) -> TrajectoryFitResult:
    """
    Search candidate N values on n_search_df, pick the best, confirm the
    improvement over level-only holds on n_confirm_df. Falls back to
    DEFAULT_FALLBACK_N if the improvement doesn't generalize.
    """
    # Baseline: level-only correlation (no trajectory) on the confirm slice.
    level_only_scores = n_confirm_df[indicator_col].apply(
        lambda v: interpolate_level_score(table, v)
    )
    valid_baseline = level_only_scores.notna() & n_confirm_df[forward_return_col].notna()
    if valid_baseline.sum() < 30:
        level_only_corr = 0.0
    else:
        level_only_corr, _ = pearsonr(
            level_only_scores[valid_baseline], n_confirm_df[forward_return_col][valid_baseline]
        )

    search_scores = {
        n: _score_n_candidate(n_search_df, indicator_col, forward_return_col, table, n)
        for n in candidates
    }
    best_n = max(search_scores, key=search_scores.get)
    best_search_corr = search_scores[best_n]

    confirm_corr = _score_n_candidate(
        n_confirm_df, indicator_col, forward_return_col, table, best_n
    )

    improves_on_confirm = confirm_corr > abs(level_only_corr) + 1e-3

    if improves_on_confirm:
        return TrajectoryFitResult(
            indicator_name=indicator_col,
            chosen_n=best_n,
            validated=True,
            search_correlation=best_search_corr,
            confirm_correlation=confirm_corr,
            level_only_correlation=float(level_only_corr),
        )

    return TrajectoryFitResult(
        indicator_name=indicator_col,
        chosen_n=DEFAULT_FALLBACK_N,
        validated=False,
        search_correlation=best_search_corr,
        confirm_correlation=confirm_corr,
        level_only_correlation=float(level_only_corr),
    )
