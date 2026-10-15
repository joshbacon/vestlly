"""
Stock Analysis with Genetic Algorithm Parameter Optimization
============================================================
Uses a genetic algorithm to optimize scoring parameters for a set of stocks.
The scoring function returns a value in [-1, +1]:
  +1  => strong buy
   0  => hold
  -1  => strong sell

Indicators optimized:
  - epsCurrentYear
  - pegRatio
  - priceToSalesTrailing12Months
  - priceToBook
  - debtToEquity
  - bookValue
  - targetMeanPrice
  - freeCashflow

Each indicator has:
  - ideal_value      : hardcoded target
  - weight           : how much this indicator contributes to the score (GA-optimized)
  - penalty_scale    : how steeply deviations are penalized (GA-optimized)
  - direction        : +1 if above ideal is good, -1 if above ideal is bad (user-configurable)

Mean-reversion parameters (GA-optimized):
  - reversion_window : lookback period (days) for computing mean price
  - reversion_weight : contribution of price mean-reversion signal to final score

Signal classification parameters (GA-optimized):
  - signal_threshold : score magnitude above which a stock is labelled BUY or SELL
                       (range 0.0-1.0; scores in [-threshold, +threshold] => HOLD)
"""

import random
import math
from typing import Optional
import csv
import pandas as pd

from data import load_local_data, fetch_stock_data
from genome import Genome, INDICATOR_CONFIG
from evaluate import score_stock

# ---------------------------------------------------------------------------
# Fitness evaluation
# ---------------------------------------------------------------------------
LABEL_TO_FLOAT = {"BUY": 1.0, "HOLD": 0.0, "SELL": -1.0}
def evaluate_fitness(genome: Genome, stocks_data: list[dict]) -> float:
    """
    Fitness encourages three properties:
      1. Decisive signals — average |score| should be high.
      2. Stock differentiation — scores should vary across the basket.
      3. Threshold calibration — the signal_threshold should not collapse to 0
         (trivially classifying everything) or balloon to 1 (classifying nothing).
         We penalise extreme threshold values with a mild regularisation term.
    """
    # scores = [score_stock(genome, sd) for sd in stocks_data]

    if not stocks_data:
        return 0.0

    correct = 0
    mse_total = 0.0
    for stock in stocks_data:
        predicted = score_stock(genome, stock)
        predicted_label = genome.classify(predicted)
        target = LABEL_TO_FLOAT[stock['label']]
        
        mse_total += (predicted - target) ** 2
        if predicted_label == stock['label']:
            correct += 1


    mse = mse_total / len(stocks_data)
    accuracy = correct / len(stocks_data)

    weights = list(genome.indicator_weights.values())
    mean_weight = sum(weights) / len(weights)
    weight_penalty = max(0.0, 0.3 - mean_weight)

    reversion_penalty = max(0.0, 0.1 - genome.reversion_weight)

    return (1.0 - mse) * 0.6 + accuracy * 0.4 - weight_penalty - reversion_penalty

    # avg_magnitude = sum(abs(s) for s in scores) / len(scores)

    # # Variance across stocks (reward differentiation)
    # mean_s = sum(scores) / len(scores)
    # variance = sum((s - mean_s) ** 2 for s in scores) / len(scores)

    # # Threshold regularisation: prefer thresholds in (0.1, 0.6)
    # t = genome.signal_threshold
    # threshold_penalty = max(0.0, t - 0.6) + max(0.0, 0.1 - t)

    # fitness = (
    #     0.6 * avg_magnitude
    #     + 0.3 * math.sqrt(variance + 1e-9)
    #     - 0.1 * threshold_penalty
    # )
    # return fitness


# ---------------------------------------------------------------------------
# Genetic algorithm operators
# ---------------------------------------------------------------------------

def crossover(parent_a: Genome, parent_b: Genome) -> Genome:
    """Uniform crossover across all genome parameters."""
    child = Genome.__new__(Genome)  # skip __post_init__; we set everything explicitly

    # Per-indicator params: coin-flip per indicator
    child.indicator_weights = {}
    child.indicator_penalty_scales = {}
    for key in INDICATOR_CONFIG:
        donor = parent_a if random.random() < 0.5 else parent_b
        child.indicator_weights[key] = donor.indicator_weights[key]
        child.indicator_penalty_scales[key] = donor.indicator_penalty_scales[key]

    # Scalar params: arithmetic mean (blend) or random pick
    child.reversion_window = random.choice(
        [parent_a.reversion_window, parent_b.reversion_window]
    )
    child.reversion_weight = (parent_a.reversion_weight + parent_b.reversion_weight) / 2.0
    child.signal_threshold = (parent_a.signal_threshold + parent_b.signal_threshold) / 2.0

    return child


