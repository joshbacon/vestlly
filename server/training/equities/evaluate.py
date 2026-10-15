import math
from genome import Genome, INDICATOR_CONFIG
from data import load_local_data, load_labeled_sample

# ---------------------------------------------------------------------------
# Scoring function
# ---------------------------------------------------------------------------

def sigmoid(x: float) -> float:
    """Maps any real number to (-1, +1)."""
    return 2.0 / (1.0 + math.exp(-x)) - 1.0


def compute_indicator_signal(
    value: float,
    ideal: float,
    direction: int,
    penalty_scale: float,
) -> float:
    """
    Returns a signal in [-1, +1] for a single indicator.

    direction = +1 : being above ideal is positive
    direction = -1 : being above ideal is negative
    penalty_scale  : steepness of the penalty for deviation from ideal
    """
    # print(f"value: {value}, ideal: {ideal}, direction: {direction}, penalty: {penalty_scale}")
    deviation = (value - ideal) / (abs(ideal) + 1e-9)  # normalised deviation
    raw = direction * deviation * penalty_scale
    return sigmoid(raw)


def score_stock(genome: Genome, stock_data: dict) -> float:
    """
    Score a single stock using the given genome.
    Returns a float in [-1, +1].
    """
    # print(stock_data)
    info = stock_data["info"]
    # print(f"THIS IS THE INFO LOOK HERE THISIS IT {info}")
    history = stock_data["history"]
    # print(f"SAME WITH THE HISTORY LOOK HERE THISIS IT {history}")
    currentPrice = stock_data["currentPrice"]
    # print(f"LASTLY IT\'S THE PRICE THIS IS HERE {currentPrice}")

    signals: list[float] = []
    total_weight: float = 0.0

    for indicator, cfg in INDICATOR_CONFIG.items():
        raw_value = info.get(indicator)

        if raw_value is None or not isinstance(raw_value, (int, float)):
            continue

        if indicator == "freeCashflow":
            value = raw_value / info.get("marketCap")
        else:
            value = float(raw_value)

        # Dynamic ideal for bookValue
        if indicator == "bookValue" and currentPrice is not None:
            ideal = currentPrice * 0.85  # 15% downside as ideal analyst target
        else:
            ideal = cfg["ideal"]
            if ideal is None:
                continue

        # Dynamic ideal for targetMeanPrice
        if indicator == "targetMeanPrice" and currentPrice is not None:
            ideal = currentPrice * 1.15   # 15% upside as ideal analyst target
        else:
            ideal = cfg["ideal"]
            if ideal is None:
                continue

        direction = cfg["direction"]
        penalty_scale = genome.indicator_penalty_scales[indicator]
        weight = genome.indicator_weights[indicator]

        signal = compute_indicator_signal(value, ideal, direction, penalty_scale)
        signals.append(signal * weight)
        total_weight += weight

    # Mean-reversion signal
    reversion_signal = 0.0
    if history is not None and currentPrice is not None:
        window = max(5, min(genome.reversion_window, len(history)))
        recent = history.iloc[-window:]
        mean_price = float(recent.mean())
        std_price = float(recent.std()) + 1e-9
        z_score = (currentPrice - mean_price) / std_price
        # Negative z-score (below mean) => buy signal; positive => sell signal
        reversion_signal = sigmoid(-z_score * genome.reversion_weight * 2)

    # Combine indicator signals and reversion signal
    indicator_score = sum(signals) / (total_weight + 1e-9) if total_weight > 0 else 0.0
    rw = max(0.0, min(1.0, genome.reversion_weight))
    final_score = (1.0 - rw) * indicator_score + rw * reversion_signal

    return max(-1.0, min(1.0, final_score))


# ---------------------------------------------------------------------------
# Convenience wrapper — score a single stock with a pre-optimised genome
# ---------------------------------------------------------------------------

def analyze_stock(ticker: dict, genome: Genome) -> dict:
    """
    Score a single ticker using an already-optimised genome.

    Returns
    -------
    dict with keys: ticker, score (-1 to +1), signal (BUY / HOLD / SELL)
    """
    # print("loading data")
    # sd = load_local_data(ticker)

    sd = load_labeled_sample(ticker)
    # print(sd)
    # print("scoring stocks")
    score = score_stock(genome, sd)
    return {"ticker": ticker['ticker'], "score": round(score, 4), "signal": genome.classify(score)}