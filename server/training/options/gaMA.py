import pandas as pd
import numpy as np
import random

# ── GA Hyperparameters ────────────────────────────────────────────────────────
POPULATION_SIZE = 100
GENERATIONS     = 100
MUTATION_RATE   = 0.3
CROSSOVER_RATE  = 0.8
TOURNAMENT_SIZE = 5

# Window search bounds (inclusive)
SMALL_WIN_MIN, SMALL_WIN_MAX = 8, 100
LARGE_WIN_MIN, LARGE_WIN_MAX = 30, 300


# ── Fitness Function ──────────────────────────────────────────────────────────
def compute_total_return(df_raw: pd.DataFrame, small_window: int, large_window: int) -> float:
    """
    Replicates the original strategy logic and returns total dollar return.
    Returns -inf for invalid window combinations or strategies with no trades.
    """
    if small_window >= large_window:
        return float("-inf")

    hist = df_raw.copy()
    hist["shortSMA"] = hist["Close"].rolling(window=small_window).mean()
    hist["longSMA"]  = hist["Close"].rolling(window=large_window).mean()
    hist["SMAdiff"]  = hist["shortSMA"] - hist["longSMA"]
    hist["SMAoverunder"] = ["over" if b > 0 else "under" for b in hist["SMAdiff"]]
    hist["sma_ou_shift"]  = hist["SMAoverunder"].shift(1)

    signals = []
    for i, b in enumerate(hist["SMAoverunder"]):
        if b == "over"  and hist["sma_ou_shift"].iloc[i] == "under":
            signals.append("buy")
        elif b == "under" and hist["sma_ou_shift"].iloc[i] == "over":
            signals.append("sell")
        else:
            signals.append("hold")

    hist["SMAsignal"] = signals
    hist = hist[hist["SMAsignal"] != "hold"].copy()

    if len(hist) < 2:
        return float("-inf")

    data = hist[::-1]
    total, curr_entry = 0.0, 0.0
    for _, row in data.iterrows():
        if row["SMAsignal"] == "buy":
            curr_entry = row["Close"]
        elif row["SMAsignal"] == "sell" and curr_entry:
            total += row["Close"] - curr_entry
            curr_entry = 0.0

    return total


# ── GA Primitives ─────────────────────────────────────────────────────────────
def random_individual() -> dict:
    small = random.randint(SMALL_WIN_MIN, SMALL_WIN_MAX)
    large = random.randint(LARGE_WIN_MIN, LARGE_WIN_MAX)
    return {"small": small, "large": large}


def tournament_select(population: list, fitnesses: list) -> dict:
    contestants = random.sample(list(zip(population, fitnesses)), TOURNAMENT_SIZE)
    return max(contestants, key=lambda x: x[1])[0]


def crossover(parent_a: dict, parent_b: dict) -> tuple[dict, dict]:
    if random.random() > CROSSOVER_RATE:
        return parent_a.copy(), parent_b.copy()
    child_a = {"small": parent_a["small"], "large": parent_b["large"]}
    child_b = {"small": parent_b["small"], "large": parent_a["large"]}
    return child_a, child_b


def mutate(individual: dict) -> dict:
    ind = individual.copy()
    if random.random() < MUTATION_RATE:
        ind["small"] = random.randint(SMALL_WIN_MIN, SMALL_WIN_MAX)
    if random.random() < MUTATION_RATE:
        ind["large"] = random.randint(LARGE_WIN_MIN, LARGE_WIN_MAX)
    return ind


def clamp(individual: dict) -> dict:
    ind = individual.copy()
    ind["small"] = max(SMALL_WIN_MIN, min(SMALL_WIN_MAX, ind["small"]))
    ind["large"] = max(LARGE_WIN_MIN, min(LARGE_WIN_MAX, ind["large"]))
    return ind


# ── Main GA Loop ──────────────────────────────────────────────────────────────
def run_genetic_algorithm(df: pd.DataFrame) -> dict:
    population = [random_individual() for _ in range(POPULATION_SIZE)]
    best_individual, best_fitness = None, float("-inf")

    for generation in range(1, GENERATIONS + 1):
        fitnesses = [compute_total_return(df, ind["small"], ind["large"]) for ind in population]

        # Track overall best
        gen_best_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
        if fitnesses[gen_best_idx] > best_fitness:
            best_fitness   = fitnesses[gen_best_idx]
            best_individual = population[gen_best_idx].copy()

        if generation % 10 == 0 or generation == 1:
            valid = [f for f in fitnesses if f != float("-inf")]
            avg   = np.mean(valid) if valid else float("nan")
            print(
                f"Gen {generation:>3}/{GENERATIONS} │ "
                f"Best so far: small={best_individual['small']:>3}, "
                f"large={best_individual['large']:>3}, "
                f"return=${best_fitness:,.2f} │ "
                f"Avg valid return=${avg:,.2f}"
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

    return {"small_window": best_individual["small"],
            "large_window": best_individual["large"],
            "total_return": best_fitness}


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)

    df = pd.read_csv("spx_hist.csv")

    print("=" * 65)
    print("  SMA Crossover — Genetic Algorithm Window Optimizer")
    print("=" * 65)
    print(f"  Population: {POPULATION_SIZE}  |  Generations: {GENERATIONS}")
    print(f"  Mutation rate: {MUTATION_RATE}  |  Crossover rate: {CROSSOVER_RATE}")
    print(f"  small_window search: [{SMALL_WIN_MIN}, {SMALL_WIN_MAX}]")
    print(f"  large_window search: [{LARGE_WIN_MIN}, {LARGE_WIN_MAX}]")
    print("=" * 65)

    result = run_genetic_algorithm(df)

    print()
    print("=" * 65)
    print("  OPTIMAL PARAMETERS FOUND")
    print("=" * 65)
    print(f"  small_window = {result['small_window']}")
    print(f"  large_window = {result['large_window']}")
    print(f"  Total return = ${result['total_return']:,.2f}")
    print("=" * 65)