"""
Stage 7: signal band calibration and final held-out evaluation.

Bands (what composite score counts as buy/sell/hold) are calibrated here,
against the test set -- the one slice untouched by every prior fitting
step (Stage 1 thresholds, Stage 5 N-selection, Stage 6 weights). This is
also where the pipeline's real, honest performance number comes from;
everything upstream is a fitting diagnostic, not a validation result.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from stock_eval.pipeline.stage1_threshold import LookupTable
from stock_eval.pipeline.stage5_trajectory import TrajectoryFitResult
from stock_eval.pipeline.stage6_weights import CompositeWeights, compute_indicator_score_series


@dataclass(frozen=True)
class BandThresholds:
    sell_threshold: float   # composite score below this -> "sell"
    buy_threshold: float    # composite score above this -> "buy"
    # scores in between -> "hold"


@dataclass(frozen=True)
class TestSetEvaluation:
    band_thresholds: BandThresholds
    test_correlation: float          # composite score vs forward return
    mean_return_by_signal: dict[str, float]
    n_observations: int
    n_buy: int
    n_sell: int
    n_hold: int


def compute_composite_score(
    df: pd.DataFrame,
    tables: dict[str, LookupTable],
    trajectory_results: dict[str, TrajectoryFitResult],
    weights: CompositeWeights,
) -> pd.Series:
    score_cols = {
        name: compute_indicator_score_series(df, name, tables[name], trajectory_results[name].chosen_n)
        for name in weights.indicator_names
    }
    scores_df = pd.DataFrame(score_cols)
    weighted = sum(scores_df[name] * weights.weights[name] for name in weights.indicator_names)
    return weighted.clip(-1, 1).rename("composite_score")


def calibrate_bands(
    weight_fit_df: pd.DataFrame,
    tables: dict[str, LookupTable],
    trajectory_results: dict[str, TrajectoryFitResult],
    weights: CompositeWeights,
    forward_return_col: str,
    buy_quantile: float = 0.75,
    sell_quantile: float = 0.25,
) -> BandThresholds:
    """
    Calibrate band thresholds on the weight-fit set (not the test set --
    the test set stays untouched until final evaluation). Bands are set at
    quantiles of the composite score distribution rather than arbitrary
    round numbers like +/-0.3, per the design discussion.
    """
    composite = compute_composite_score(weight_fit_df, tables, trajectory_results, weights)
    valid = composite.notna()
    sell_threshold = float(np.quantile(composite[valid], sell_quantile))
    buy_threshold = float(np.quantile(composite[valid], buy_quantile))
    return BandThresholds(sell_threshold=sell_threshold, buy_threshold=buy_threshold)


def assign_signal(score: float, bands: BandThresholds) -> str:
    if pd.isna(score):
        return "hold"  # conservative default for missing/insufficient data
    if score >= bands.buy_threshold:
        return "buy"
    if score <= bands.sell_threshold:
        return "sell"
    return "hold"


def evaluate_on_test_set(
    test_df: pd.DataFrame,
    tables: dict[str, LookupTable],
    trajectory_results: dict[str, TrajectoryFitResult],
    weights: CompositeWeights,
    bands: BandThresholds,
    forward_return_col: str,
) -> TestSetEvaluation:
    """
    The pipeline's one honest performance number: composite score and
    resulting buy/sell/hold signal evaluated on data no prior stage ever
    saw. Everything upstream (Stage 1 curve shape, Stage 5 N validation,
    Stage 6 weight fit) is a fitting/diagnostic number, not this.
    """
    composite = compute_composite_score(test_df, tables, trajectory_results, weights)
    signals = composite.apply(lambda s: assign_signal(s, bands))

    valid = composite.notna() & test_df[forward_return_col].notna()
    corr = (
        float(composite[valid].corr(test_df[forward_return_col][valid]))
        if valid.sum() >= 30
        else float("nan")
    )

    mean_by_signal = {}
    for label in ("buy", "hold", "sell"):
        mask = valid & (signals == label)
        mean_by_signal[label] = (
            float(test_df[forward_return_col][mask].mean()) if mask.sum() > 0 else float("nan")
        )

    return TestSetEvaluation(
        band_thresholds=bands,
        test_correlation=corr,
        mean_return_by_signal=mean_by_signal,
        n_observations=int(valid.sum()),
        n_buy=int((signals == "buy").sum()),
        n_sell=int((signals == "sell").sum()),
        n_hold=int((signals == "hold").sum()),
    )
