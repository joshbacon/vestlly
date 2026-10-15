/**
 * Live scoring runtime (Stages 2-4 and 7).
 *
 * This is a deliberate, line-for-line port of the Python fitting logic in
 * stage1_threshold.py (interpolation + calibration) and
 * stage5_trajectory.py (trajectory multiplier). It must stay in exact sync
 * with those two files -- see PARITY.md and parity_check.js for how to
 * verify that after any change on either side.
 *
 * This module does NOT fit anything. It only consumes an already-fitted
 * artifact (the JSON produced by the Python pipeline) and scores a single
 * stock's current + recent indicator values against it.
 */

'use strict';

/**
 * Linear interpolation on a lookup table, clamped at the edges, then
 * calibrated onto [-1, 1] using the table's own observed value range.
 *
 * Mirrors: stock_eval/pipeline/stage1_threshold.py
 *   -> interpolate_level_score() + _calibrate_to_range()
 *
 * @param {Array<[number, number]>} lookupTable - [[x, y], ...] sorted by x ascending (as exported by Python).
 * @param {number} value - current indicator value.
 * @param {[number, number]} scoreRange - defaults to [-1, 1].
 * @returns {number} level_score
 */
function interpolateLevelScore(lookupTable, value, scoreRange = [-1, 1]) {
  const xs = lookupTable.map((p) => p[0]);
  const ysRaw = lookupTable.map((p) => p[1]);

  let raw;
  if (value <= xs[0]) {
    raw = ysRaw[0];
  } else if (value >= xs[xs.length - 1]) {
    raw = ysRaw[ysRaw.length - 1];
  } else {
    raw = linearInterp(xs, ysRaw, value);
  }

  return calibrateToRange(raw, ysRaw, scoreRange);
}

/** Equivalent to numpy.interp for a scalar x. Assumes xs is sorted ascending. */
function linearInterp(xs, ys, x) {
  // Find the bracketing segment.
  let i = 0;
  while (i < xs.length - 1 && xs[i + 1] < x) i++;
  const x0 = xs[i];
  const x1 = xs[i + 1];
  const y0 = ys[i];
  const y1 = ys[i + 1];
  if (x1 === x0) return y0;
  const t = (x - x0) / (x1 - x0);
  return y0 + t * (y1 - y0);
}

/**
 * Min-max calibration of a raw forward-return-scale value onto scoreRange,
 * based on the observed min/max of the fitted table itself.
 *
 * Mirrors: stage1_threshold.py -> _calibrate_to_range()
 */
function calibrateToRange(rawValue, allRawValues, scoreRange) {
  const lo = Math.min(...allRawValues);
  const hi = Math.max(...allRawValues);
  if (hi - lo < 1e-12) return 0.0;
  const normalized = (rawValue - lo) / (hi - lo); // 0..1
  const [outLo, outHi] = scoreRange;
  return outLo + normalized * (outHi - outLo);
}

/**
 * Simple slope over the last n periods: (value_t - value_{t-n}) / n.
 *
 * Mirrors: stage5_trajectory.py -> compute_slope()
 *
 * @param {number[]} series - indicator values, oldest first, most recent last.
 * @param {number} n
 * @returns {number|null} null if there isn't enough history yet.
 */
function computeSlope(series, n) {
  if (series.length <= n) return null;
  const current = series[series.length - 1];
  const past = series[series.length - 1 - n];
  if (current == null || past == null || Number.isNaN(current) || Number.isNaN(past)) {
    return null;
  }
  return (current - past) / n;
}

/**
 * Local gradient of the fitted curve at `value`, via central finite
 * difference on the lookup table -- same approach as
 * `np.gradient(table.bin_values, table.bin_midpoints)` in Python, then
 * interpolated to the query value.
 */
function localCurveGradient(lookupTable, value) {
  const xs = lookupTable.map((p) => p[0]);
  const ys = lookupTable.map((p) => p[1]);
  const n = xs.length;

  const grad = new Array(n);
  for (let i = 0; i < n; i++) {
    if (i === 0) {
      grad[i] = (ys[1] - ys[0]) / (xs[1] - xs[0]);
    } else if (i === n - 1) {
      grad[i] = (ys[n - 1] - ys[n - 2]) / (xs[n - 1] - xs[n - 2]);
    } else {
      grad[i] = (ys[i + 1] - ys[i - 1]) / (xs[i + 1] - xs[i - 1]);
    }
  }

  if (value <= xs[0]) return grad[0];
  if (value >= xs[n - 1]) return grad[n - 1];
  return linearInterp(xs, grad, value);
}

