import pandas as pd
import numpy as np
import random

# ── GA Hyperparameters ────────────────────────────────────────────────────────
POPULATION_SIZE = 100
GENERATIONS     = 100
MUTATION_RATE   = 0.25
CROSSOVER_RATE  = 0.8
TOURNAMENT_SIZE = 5

# Gene search bounds (inclusive)
LOOKBACK_MIN      = 10                # rolling window for mean & std
LOOKBACK_MAX      = 120
ENTRY_ZSCORE_MIN  = 0.5              # how many std devs from mean to enter
ENTRY_ZSCORE_MAX  = 3.0
EXIT_ZSCORE_MIN   = 0.0              # how close to mean before exiting
EXIT_ZSCORE_MAX   = 2.0
ZSCORE_STEP       = 0.05             # granularity for z-score genes


# ── Fitness Function ──────────────────────────────────────────────────────────
def compute_total_return(
    close: np.ndarray,
    lookback: int,
    entry_zscore: float,
    exit_zscore: float,
) -> float:
    """
    Mean reversion strategy using a rolling z-score:

      z = (price - rolling_mean) / rolling_std

    Logic:
      - Buy  when z drops below -entry_zscore  (price is cheap vs its mean)
      - Sell when z rises back above -exit_zscore (price has reverted)

    The genome being optimised:
      lookback     : rolling window length for mean/std calculation
      entry_zscore : z-score threshold that triggers a buy  (e.g. -2.0)
      exit_zscore  : z-score threshold that triggers a sell (e.g. -0.5)

    Returns total dollar P&L, or -inf if the parameter combo is degenerate.
    """
    if exit_zscore >= entry_zscore:
        # Exit must be less extreme than entry, otherwise we'd never hold
        return float("-inf")

    n = len(close)
    if n < lookback + 1:
        return float("-inf")

    # ── Vectorised rolling mean and std ──────────────────────────────────────
    # Use cumsum trick for O(n) rolling mean
    cumsum  = np.cumsum(np.insert(close, 0, 0.0))
    rm      = np.full(n, np.nan)
    rm[lookback - 1:] = (cumsum[lookback:] - cumsum[:-lookback]) / lookback

    # Rolling std: E[x²] - E[x]²  (numerically stable for large windows)
    cumsum2 = np.cumsum(np.insert(close ** 2, 0, 0.0))
    rm2     = np.full(n, np.nan)
    rm2[lookback - 1:] = (cumsum2[lookback:] - cumsum2[:-lookback]) / lookback
    rstd    = np.sqrt(np.maximum(rm2 - rm ** 2, 0.0))   # clamp for float noise

    # ── Z-score ───────────────────────────────────────────────────────────────
    with np.errstate(invalid="ignore", divide="ignore"):
        zscore = np.where(rstd > 0, (close - rm) / rstd, np.nan)

    valid_from = lookback  # first bar with a full window
    zscore[:valid_from] = np.nan

    # ── Signal generation ─────────────────────────────────────────────────────
    # Buy  when z crosses below -entry_zscore
    # Sell when z crosses above -exit_zscore  (price has reverted upward)
    buy_mask  = zscore < -entry_zscore
    sell_mask = zscore > -exit_zscore

    # ── Trade matching ────────────────────────────────────────────────────────
    total       = 0.0
    in_position = False
    entry_price = 0.0

    for i in range(valid_from, n):
        if np.isnan(zscore[i]):
            continue
        if not in_position and buy_mask[i]:
            entry_price = close[i]
            in_position = True
        elif in_position and sell_mask[i]:
            total      += close[i] - entry_price
            in_position = False

    if total == 0.0 and not in_position:
        # No completed trades — degenerate individual
        return float("-inf")

    return total


# ── GA Primitives ─────────────────────────────────────────────────────────────
def _rand_zscore(lo: float, hi: float) -> float:
    steps = round((hi - lo) / ZSCORE_STEP)
    return round(lo + random.randint(0, steps) * ZSCORE_STEP, 10)


def random_individual() -> dict:
    return {
        "lookback"    : random.randint(LOOKBACK_MIN, LOOKBACK_MAX),
        "entry_zscore": _rand_zscore(ENTRY_ZSCORE_MIN, ENTRY_ZSCORE_MAX),
        "exit_zscore" : _rand_zscore(EXIT_ZSCORE_MIN,  EXIT_ZSCORE_MAX),
    }


def tournament_select(population: list, fitnesses: list) -> dict:
    contestants = random.sample(list(zip(population, fitnesses)), TOURNAMENT_SIZE)
    return max(contestants, key=lambda x: x[1])[0]


