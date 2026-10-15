"""
Data splitting.

Two distinct concerns live here, both from the design discussion:

1. Walk-forward three-way split (fit / weight-fit / test) in TIME, so
   nothing is tuned and evaluated on the same period twice, and Stage 6
   weight-fitting can't double-dip on the same data Stage 1 thresholds
   were fit on.

2. Non-overlapping forward-return sampling, so consecutive rows in the
   regression aren't 29/30 days apart in an overlapping window (which
   would understate the true noise in the fitted curve).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from stock_eval.config import (
    SPLIT_FIT_FRAC,
    SPLIT_WEIGHT_FIT_FRAC,
    SPLIT_TEST_FRAC,
    N_SEARCH_FRAC_OF_FIT,
    FORWARD_RETURN_HORIZON_DAYS,
)


@dataclass(frozen=True)
class ThreeWaySplit:
    fit: pd.DataFrame
    weight_fit: pd.DataFrame
    test: pd.DataFrame


@dataclass(frozen=True)
class FitSetSubsplit:
    """Further split of the fit set for Stage 5's N-selection, so the
    search slice and confirm slice don't overlap."""
    n_search: pd.DataFrame
    n_confirm: pd.DataFrame


def walk_forward_three_way_split(df: pd.DataFrame, date_col: str = "date") -> ThreeWaySplit:
    """
    Split a DataFrame chronologically into fit / weight-fit / test slices.
    Assumes `df` is already sorted (or sorts it) by `date_col`.

    This is walk-forward by construction: fit is the earliest slice,
    weight_fit is the middle slice, test is the most recent slice. None of
    the three slices' date ranges overlap.
    """
    total = SPLIT_FIT_FRAC + SPLIT_WEIGHT_FIT_FRAC + SPLIT_TEST_FRAC
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"Split fractions must sum to 1.0, got {total}")

    df = df.sort_values(date_col).reset_index(drop=True)
    n = len(df)
    fit_end = int(n * SPLIT_FIT_FRAC)
    weight_fit_end = fit_end + int(n * SPLIT_WEIGHT_FIT_FRAC)

    return ThreeWaySplit(
        fit=df.iloc[:fit_end].reset_index(drop=True),
        weight_fit=df.iloc[fit_end:weight_fit_end].reset_index(drop=True),
        test=df.iloc[weight_fit_end:].reset_index(drop=True),
    )


def subsplit_fit_set_for_n_search(fit_df: pd.DataFrame, date_col: str = "date") -> FitSetSubsplit:
    """
    Further split the fit set (chronologically) into an N-search slice and
    an N-confirm slice, so Stage 5's trajectory-window selection is
    validated out-of-sample within the fit set, rather than searching and
    confirming on the same data.
    """
    df = fit_df.sort_values(date_col).reset_index(drop=True)
    n = len(df)
    split_point = int(n * N_SEARCH_FRAC_OF_FIT)
    return FitSetSubsplit(
        n_search=df.iloc[:split_point].reset_index(drop=True),
        n_confirm=df.iloc[split_point:].reset_index(drop=True),
    )


def sample_non_overlapping(
    df: pd.DataFrame,
    horizon_days: int = FORWARD_RETURN_HORIZON_DAYS,
    date_col: str = "date",
) -> pd.DataFrame:
    """
    Downsample to one observation every `horizon_days` trading days per
    ticker, so forward-return windows used in the regression don't overlap.

    This directly addresses the autocorrelated-errors issue: computing a
    30-day forward return for every single day means consecutive rows
    share 29 of their 30 days, which inflates apparent statistical
    confidence in the fitted curve. Sampling every `horizon_days` rows
    removes that overlap at the cost of data density -- which is exactly
    why sector pooling (more tickers) matters more under this scheme.

    Expects `df` to already be sorted by date within each ticker group and
    to contain a 'ticker' column; if a single-ticker frame is passed
    without that column, it's treated as one group.
    """
    if "ticker" not in df.columns:
        df = df.sort_values(date_col).reset_index(drop=True)
        return df.iloc[::horizon_days].reset_index(drop=True)

    sampled = (
        df.sort_values([  # ensure chronological order within each ticker
            "ticker", date_col
        ])
        .groupby("ticker", group_keys=False)
        .apply(lambda g: g.iloc[::horizon_days])
    )
    return sampled.reset_index(drop=True)
