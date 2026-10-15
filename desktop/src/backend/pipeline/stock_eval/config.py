"""
Central configuration for the stock evaluation fitting pipeline.

This file is the single source of truth for the structural decisions made
during design: forward-return horizon, data split ratios, per-indicator
scale classification (for cross-sectional normalization before sector
pooling), and candidate trajectory windows. Keeping these here (rather than
scattered as magic numbers through the pipeline stages) makes the pipeline's
assumptions auditable at a glance.
"""

from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Global parameters
# ---------------------------------------------------------------------------

# Forward-return horizon in trading days. This is a property of the
# strategy (intended holding period), fixed globally, and used to build
# the label for every indicator's Stage 1 lookup table.
FORWARD_RETURN_HORIZON_DAYS = 30

# Three-way split fractions (fit / weight-fit / test), applied walk-forward
# in time (i.e. fit is the earliest slice, test is the most recent).
SPLIT_FIT_FRAC = 0.5
SPLIT_WEIGHT_FIT_FRAC = 0.25
SPLIT_TEST_FRAC = 0.25

# Within the fit set, the further split used for Stage 5 (trajectory
# window N selection), to keep N-selection from contaminating the
# weight-fit / test sets.
N_SEARCH_FRAC_OF_FIT = 0.6  # remaining (1 - this) is the N-confirm slice

# Number of bins used to build each indicator's Stage 1 lookup table.
LOOKUP_TABLE_BINS = 25

# Smoothing window (in bins) applied to the lookup table after binning.
LOOKUP_TABLE_SMOOTHING_WINDOW = 3

# Candidate trajectory windows (in trading days) tested per indicator in
# Stage 5. Actual chosen N is validated per-indicator, not assumed.
CANDIDATE_N_WINDOWS = [3, 5, 10, 20, 40, 60]

# Fallback N used if Stage 5 validation fails to find an N that holds up
# out-of-sample (i.e. improvement doesn't generalize from search -> confirm
# slice). Deliberately mid-range and conservative.
DEFAULT_FALLBACK_N = 10

# Minimum number of samples required in a lookup-table bin before it's
# trusted; sparser bins get pulled toward smoothed neighbors more heavily.
MIN_SAMPLES_PER_BIN = 20


class ScaleType(str, Enum):
    """
    Whether an indicator's raw values are directly comparable across
    stocks of different price levels, or need normalization before being
    pooled into a single sector-level lookup table.

    SCALE_INDEPENDENT: already bounded/ratio-based (e.g. RSI, %B, stochastic).
    SCALE_DEPENDENT: in price units; must be normalized (e.g. as % of price,
        or divided by a volatility measure like ATR) before pooling.
    """
    SCALE_INDEPENDENT = "scale_independent"
    SCALE_DEPENDENT = "scale_dependent"


@dataclass(frozen=True)
class IndicatorSpec:
    """Declarative definition of one indicator for the pipeline."""

    name: str
    scale_type: ScaleType
    # How the trajectory ("moving toward ideal") should be interpreted:
    # for most oscillators a positive slope simply means "value went up",
    # and whether that's "toward" or "away" from ideal depends on the
    # fitted curve, so this is resolved at scoring time. Kept here only
    # as documentation / validation hook for now.
    description: str = ""


# Starter indicator set. Extend this as you add more indicators -- the
# rest of the pipeline is generic and reads this list, not indicator names
# hardcoded elsewhere.
INDICATOR_SPECS: list[IndicatorSpec] = [
    IndicatorSpec(
        name="rsi_14",
        scale_type=ScaleType.SCALE_INDEPENDENT,
        description="14-period Relative Strength Index, bounded 0-100.",
    ),
    IndicatorSpec(
        name="stoch_k_14",
        scale_type=ScaleType.SCALE_INDEPENDENT,
        description="14-period stochastic %K, bounded 0-100.",
    ),
    IndicatorSpec(
        name="bb_percent_b_20",
        scale_type=ScaleType.SCALE_INDEPENDENT,
        description="Bollinger %B (20-period): position within bands, "
                     "typically 0-1 but can exceed on breakouts.",
    ),
    IndicatorSpec(
        name="macd_hist_norm",
        scale_type=ScaleType.SCALE_DEPENDENT,
        description="MACD histogram (12/26/9), normalized by price before "
                     "pooling since raw MACD is in price units.",
    ),
    IndicatorSpec(
        name="sma_dist_50",
        scale_type=ScaleType.SCALE_DEPENDENT,
        description="Distance of price from its 50-day SMA, normalized as "
                     "a percentage of price before pooling.",
    ),
]


@dataclass(frozen=True)
class UniverseConfig:
    """
    Encodes the scoped-down decision on universe construction:
    US sector universes use point-in-time, survivorship-bias-free
    constituents; Canadian (TSX) universes use current constituents only,
    as a known, explicitly-flagged limitation (see design discussion).
    """
    market: str  # "US" or "CA"
    survivorship_bias_free: bool
    source: str  # human-readable description of how the universe was built


US_UNIVERSE = UniverseConfig(
    market="US",
    survivorship_bias_free=True,
    source="Point-in-time S&P family constituents (e.g. EODHD historical "
           "components), includes delisted tickers.",
)

CA_UNIVERSE = UniverseConfig(
    market="CA",
    survivorship_bias_free=False,
    source="Current TSX sector constituents only. KNOWN LIMITATION: "
           "no point-in-time membership history available yet; "
           "delisted/failed constituents are excluded from fitting, "
           "which likely makes fitted thresholds look somewhat better "
           "than they would with full history. Revisit if this market "
           "proves out.",
)