/**
 * Convert a raw slope into a positive multiplier on the level score.
 * Never flips sign -- alignment with the curve's local gradient determines
 * whether the indicator is moving toward or away from higher-scoring
 * territory, independent of the level score's own sign.
 *
 * Mirrors: stage5_trajectory.py -> trajectory_multiplier()
 */
function trajectoryMultiplier(slope, curveLocalGradient, sensitivity = 4.0, bounds = [0.5, 1.5]) {
  const alignment = slope * curveLocalGradient; // >0 => moving toward ideal
  const rawMultiplier = 1.0 + Math.tanh(alignment * sensitivity) * 0.5;
  return Math.min(bounds[1], Math.max(bounds[0], rawMultiplier));
}

/**
 * Full Stage 2-4 computation for a single indicator: level_score *
 * trajectory_multiplier, clipped to [-1, 1].
 *
 * @param {object} indicatorArtifact - artifact.indicators[name], i.e.
 *   { lookup_table, optimal_n, n_validated, weight }.
 * @param {number[]} indicatorHistory - indicator values, oldest first,
 *   most recent last, at least optimal_n + 1 long for trajectory to apply.
 * @returns {{score: number, levelScore: number, trajectoryMultiplier: number|null}}
 */
function scoreIndicator(indicatorArtifact, indicatorHistory) {
  const { lookup_table: lookupTable, optimal_n: n } = indicatorArtifact;
  const currentValue = indicatorHistory[indicatorHistory.length - 1];

  if (currentValue == null || Number.isNaN(currentValue)) {
    return { score: null, levelScore: null, trajectoryMultiplier: null };
  }

  const levelScore = interpolateLevelScore(lookupTable, currentValue);

  const slope = computeSlope(indicatorHistory, n);
  let multiplier = 1.0; // neutral if not enough history for trajectory
  if (slope !== null) {
    const gradient = localCurveGradient(lookupTable, currentValue);
    multiplier = trajectoryMultiplier(slope, gradient);
  }

  const rawScore = levelScore * multiplier;
  const score = Math.min(1, Math.max(-1, rawScore));

  return { score, levelScore, trajectoryMultiplier: multiplier };
}

/**
 * Stage 6 (runtime side) + Stage 7: weighted sum of indicator scores,
 * clipped to [-1, 1], mapped to a buy/sell/hold signal via the artifact's
 * calibrated bands.
 *
 * @param {object} artifact - the full parsed JSON artifact for a sector.
 * @param {Object<string, number[]>} indicatorHistories - map of indicator
 *   name -> array of historical values (oldest first) for one stock.
 * @returns {{
 *   compositeScore: number|null,
 *   signal: 'buy'|'sell'|'hold',
 *   perIndicator: Object<string, {score:number|null, levelScore:number|null, trajectoryMultiplier:number|null}>,
 *   missingIndicators: string[]
 * }}
 */
function evaluateStock(artifact, indicatorHistories) {
  const perIndicator = {};
  const missingIndicators = [];
  let weightedSum = 0;
  let weightUsed = 0;

  for (const [name, indicatorArtifact] of Object.entries(artifact.indicators)) {
    const history = indicatorHistories[name];
    if (!history || history.length === 0) {
      missingIndicators.push(name);
      continue;
    }

    const result = scoreIndicator(indicatorArtifact, history);
    perIndicator[name] = result;

    if (result.score !== null) {
      weightedSum += result.score * indicatorArtifact.weight;
      weightUsed += indicatorArtifact.weight;
    }
  }

  // If some indicators were missing/NaN, renormalize over the weight that
  // was actually usable rather than silently treating missing data as a
  // zero contribution (which would bias the composite toward "hold").
  let compositeScore = null;
  if (weightUsed > 1e-9) {
    compositeScore = Math.min(1, Math.max(-1, weightedSum / weightUsed));
  }

  const signal = assignSignal(compositeScore, artifact.bands);

  return { compositeScore, signal, perIndicator, missingIndicators };
}

/**
 * Mirrors: stage7_bands.py -> assign_signal()
 * Missing/insufficient data defaults to 'hold' -- the conservative choice.
 */
function assignSignal(compositeScore, bands) {
  if (compositeScore === null || compositeScore === undefined) return 'hold';
  if (compositeScore >= bands.buy_threshold) return 'buy';
  if (compositeScore <= bands.sell_threshold) return 'sell';
  return 'hold';
}

module.exports = {
  interpolateLevelScore,
  calibrateToRange,
  computeSlope,
  localCurveGradient,
  trajectoryMultiplier,
  scoreIndicator,
  evaluateStock,
  assignSignal,
  linearInterp,
};
