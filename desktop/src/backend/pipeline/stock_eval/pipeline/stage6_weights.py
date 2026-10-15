"""
Stage 6: composite weight fitting.

Computes per-indicator scores (level x trajectory, from Stages 1-4) on the
weight-fit set only -- never the fit set the thresholds/N were chosen on --
and fits a regularized, non-negative-constrained regression against
forward returns to get the composite weights. Ridge regularization plus a
non-negativity constraint guards against unstable/sign-flipped weights
from correlated indicators (flagged during design).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import nnls
from sklearn.linear_model import Ridge

from stock_eval.pipeline.stage1_threshold import LookupTable, interpolate_level_score
from stock_eval.pipeline.stage5_trajectory import (
    TrajectoryFitResult,
    compute_slope,
    trajectory_multiplier,
)


@dataclass(frozen=True)
class CompositeWeights:
    indicator_names: list[str]
    weights: dict[str, float]
    ridge_alpha: float
    r_squared: float  # on the weight-fit set itself -- see caveat in fit_weights


def compute_indicator_score_series(
    df: pd.DataFrame,
    indicator_col: str,
    table: LookupTable,
    chosen_n: int,
) -> pd.Series:
    """
    Stage 2-4 applied to a whole DataFrame: level_score * trajectory_multiplier,
    clipped to [-1, 1]. This is the Python-side equivalent of the runtime
    scoring the JS side will perform -- kept here so Stage 6 fits weights
    against the same quantity that will be computed live.
    """
    grad_lookup = np.gradient(table.bin_values, table.bin_midpoints)
    slopes = compute_slope(df[indicator_col], chosen_n)

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

    return (level_scores * multipliers).clip(-1, 1).rename(f"{indicator_col}_score")


def fit_weights(
    weight_fit_df: pd.DataFrame,
    tables: dict[str, LookupTable],
    trajectory_results: dict[str, TrajectoryFitResult],
    forward_return_col: str,
    ridge_alpha: float = 1.0,
    non_negative: bool = True,
) -> CompositeWeights:
    """
    Fit composite weights on the weight-fit set.

    IMPORTANT CAVEAT: the r_squared returned here is in-sample on the
    weight-fit set (the set the weights were literally fit on) -- it is
    NOT a substitute for Stage 7's held-out test-set evaluation. Treat it
    as a fitting diagnostic only.
    """
    indicator_names = list(tables.keys())
    score_cols = {}
    for name in indicator_names:
        score_cols[name] = compute_indicator_score_series(
            weight_fit_df, name, tables[name], trajectory_results[name].chosen_n
        )

    scores_df = pd.DataFrame(score_cols)
    y = weight_fit_df[forward_return_col]

    valid = scores_df.notna().all(axis=1) & y.notna()
    X = scores_df[valid].to_numpy()
    y_valid = y[valid].to_numpy()

    if len(y_valid) < 30:
        raise ValueError(
            "Not enough overlapping, non-NaN observations to fit Stage 6 "
            "weights reliably. Check indicator NaN rates and weight-fit "
            "set size."
        )

    if non_negative:
        # Ridge-regularized non-negative least squares: augment the design
        # matrix with sqrt(alpha) * I and target 0, then solve via NNLS,
        # which is the standard trick for non-negative ridge.
        n_features = X.shape[1]
        X_aug = np.vstack([X, np.sqrt(ridge_alpha) * np.eye(n_features)])
        y_aug = np.concatenate([y_valid, np.zeros(n_features)])
        coef, _ = nnls(X_aug, y_aug)
        preds = X @ coef
        ss_res = np.sum((y_valid - preds) ** 2)
        ss_tot = np.sum((y_valid - y_valid.mean()) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 1e-12 else 0.0
    else:
        model = Ridge(alpha=ridge_alpha, fit_intercept=False)
        model.fit(X, y_valid)
        coef = model.coef_
        r_squared = model.score(X, y_valid)

    # Normalize weights to sum to 1 for interpretability (doesn't change
    # relative ranking of buy/sell/hold, just keeps the composite score's
    # scale sane).
    coef = np.array(coef)
    total = coef.sum()
    normalized = coef / total if total > 1e-9 else coef

    weights = {name: float(w) for name, w in zip(indicator_names, normalized)}

    return CompositeWeights(
        indicator_names=indicator_names,
        weights=weights,
        ridge_alpha=ridge_alpha,
        r_squared=float(r_squared),
    )
