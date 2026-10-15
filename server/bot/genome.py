from dataclasses import dataclass, field
import random
import json, os, io

# ---------------------------------------------------------------------------
# Hardcoded ideal values & user-configurable directions
# ---------------------------------------------------------------------------

INDICATOR_CONFIG: dict[str, dict] = {
    "epsCurrentYear": {
        "ideal": 4.5,          # Positive earnings per share
        "direction": 1,        # Higher is better
    },
    "pegRatio": {
        "ideal": 1.0,          # PEG of 1 = fairly valued
        "direction": -1,       # Higher above ideal is worse (overvalued)
    },
    "priceToSalesTrailing12Months": {
        "ideal": 2.0,          # Reasonable P/S ratio
        "direction": -1,       # Higher is worse
    },
    "priceToBook": {
        "ideal": 1.5,          # Near book value
        "direction": -1,       # Higher is worse (more expensive relative to book)
    },
    "debtToEquity": {
        "ideal": 50.0,         # 50% D/E ratio
        "direction": -1,       # Higher is worse
    },
    "bookValue": {
        "ideal": None,         # Computed dynamically as current_price * 0.85
        "direction": 1,        # Lower book value vs current price is better
    },
    "targetMeanPrice": {
        "ideal": None,         # Computed dynamically as current_price * 1.15
        "direction": 1,        # Higher analyst target vs current price is better
    },
    "freeCashflow": {
        "ideal": 0.1,          # Free cash flow is at least 10% of market cap
        "direction": 1,        # Higher free cash flow vs market cap is better
    },
    "returnOnEquity": {
        "ideal": 0.15,         # 15% is healthy, too high can be good or bad
        "direction": 1,        # Higher ROE is generally good
    },
}

# ---------------------------------------------------------------------------
# Genome definition
# ---------------------------------------------------------------------------

# Sentinels used to distinguish "caller supplied a value" from "randomise it"
_RANDOM_INT = object()
_RANDOM_FLOAT = object()

@dataclass
class Genome:
    """Represents one individual in the genetic algorithm population.

    Scalar parameters use sentinel defaults so that a bare ``Genome()``
    randomises every parameter, while ``Genome(reversion_window=60)``
    pins that parameter and randomises the rest.  This ensures crossover
    (which constructs a new ``Genome`` and then sets fields) always
    produces fully-randomised children before field assignment.
    """

    # Per-indicator weights (0–1) and penalty scales (0.05–5.0)
    indicator_weights: dict[str, float] = field(default_factory=dict)
    indicator_penalty_scales: dict[str, float] = field(default_factory=dict)

    # Mean-reversion parameters (GA-optimized)
    reversion_window: object = field(default_factory=lambda: _RANDOM_INT)
    reversion_weight: object = field(default_factory=lambda: _RANDOM_FLOAT)

    # Signal classification threshold (GA-optimized)
    # Scores with |score| >= signal_threshold => BUY / SELL; otherwise HOLD
    signal_threshold: object = field(default_factory=lambda: _RANDOM_FLOAT)

    def __post_init__(self):
        # Indicator dicts
        for key in INDICATOR_CONFIG:
            if key not in self.indicator_weights:
                self.indicator_weights[key] = random.random()
            if key not in self.indicator_penalty_scales:
                self.indicator_penalty_scales[key] = random.uniform(0.05, 5.0)

        # Scalar parameters — randomise if sentinel, clamp if caller-supplied
        if self.reversion_window is _RANDOM_INT:
            self.reversion_window = random.randint(10, 120)
        else:
            self.reversion_window = max(5, min(252, int(self.reversion_window)))

        if self.reversion_weight is _RANDOM_FLOAT:
            self.reversion_weight = random.uniform(0.05, 0.6)
        else:
            self.reversion_weight = max(0.0, min(1.0, float(self.reversion_weight)))

        if self.signal_threshold is _RANDOM_FLOAT:
            self.signal_threshold = random.uniform(0.05, 0.5)
        else:
            self.signal_threshold = max(0.0, min(1.0, float(self.signal_threshold)))

    def classify(self, score: float) -> str:
        # Return BUY / HOLD / SELL for a score using this genome's threshold.
        if score >= self.signal_threshold:
            return "BUY"
        if score <= -self.signal_threshold:
            return "SELL"
        return "HOLD"

    def copy(self) -> "Genome":
        return Genome(
            indicator_weights={k: v for k, v in self.indicator_weights.items()},
            indicator_penalty_scales={k: v for k, v in self.indicator_penalty_scales.items()},
            reversion_window=self.reversion_window,
            reversion_weight=self.reversion_weight,
            signal_threshold=self.signal_threshold,
        )
    
    def save(self):
        data = {
            "indicator_weights": self.indicator_weights,
            "indicator_penalty_scales": self.indicator_penalty_scales,
            "reversion_window": self.reversion_window,
            "reversion_weight": self.reversion_weight,
            "signal_threshold": self.signal_threshold,
        }
        with io.open(os.path.join('output','_genome.json'), 'w') as f:
            f.write(json.dumps({}))
        with open("output/_genome.json", "w") as f:
            json.dump(data, f, indent=2)