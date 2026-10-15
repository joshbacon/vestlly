/**
 * Indicator computation -- a deliberate port of
 * stock_eval/indicators/compute.py, matching pandas' exact conventions
 * (EWM with adjust=False, rolling min_periods behavior, sample std with
 * ddof=1) rather than using a generic charting library's indicator
 * implementations, which commonly differ in these details. See
 * PARITY.md / the top-level README for why this matters: Stage 1's
 * lookup tables were fit against these exact formulas, so a differently
 * -conventioned RSI/MACD/etc. would silently mis-score live stocks.
 *
 * Input: an array of { date, open, high, low, close, volume } objects,
 * sorted ascending by date (oldest first) -- same convention as
 * evaluateStock's indicatorHistories expects.
 *
 * Output: for each indicator, an array the same length as the input,
 * with `null` wherever pandas would have produced NaN (not enough
 * history yet), and a number everywhere else.
 */

'use strict';

// ---------------------------------------------------------------------
// Generic rolling-window / EWM helpers, matching pandas semantics
// ---------------------------------------------------------------------

/** Rolling mean, matching pandas .rolling(window).mean() (min_periods
 * defaults to `window`, i.e. the first `window - 1` outputs are null). */
function rollingMean(values, window, minPeriods = window) {
  const n = values.length;
  const out = new Array(n).fill(null);
  let sum = 0;
  const buf = [];
  for (let i = 0; i < n; i++) {
    buf.push(values[i]);
    sum += values[i];
    if (buf.length > window) sum -= buf.shift();
    if (buf.length >= minPeriods) out[i] = sum / buf.length;
  }
  return out;
}

/** Rolling sample standard deviation (ddof=1), matching pandas
 * .rolling(window).std() default behavior. */
function rollingStd(values, window, minPeriods = window) {
  const n = values.length;
  const out = new Array(n).fill(null);
  const buf = [];
  for (let i = 0; i < n; i++) {
    buf.push(values[i]);
    if (buf.length > window) buf.shift();
    if (buf.length >= minPeriods && buf.length >= 2) {
      const mean = buf.reduce((a, b) => a + b, 0) / buf.length;
      const sumSqDiff = buf.reduce((a, b) => a + (b - mean) ** 2, 0);
      out[i] = Math.sqrt(sumSqDiff / (buf.length - 1)); // ddof=1
    }
  }
  return out;
}

/** Rolling min, matching pandas .rolling(window).min(). */
function rollingMin(values, window, minPeriods = window) {
  return rollingReduce(values, window, minPeriods, (buf) => Math.min(...buf));
}

/** Rolling max, matching pandas .rolling(window).max(). */
function rollingMax(values, window, minPeriods = window) {
  return rollingReduce(values, window, minPeriods, (buf) => Math.max(...buf));
}

function rollingReduce(values, window, minPeriods, fn) {
  const n = values.length;
  const out = new Array(n).fill(null);
  const buf = [];
  for (let i = 0; i < n; i++) {
    buf.push(values[i]);
    if (buf.length > window) buf.shift();
    if (buf.length >= minPeriods) out[i] = fn(buf);
  }
  return out;
}

/**
 * Exponentially-weighted mean matching pandas .ewm(..., adjust=False).mean().
 *
 * Pandas' adjust=False recursion: y[0] = x[0]; y[t] = (1-alpha)*y[t-1] + alpha*x[t].
 * This recursion runs from the very first value regardless of min_periods
 * -- min_periods only controls which output positions are reported as
 * null, not how the internal state accumulates. Getting this wrong (e.g.
 * resetting the recursion at min_periods) silently produces different
 * values than pandas for the same alpha, especially early in the series.
 *
 * Pass either `alpha` directly (used by RSI's Wilder smoothing, alpha=1/14)
 * or `span` (used by MACD, alpha = 2/(span+1)).
 */
function ewmMean(values, { alpha, span, minPeriods = 0 } = {}) {
  const a = alpha !== undefined ? alpha : 2 / (span + 1);
  const n = values.length;
  const out = new Array(n).fill(null);

  let y = null;
  let seen = 0;
  for (let i = 0; i < n; i++) {
    const x = values[i];
    if (x === null || Number.isNaN(x)) {
      // pandas ewm treats leading NaNs as "not yet started"; once started,
      // it doesn't handle interior NaNs the way we need for this pipeline
      // (our indicator inputs shouldn't have interior NaNs in practice).
      continue;
    }
    y = y === null ? x : (1 - a) * y + a * x;
    seen += 1;
    if (seen >= Math.max(minPeriods, 1)) out[i] = y;
  }
  return out;
}

// ---------------------------------------------------------------------
// Indicators -- mirrors indicators/compute.py function-for-function
// ---------------------------------------------------------------------

