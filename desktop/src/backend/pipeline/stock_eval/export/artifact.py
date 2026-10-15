"""
JSON artifact export -- the handoff contract between the Python fitting
pipeline and the JS/Electron runtime.

Schema is versioned (`schema_version`) from day one so a future change to
this shape doesn't silently break an older app build, or vice versa (see
the JSON schema versioning pain point flagged during design review).
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone

from stock_eval.config import UniverseConfig
from stock_eval.pipeline.stage1_threshold import LookupTable
from stock_eval.pipeline.stage5_trajectory import TrajectoryFitResult
from stock_eval.pipeline.stage6_weights import CompositeWeights
from stock_eval.pipeline.stage7_bands import BandThresholds, TestSetEvaluation

SCHEMA_VERSION = "1.0.0"


def build_artifact(
    sector: str,
    universe_config: UniverseConfig,
    tables: dict[str, LookupTable],
    trajectory_results: dict[str, TrajectoryFitResult],
    weights: CompositeWeights,
    bands: BandThresholds,
    test_evaluation: TestSetEvaluation,
    forward_return_horizon_days: int,
) -> dict:
    """
    Assemble the full artifact dict for one sector's fitted model. This is
    what gets json.dump'd and read by the JS runtime.
    """
    indicators_payload = {}
    for name, table in tables.items():
        traj = trajectory_results[name]
        indicators_payload[name] = {
            "lookup_table": table.to_points(),
            "optimal_n": traj.chosen_n,
            "n_validated": traj.validated,  # False -> fell back to default
            "weight": weights.weights[name],
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sector": sector,
        "forward_return_horizon_days": forward_return_horizon_days,
        "universe": {
            "market": universe_config.market,
            "survivorship_bias_free": universe_config.survivorship_bias_free,
            "source": universe_config.source,
        },
        "indicators": indicators_payload,
        "bands": {
            "sell_threshold": bands.sell_threshold,
            "buy_threshold": bands.buy_threshold,
        },
        # Diagnostics from the held-out test set -- the artifact carries
        # its own honest performance record, so a stale/bad refit can be
        # sanity-checked (compare against the previous artifact's numbers)
        # before it's trusted, per the "no guardrail against a bad refit"
        # pain point flagged during design review.
        "test_set_diagnostics": {
            "correlation": test_evaluation.test_correlation,
            "n_observations": test_evaluation.n_observations,
            "n_buy": test_evaluation.n_buy,
            "n_sell": test_evaluation.n_sell,
            "n_hold": test_evaluation.n_hold,
            "mean_return_by_signal": test_evaluation.mean_return_by_signal,
        },
    }


def save_artifact(artifact: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(artifact, f, indent=2)


def sanity_check_against_previous(new_artifact: dict, previous_artifact: dict, max_weight_shift: float = 0.35, max_band_shift: float = 0.3) -> list[str]:
    """
    Guardrail against a bad refit (flagged during design review): compare
    a newly-fit artifact against the previous one and flag implausible
    jumps in weights or band thresholds before the new artifact is allowed
    to go live. Returns a list of warning strings; empty list = looks fine.

    This is a heuristic tripwire, not a proof of correctness -- tune the
    thresholds as you observe normal refit-to-refit variation in practice.
    """
    warnings: list[str] = []

    prev_weights = {
        name: info["weight"] for name, info in previous_artifact.get("indicators", {}).items()
    }
    new_weights = {
        name: info["weight"] for name, info in new_artifact.get("indicators", {}).items()
    }
    for name, new_w in new_weights.items():
        old_w = prev_weights.get(name)
        if old_w is not None and abs(new_w - old_w) > max_weight_shift:
            warnings.append(
                f"Weight for '{name}' shifted by {abs(new_w - old_w):.2f} "
                f"({old_w:.2f} -> {new_w:.2f}), exceeding {max_weight_shift}."
            )

    old_bands = previous_artifact.get("bands", {})
    new_bands = new_artifact.get("bands", {})
    for key in ("buy_threshold", "sell_threshold"):
        if key in old_bands and key in new_bands:
            shift = abs(new_bands[key] - old_bands[key])
            if shift > max_band_shift:
                warnings.append(
                    f"Band '{key}' shifted by {shift:.2f} "
                    f"({old_bands[key]:.2f} -> {new_bands[key]:.2f}), "
                    f"exceeding {max_band_shift}."
                )

    return warnings
