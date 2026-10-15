# Stock Evaluation Fitting Pipeline (Python side)

This is the Python half of the two-language architecture we settled on:
this package does the heavy statistical fitting (Stages 1, 5, 6, 7) on a
schedule; a JS/Electron runtime (not included here) loads the JSON
artifact this produces and does the lightweight live scoring (Stages 2-4).

## Quick start

```bash
pip install -r requirements.txt --break-system-packages   # or use a venv
python -m stock_eval.main --sector TECH --market US
```

This runs the entire pipeline against **synthetic data** (no API key
needed) and writes `artifacts/sector_model.json`. The synthetic generator
bakes in a mild, known mean-reverting relationship so you can confirm the
pipeline actually recovers a sensible-looking curve, not just that it runs
without crashing.

Try the Canadian path too -- it's deliberately left in the repo failing
under default synthetic settings, to demonstrate a real guardrail:

```bash
python -m stock_eval.main --sector FINANCIALS --market CA
```

This raises `RuntimeError: No indicators were successfully fit` because
the synthetic CA universe (15 tickers) doesn't produce enough
non-overlapping observations to fill 25 bins at the configured minimum
samples/bin. That's the pipeline correctly refusing to fit a table it
can't trust, rather than silently producing a bad one -- exactly the kind
of check you want firing on a real, possibly-thin CA sector universe. Fix
by lowering `LOOKUP_TABLE_BINS` / `MIN_SAMPLES_PER_BIN` in `config.py`,
pooling a broader universe, or accepting fewer bins for smaller markets.

## How this maps to the design

| Stage | Module | What it does |
|---|---|---|
| Universe + data | `data/sources.py` | `DataSource` interface; `SyntheticDataSource` for dev, `EODHDDataSource` stub for real data |
| Indicators | `indicators/compute.py` | RSI, stochastic %K, Bollinger %B, MACD histogram, SMA distance -- scale-dependent ones normalized by price before pooling |
| Splitting | `pipeline/splits.py` | Walk-forward fit/weight-fit/test split; non-overlapping forward-return sampling (autocorrelation fix); fit-set sub-split for N-search/confirm |
| Stage 1 | `pipeline/stage1_threshold.py` | Binned, smoothed lookup table per indicator; runtime-equivalent interpolation + calibration |
| Stage 5 | `pipeline/stage5_trajectory.py` | Per-indicator slope window (N) search + out-of-sample confirmation; sign-safe trajectory multiplier |
| Stage 6 | `pipeline/stage6_weights.py` | Non-negative ridge regression for composite weights, fit only on the weight-fit set |
| Stage 7 | `pipeline/stage7_bands.py` | Quantile-based band calibration + the one honest performance number, from the held-out test set |
| Export | `export/artifact.py` | Versioned JSON artifact; `sanity_check_against_previous()` guardrail against a bad refit |

All structural decisions (30-day horizon, split fractions, bin counts,
candidate N windows, indicator scale classification, US vs CA universe
handling) live in `config.py` -- check there first before digging through
pipeline code.

## Known limitations carried over from the design discussion

- **CA universe is current-constituents-only** (`config.CA_UNIVERSE`), not
  point-in-time / survivorship-bias-free, per the scoped-down decision.
  This is tagged in every artifact's `universe` field so it's visible
  downstream, not silently absorbed.
- **`EODHDDataSource` is a stub.** `get_sector_universe` and the exact
  response parsing are placeholders -- wire up your API key and the real
  EODHD response shape before using `--use-eodhd`.
- **Python/JS formula drift risk.** The JS runtime must replicate Stage
  1's interpolation + calibration (`stage1_threshold.interpolate_level_score`)
  and Stage 5's trajectory multiplier (`stage5_trajectory.trajectory_multiplier`)
  *exactly*, including edge-clamping. Any divergence is silent -- a live
  indicator value won't score the way the lookup table implies. Write a
  cross-check early: same inputs into both implementations, same output.
- **In-sample R² from Stage 6 is a diagnostic, not a validation result.**
  Only `test_set_diagnostics.correlation` (Stage 7, held-out) reflects
  real out-of-sample performance.
- **No model-decay monitoring yet.** The artifact records its own
  test-set performance at fit time, but nothing here tracks live signal
  accuracy over time to tell you *when* a refit is needed.

## Next steps

1. Wire up `EODHDDataSource` against your actual API key and confirm the
   response parsing.
2. Build the point-in-time universe fetch for US S&P family indices
   (the `historical=1` EODHD endpoint), replacing the current-constituents
   placeholder.
3. Write the JS runtime that consumes this artifact (Stages 2-4, 7) and
   the cross-check harness for indicator-formula parity.
4. Once real data is flowing, revisit `LOOKUP_TABLE_BINS` /
   `MIN_SAMPLES_PER_BIN` / `CANDIDATE_N_WINDOWS` with real sample sizes in
   mind -- the defaults here were chosen for the synthetic demo, not
   tuned against real market data volume.
