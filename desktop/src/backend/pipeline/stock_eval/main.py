"""
Orchestrates the full fitting pipeline, end to end, for one sector:

  universe -> per-ticker OHLCV -> indicators + forward returns
    -> walk-forward 3-way split (+ non-overlapping sampling)
    -> Stage 1 (lookup tables, per indicator)
    -> Stage 5 (trajectory N, search/confirm per indicator)
    -> Stage 6 (composite weights, weight-fit set)
    -> Stage 7 (band calibration + held-out test evaluation)
    -> JSON artifact

Run with synthetic data out of the box:
    python -m stock_eval.main --sector TECH --market US

Swap in real data later by passing a different DataSource into
`run_pipeline` -- nothing else in this file needs to change.
"""

from __future__ import annotations

import argparse
import sys

import pandas as pd

from stock_eval.config import (
    FORWARD_RETURN_HORIZON_DAYS,
    INDICATOR_SPECS,
    US_UNIVERSE,
    CA_UNIVERSE,
)
from stock_eval.data.sources import DataSource, SyntheticDataSource
from stock_eval.indicators.compute import compute_all_indicators, forward_return
from stock_eval.pipeline.splits import (
    walk_forward_three_way_split,
    subsplit_fit_set_for_n_search,
    sample_non_overlapping,
)
from stock_eval.pipeline.stage1_threshold import fit_lookup_table
from stock_eval.pipeline.stage5_trajectory import select_and_validate_n
from stock_eval.pipeline.stage6_weights import fit_weights
from stock_eval.pipeline.stage7_bands import calibrate_bands, evaluate_on_test_set
from stock_eval.export.artifact import build_artifact, save_artifact

FWD_COL = f"fwd_return_{FORWARD_RETURN_HORIZON_DAYS}d"


def build_sector_dataset(source: DataSource, sector: str, market: str, start: str, end: str) -> pd.DataFrame:
    """Pull OHLCV for every ticker in the sector universe, compute
    indicators + forward returns, and stack into one long DataFrame."""
    tickers = source.get_sector_universe(sector, market)
    frames = []
    for ticker in tickers:
        ohlcv = source.get_daily_ohlcv(ticker, start, end)
        ind = compute_all_indicators(ohlcv.frame)
        ind[FWD_COL] = forward_return(ohlcv.frame, FORWARD_RETURN_HORIZON_DAYS)
        ind["ticker"] = ticker
        frames.append(ind)
    return pd.concat(frames, ignore_index=True)


def run_pipeline(
    source: DataSource,
    sector: str,
    market: str,
    start: str,
    end: str,
    output_path: str,
) -> dict:
    universe_config = US_UNIVERSE if market == "US" else CA_UNIVERSE

    print(f"[1/6] Building sector dataset ({sector}, {market})...")
    full_df = build_sector_dataset(source, sector, market, start, end)
    print(f"      {len(full_df)} rows across {full_df['ticker'].nunique()} tickers")

    print("[2/6] Walk-forward 3-way split + non-overlapping sampling...")
    split = walk_forward_three_way_split(full_df)
    fit_sampled = sample_non_overlapping(split.fit)
    weight_fit_sampled = sample_non_overlapping(split.weight_fit)
    test_sampled = sample_non_overlapping(split.test)
    n_subsplit = subsplit_fit_set_for_n_search(fit_sampled)
    print(f"      fit={len(fit_sampled)}, weight_fit={len(weight_fit_sampled)}, "
          f"test={len(test_sampled)} rows after sampling")

    tables = {}
    trajectory_results = {}

    for spec in INDICATOR_SPECS:
        name = spec.name
        print(f"[3/6] Stage 1 - fitting lookup table for '{name}'...")
        try:
            table = fit_lookup_table(fit_sampled[name], fit_sampled[FWD_COL], name)
        except ValueError as e:
            print(f"      SKIPPING '{name}': {e}", file=sys.stderr)
            continue
        tables[name] = table

        print(f"[4/6] Stage 5 - selecting trajectory N for '{name}'...")
        traj_result = select_and_validate_n(
            n_subsplit.n_search, n_subsplit.n_confirm, name, FWD_COL, table
        )
        trajectory_results[name] = traj_result
        status = "validated" if traj_result.validated else "FALLBACK (no improvement confirmed)"
        print(f"      N={traj_result.chosen_n} ({status}), "
              f"confirm_corr={traj_result.confirm_correlation:.4f} vs "
              f"level_only={traj_result.level_only_correlation:.4f}")

    if not tables:
        raise RuntimeError("No indicators were successfully fit -- check data volume.")

    print("[5/6] Stage 6 - fitting composite weights on weight-fit set...")
    weights = fit_weights(weight_fit_sampled, tables, trajectory_results, FWD_COL)
    for name, w in weights.weights.items():
        print(f"      {name}: weight={w:.3f}")
    print(f"      (in-sample R^2 on weight-fit set: {weights.r_squared:.4f} "
          f"-- diagnostic only, not a validation result)")

    print("[6/6] Stage 7 - calibrating bands and evaluating on held-out test set...")
    bands = calibrate_bands(weight_fit_sampled, tables, trajectory_results, weights, FWD_COL)
    test_eval = evaluate_on_test_set(
        test_sampled, tables, trajectory_results, weights, bands, FWD_COL
    )
    print(f"      buy_threshold={bands.buy_threshold:.3f}, sell_threshold={bands.sell_threshold:.3f}")
    print(f"      TEST SET correlation (the honest number): {test_eval.test_correlation:.4f}")
    print(f"      mean forward return by signal: {test_eval.mean_return_by_signal}")

    artifact = build_artifact(
        sector=sector,
        universe_config=universe_config,
        tables=tables,
        trajectory_results=trajectory_results,
        weights=weights,
        bands=bands,
        test_evaluation=test_eval,
        forward_return_horizon_days=FORWARD_RETURN_HORIZON_DAYS,
    )
    save_artifact(artifact, output_path)
    print(f"\nArtifact written to {output_path}")
    return artifact


def main():
    parser = argparse.ArgumentParser(description="Run the stock evaluation fitting pipeline.")
    parser.add_argument("--sector", default="TECH")
    parser.add_argument("--market", default="US", choices=["US", "CA"])
    parser.add_argument("--start", default="2015-01-01")
    parser.add_argument("--end", default="2025-01-01")
    parser.add_argument("--output", default="artifacts/sector_model.json")
    parser.add_argument(
        "--use-eodhd", action="store_true",
        help="Use EODHDDataSource (requires EODHD_API_KEY env var) instead of synthetic data.",
    )
    args = parser.parse_args()

    if args.use_eodhd:
        from stock_eval.data.sources import EODHDDataSource
        source = EODHDDataSource()
    else:
        source = SyntheticDataSource()
        print("Using synthetic data source (pass --use-eodhd for real data once configured).\n")

    run_pipeline(source, args.sector, args.market, args.start, args.end, args.output)


if __name__ == "__main__":
    main()
