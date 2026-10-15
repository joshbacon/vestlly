# Stock Evaluation Runtime (JS side)

This is the live-scoring half of the pipeline: given an artifact produced
by the Python fitting pipeline and a stock's current + recent indicator
values, it computes a composite score in [-1, 1] and a buy/sell/hold
signal. Intended to run inside your Electron app.

## Usage

```js
const { computeAllIndicators } = require('./src/indicators');
const { evaluateStock } = require('./src/scoring');

// 1. Load the artifact matching this stock's sector.
const artifact = require('./artifacts/us_tech.json');

// 2. Get raw daily OHLCV history for the stock, ascending by date --
//    [{ date, open, high, low, close, volume }, ...]. Needs enough
//    history for the longest lookback (50 days for sma_dist_50) plus
//    `optimal_n` more for trajectory to kick in; less still works, it
//    just falls back to a neutral (level-only) score for that indicator.
const ohlcvRows = /* ...from your existing price data source... */;

// 3. Compute all indicators from raw prices -- ported directly from the
//    Python fitting pipeline's indicators/compute.py, see parity notes
//    below.
const indicatorHistories = computeAllIndicators(ohlcvRows);

// 4. Score it.
const result = evaluateStock(artifact, indicatorHistories);
console.log(result.compositeScore, result.signal);
// result.perIndicator gives you the level/trajectory breakdown per
// indicator -- surface this in the UI so a score isn't a black box
// (per the design discussion on user trust + your own debugging).
```

`computeAllIndicators` is a deliberate port of the Python side's
`indicators/compute.py` -- same RSI/MACD EWM conventions
(`adjust=False`), same rolling-window `min_periods` behavior, same
normalization (MACD histogram ÷ price, SMA distance as % of price). A
generic charting library's RSI/MACD will very likely NOT match these
conventions exactly (see "Why port instead of using a library" below) --
use this module, not a substitute, unless you've verified equivalence
yourself.

## Formula parity with Python

Two files here are deliberate ports of Python fitting-pipeline code, and
both are covered by the parity check:

- `src/indicators.js` ports `stock_eval/indicators/compute.py` (RSI,
  stochastic %K, Bollinger %B, MACD histogram, SMA distance).
- `src/scoring.js` ports `stock_eval/pipeline/stage1_threshold.py`
  (interpolation + calibration) and `stock_eval/pipeline/stage5_trajectory.py`
  (trajectory multiplier).

**Whenever any of those three Python files change, re-run the parity check:**

```bash
# from the Python repo
python -m stock_eval.tools.generate_parity_fixture
cp parity_fixture.json <this repo>/

# from this repo
node parity_check.js
```

The fixture now contains a deterministic 200-day synthetic OHLCV series
plus Python's computed indicator values for it, alongside the original
lookup-table/trajectory test cases -- so one run checks indicator
computation end-to-end (raw prices → indicator series) as well as the
scoring math. Indicator checks use a 1e-6 tolerance (many chained
floating-point rolling/EWM operations); scoring checks use 1e-9.

Exits 0 if Python and JS agree on every case, non-zero otherwise. Wire
this into CI on both repos so a change to either side's math is caught
immediately rather than surfacing later as a live score that doesn't
match what the artifact implies.

### Why port instead of using a charting library's indicators

RSI and MACD in particular have multiple common, equally "correct"
conventions (different EWM seeding, `adjust=True` vs `adjust=False`,
SMA-seeded vs EWM-seeded Wilder smoothing) that agree asymptotically but
diverge meaningfully over the short-to-medium term -- exactly where
trajectory scoring is most sensitive. Since Stage 1's lookup tables were
fit against this specific implementation's output, a library using a
different convention would silently mis-score live stocks with no error
thrown. The parity check above is what makes this verifiable rather than
assumed.

## One intentional Python/JS behavioral difference

Python's Stage 6 fitting code (`compute_indicator_score_series`) drops
NaN rows entirely when an indicator's trajectory can't be computed (not
enough history) -- correct for *fitting*, since you don't want sparse-data
rows influencing the composite weight regression.

The JS runtime instead falls back to a **neutral trajectory multiplier of
1.0** (level-only score) when there isn't enough history yet -- correct
for *live scoring*, since you don't want to refuse to score a newly-added
or thinly-tracked stock just because trajectory isn't available yet. This
is a deliberate, documented divergence, not a parity bug -- the parity
check only covers the math that's supposed to match exactly
(interpolation, calibration, the multiplier formula itself), not this
fallback behavior.

## Missing indicators

If `indicatorHistories` is missing an indicator entirely (e.g. a
data-quality gap upstream), `evaluateStock` renormalizes the composite
over the weight that *was* usable, rather than treating the missing
indicator as a silent zero contribution -- a zero would bias the
composite toward "hold" regardless of what the missing indicator would
have said. `result.missingIndicators` tells you which ones were skipped,
so you can decide whether to trust the resulting score or show a
lower-confidence indicator in the UI.