function diff(values) {
  const out = new Array(values.length).fill(null);
  for (let i = 1; i < values.length; i++) out[i] = values[i] - values[i - 1];
  return out;
}

/** Mirrors: indicators/compute.py -> rsi_14() */
function rsi14(rows) {
  const close = rows.map((r) => r.close);
  const delta = diff(close);

  const gain = delta.map((d) => (d === null ? null : Math.max(d, 0)));
  const loss = delta.map((d) => (d === null ? null : Math.max(-d, 0)));

  // delta[0] is null (no prior value) -- matches pandas .diff()'s first
  // element being NaN, which then propagates through gain/loss/ewm below
  // exactly as it does in pandas.
  const avgGain = ewmMean(gain, { alpha: 1 / 14, minPeriods: 14 });
  const avgLoss = ewmMean(loss, { alpha: 1 / 14, minPeriods: 14 });

  return avgGain.map((ag, i) => {
    const al = avgLoss[i];
    if (ag === null || al === null) return null;
    if (al === 0) return null; // pandas: division by 0 -> inf -> rsi=100, but
    // avg_loss.replace(0, np.nan) in Python turns this into NaN explicitly,
    // matched here.
    const rs = ag / al;
    return 100 - 100 / (1 + rs);
  });
}

/** Mirrors: indicators/compute.py -> stoch_k_14() */
function stochK14(rows) {
  const low = rows.map((r) => r.low);
  const high = rows.map((r) => r.high);
  const close = rows.map((r) => r.close);

  const lowMin = rollingMin(low, 14);
  const highMax = rollingMax(high, 14);

  return close.map((c, i) => {
    if (lowMin[i] === null || highMax[i] === null) return null;
    const denom = highMax[i] - lowMin[i];
    if (denom === 0) return null; // matches .replace(0, np.nan) in Python
    return (100 * (c - lowMin[i])) / denom;
  });
}

/** Mirrors: indicators/compute.py -> bb_percent_b_20() */
function bbPercentB20(rows) {
  const close = rows.map((r) => r.close);
  const sma = rollingMean(close, 20);
  const std = rollingStd(close, 20);

  return close.map((c, i) => {
    if (sma[i] === null || std[i] === null) return null;
    const upper = sma[i] + 2 * std[i];
    const lower = sma[i] - 2 * std[i];
    const denom = upper - lower;
    if (denom === 0) return null;
    return (c - lower) / denom;
  });
}

/** Mirrors: indicators/compute.py -> macd_hist_norm() */
function macdHistNorm(rows) {
  const close = rows.map((r) => r.close);
  const ema12 = ewmMean(close, { span: 12 });
  const ema26 = ewmMean(close, { span: 26 });

  const macdLine = close.map((_, i) => {
    if (ema12[i] === null || ema26[i] === null) return null;
    return ema12[i] - ema26[i];
  });

  const signal = ewmMean(macdLine, { span: 9 });

  return close.map((c, i) => {
    if (macdLine[i] === null || signal[i] === null) return null;
    const hist = macdLine[i] - signal[i];
    return hist / c; // scale-dependent -> normalized by price
  });
}

/** Mirrors: indicators/compute.py -> sma_dist_50() */
function smaDist50(rows) {
  const close = rows.map((r) => r.close);
  const sma = rollingMean(close, 50);

  return close.map((c, i) => {
    if (sma[i] === null || sma[i] === 0) return null;
    return (c - sma[i]) / sma[i]; // scale-dependent -> % distance from price
  });
}

const REGISTRY = {
  rsi_14: rsi14,
  stoch_k_14: stochK14,
  bb_percent_b_20: bbPercentB20,
  macd_hist_norm: macdHistNorm,
  sma_dist_50: smaDist50,
};

/**
 * Compute one named indicator over an OHLCV row array.
 * @param {string} name
 * @param {Array<{date, open, high, low, close, volume}>} rows - ascending by date.
 * @returns {Array<number|null>}
 */
function computeIndicator(name, rows) {
  const fn = REGISTRY[name];
  if (!fn) {
    throw new Error(`No indicator function registered for '${name}'. Known: ${Object.keys(REGISTRY)}`);
  }
  return fn(rows);
}

/**
 * Compute every registered indicator over an OHLCV row array, returning
 * an object of { indicatorName: [values...] } directly usable as the
 * `indicatorHistories` argument to evaluateStock() in scoring.js (after
 * slicing to whatever recent window you want to pass through).
 */
function computeAllIndicators(rows) {
  const out = {};
  for (const name of Object.keys(REGISTRY)) {
    out[name] = computeIndicator(name, rows);
  }
  return out;
}

module.exports = {
  rollingMean,
  rollingStd,
  rollingMin,
  rollingMax,
  ewmMean,
  computeIndicator,
  computeAllIndicators,
};