def mutate(genome: Genome, mutation_rate: float = 0.2, mutation_strength: float = 0.3) -> Genome:
    """Gaussian mutation."""
    g = genome.copy()
    for key in INDICATOR_CONFIG:
        if random.random() < mutation_rate:
            g.indicator_weights[key] = max(
                0.15, min(1.0, g.indicator_weights[key] + random.gauss(0, mutation_strength))
            )
        if random.random() < mutation_rate:
            g.indicator_penalty_scales[key] = max(
                0.05, g.indicator_penalty_scales[key] + random.gauss(0, mutation_strength)
            )

    if random.random() < mutation_rate:
        g.reversion_window = max(5, min(252, g.reversion_window + random.randint(-15, 15)))
    if random.random() < mutation_rate:
        g.reversion_weight = max(0.0, min(1.0, g.reversion_weight + random.gauss(0, 0.1)))
    if random.random() < mutation_rate:
        g.signal_threshold = max(0.0, min(1.0, g.signal_threshold + random.gauss(0, 0.05)))

    return g


def tournament_select(population: list[Genome], fitnesses: list[float], k: int = 3) -> Genome:
    contestants = random.sample(list(zip(population, fitnesses)), min(k, len(population)))
    return max(contestants, key=lambda x: x[1])[0]


# ---------------------------------------------------------------------------
# Main GA loop
# ---------------------------------------------------------------------------

def run_genetic_algorithm(
    samples: list[dict],
    validation_fraction: float = 0.2,
    population_size: int = 50,
    generations: int = 30,
    elite_fraction: float = 0.1,
    mutation_rate: float = 0.2,
    verbose: bool = True,
) -> tuple[Genome, dict]:

    random.shuffle(samples)
    split        = int(len(samples) * (1 - validation_fraction))
    train_set    = samples[:split]
    val_set      = samples[split:]

    population   = [Genome() for _ in range(population_size)]
    n_elite      = max(1, int(population_size * elite_fraction))
    best_genome  = None
    best_val_fitness = -float("inf")

    for gen in range(generations):
        # Evaluate on training set
        train_fitnesses = [
            evaluate_fitness(g, train_set) for g in population
        ]

        # Select next generation using training fitness
        sorted_pairs = sorted(
            zip(population, train_fitnesses), key=lambda x: x[1], reverse=True
        )
        new_population = [p.copy() for p, _ in sorted_pairs[:n_elite]]
        while len(new_population) < population_size:
            parent_a = tournament_select(population, train_fitnesses)
            parent_b = tournament_select(population, train_fitnesses)
            child    = crossover(parent_a, parent_b)
            child    = mutate(child, mutation_rate=mutation_rate)
            new_population.append(child)

        # Pick the best genome by VALIDATION fitness (not training)
        # This is what prevents overfitting
        for genome in population:
            vf = evaluate_fitness(genome, val_set)
            if vf > best_val_fitness:
                best_val_fitness = vf
                best_genome      = genome.copy()

        population = new_population

        if verbose and (gen % 5 == 0 or gen == generations - 1):
            best_train = max(train_fitnesses)
            print(
                f"  Gen {gen+1:3d}/{generations}  "
                f"train={best_train:.4f}  val={best_val_fitness:.4f}"
            )

    # Final scores on all samples
    results = []
    for sample in samples:
        score  = score_stock(best_genome, sample)
        signal = best_genome.classify(score)
        results.append({
            "ticker": sample["ticker"],
            "date":   sample["date"],
            "score":  round(score, 4),
            "signal": signal,
            "label":  sample["label"],
            "correct": signal == sample["label"],
        })

    metrics = {
        "val_fitness": round(best_val_fitness, 4),
        "accuracy":    round(sum(r["correct"] for r in results) / len(results), 4),
    }
    return best_genome, metrics

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    FIELDS = [
        "epsCurrentYear",
        "pegRatio",
        "priceToSalesTrailing12Months",
        "priceToBook",
        "debtToEquity",
        "bookValue",
        "targetMeanPrice",
        "freeCashflow",
        "returnOnEquity",
    ]
    TICKERS = []
    with open('./data/labeled.csv', 'r') as f:
        for row in csv.DictReader(f):
            TICKERS.append({
                "ticker": row["ticker"],
                "date": row["date"],
                "label": row["label"],
                "info": eval(row["info"]),
                "currentPrice": float(row["currentPrice"]),
                "history": pd.DataFrame([float(p.lstrip()) for p in row["history"].replace('[', '').replace(']', '').split(",")])
            })
    print("=" * 60)
    print("  Stock Analyzer — Genetic Algorithm Parameter Optimisation")
    print("=" * 60)

    best_genome, results = run_genetic_algorithm(
        samples=TICKERS,
        population_size=100,
        generations=50,
        elite_fraction=0.1,
        mutation_rate=0.25,
        verbose=True,
    )

    best_genome.save()

    print("\n--- Optimised Parameters ---")
    print(f"  Reversion window : {best_genome.reversion_window} days")
    print(f"  Reversion weight : {best_genome.reversion_weight:.3f}")
    print(f"  Signal threshold : ±{best_genome.signal_threshold:.3f}")
    for key in INDICATOR_CONFIG:
        w = best_genome.indicator_weights[key]
        ps = best_genome.indicator_penalty_scales[key]
        print(f"  {key:<38}  weight={w:.3f}  penalty_scale={ps:.3f}")