def crossover(parent_a: dict, parent_b: dict) -> tuple[dict, dict]:
    if random.random() > CROSSOVER_RATE:
        return parent_a.copy(), parent_b.copy()
    # Each gene inherited independently from either parent (uniform crossover)
    child_a, child_b = {}, {}
    for gene in ("lookback", "entry_zscore", "exit_zscore"):
        if random.random() < 0.5:
            child_a[gene], child_b[gene] = parent_a[gene], parent_b[gene]
        else:
            child_a[gene], child_b[gene] = parent_b[gene], parent_a[gene]
    return child_a, child_b


def mutate(individual: dict) -> dict:
    ind = individual.copy()
    if random.random() < MUTATION_RATE:
        ind["lookback"]     = random.randint(LOOKBACK_MIN, LOOKBACK_MAX)
    if random.random() < MUTATION_RATE:
        ind["entry_zscore"] = _rand_zscore(ENTRY_ZSCORE_MIN, ENTRY_ZSCORE_MAX)
    if random.random() < MUTATION_RATE:
        ind["exit_zscore"]  = _rand_zscore(EXIT_ZSCORE_MIN,  EXIT_ZSCORE_MAX)
    return ind


def clamp(individual: dict) -> dict:
    ind = individual.copy()
    ind["lookback"]     = max(LOOKBACK_MIN,     min(LOOKBACK_MAX,     ind["lookback"]))
    ind["entry_zscore"] = max(ENTRY_ZSCORE_MIN, min(ENTRY_ZSCORE_MAX, ind["entry_zscore"]))
    ind["exit_zscore"]  = max(EXIT_ZSCORE_MIN,  min(EXIT_ZSCORE_MAX,  ind["exit_zscore"]))
    return ind


# ── Main GA Loop ──────────────────────────────────────────────────────────────
def run_genetic_algorithm(df: pd.DataFrame) -> dict:
    close = df["Close"].to_numpy(dtype=np.float64)

    population = [random_individual() for _ in range(POPULATION_SIZE)]
    best_individual, best_fitness = None, float("-inf")

    for generation in range(1, GENERATIONS + 1):
        fitnesses = [
            compute_total_return(
                close,
                ind["lookback"],
                ind["entry_zscore"],
                ind["exit_zscore"],
            )
            for ind in population
        ]

        gen_best_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
        if fitnesses[gen_best_idx] > best_fitness:
            best_fitness    = fitnesses[gen_best_idx]
            best_individual = population[gen_best_idx].copy()

        if generation % 10 == 0 or generation == 1:
            valid = [f for f in fitnesses if f != float("-inf")]
            avg   = np.mean(valid) if valid else float("nan")
            bi    = best_individual
            print(
                f"Gen {generation:>3}/{GENERATIONS} │ "
                f"Best so far: lookback={bi['lookback']:>3}, "
                f"entry_z={bi['entry_zscore']:.2f}, "
                f"exit_z={bi['exit_zscore']:.2f}, "
                f"return=${best_fitness:,.2f} │ "
                f"Avg valid=${avg:,.2f}"
            )

        # Elitism: carry the best individual forward unchanged
        new_population = [best_individual.copy()]

        while len(new_population) < POPULATION_SIZE:
            parent_a = tournament_select(population, fitnesses)
            parent_b = tournament_select(population, fitnesses)
            child_a, child_b = crossover(parent_a, parent_b)
            new_population.append(clamp(mutate(child_a)))
            if len(new_population) < POPULATION_SIZE:
                new_population.append(clamp(mutate(child_b)))

        population = new_population

    return {
        "lookback"    : best_individual["lookback"],
        "entry_zscore": best_individual["entry_zscore"],
        "exit_zscore" : best_individual["exit_zscore"],
        "total_return": best_fitness,
    }


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)

    # df = pd.read_csv("data/bitcoin.csv")
    df = pd.read_csv("data/bitcoin.csv")
    # df = pd.read_csv("data/ethereum.csv")

    print("=" * 65)
    print("  Mean Reversion — Genetic Algorithm Parameter Optimizer")
    print("=" * 65)
    print(f"  Population: {POPULATION_SIZE}  |  Generations: {GENERATIONS}")
    print(f"  Mutation rate: {MUTATION_RATE}  |  Crossover rate: {CROSSOVER_RATE}")
    print(f"  lookback search:      [{LOOKBACK_MIN}, {LOOKBACK_MAX}]")
    print(f"  entry_zscore search:  [{ENTRY_ZSCORE_MIN}, {ENTRY_ZSCORE_MAX}]")
    print(f"  exit_zscore search:   [{EXIT_ZSCORE_MIN}, {EXIT_ZSCORE_MAX}]")
    print("=" * 65)

    result = run_genetic_algorithm(df)

    print()
    print("=" * 65)
    print("  OPTIMAL PARAMETERS FOUND")
    print("=" * 65)
    print(f"  lookback     = {result['lookback']}")
    print(f"  entry_zscore = {result['entry_zscore']:.2f}")
    print(f"  exit_zscore  = {result['exit_zscore']:.2f}")
    print(f"  Total return = ${result['total_return']:,.2f}")
    print("=" * 65)