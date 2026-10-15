import pandas as pd
import numpy as np
import random

# ── GA Hyperparameters ────────────────────────────────────────────────────────
POPULATION_SIZE = 100
GENERATIONS     = 100
MUTATION_RATE   = 0.25
CROSSOVER_RATE  = 0.8
TOURNAMENT_SIZE = 10

# Window search bounds (inclusive)
SMALL_WIN_MIN, SMALL_WIN_MAX = 10,  100
LARGE_WIN_MIN, LARGE_WIN_MAX = 20, 300


# ── Fitness Function ──────────────────────────────────────────────────────────
def compute_total_return(close: np.ndarray, small_window: int, large_window: int) -> float:
    if small_window >= large_window:
        return float("-inf")

    n = len(close)
    if n < large_window:
        return float("-inf")

    # Vectorised SMAs using cumsum for O(n) computation
    def rolling_mean(arr: np.ndarray, w: int) -> np.ndarray:
        cumsum = np.cumsum(np.insert(arr, 0, 0.0))
        out = np.full(n, np.nan)
        out[w - 1:] = (cumsum[w:] - cumsum[:-w]) / w
        return out

    short_sma = rolling_mean(close, small_window)
    long_sma  = rolling_mean(close, large_window)
    diff      = short_sma - long_sma

    # Crossover detection: +1 = crossed above (buy), -1 = crossed below (sell)
    above      = (diff > 0).astype(np.int8)
    above_prev = np.roll(above, 1)
    above_prev[0] = above[0]          # no signal on first bar

    buy_mask  = (above == 1) & (above_prev == 0)
    sell_mask = (above == 0) & (above_prev == 1)

    # Discard bars before both SMAs are valid
    valid_from = large_window - 1
    buy_mask[:valid_from]  = False
    sell_mask[:valid_from] = False

    buy_indices  = np.where(buy_mask)[0]
    sell_indices = np.where(sell_mask)[0]

    if len(buy_indices) == 0 or len(sell_indices) == 0:
        return float("-inf")

    # Match each buy to the next sell that follows it
    total      = 0.0
    in_position = False
    entry_price = 0.0

    bi, si = 0, 0
    while bi < len(buy_indices) and si < len(sell_indices):
        if not in_position:
            entry_price = close[buy_indices[bi]]
            in_position = True
            bi += 1
        else:
            # Advance sell pointer until it's after the entry bar
            entry_bar = buy_indices[bi - 1]
            while si < len(sell_indices) and sell_indices[si] <= entry_bar:
                si += 1
            if si >= len(sell_indices):
                break
            total      += close[sell_indices[si]] - entry_price
            in_position = False
            si += 1

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
    # Extract once; every fitness call receives a lightweight numpy array
    close = df["Close"].to_numpy(dtype=np.float64)

    population = [random_individual() for _ in range(POPULATION_SIZE)]
    best_individual, best_fitness = None, float("-inf")

    for generation in range(1, GENERATIONS + 1):
        fitnesses = [compute_total_return(close, ind["small"], ind["large"]) for ind in population]

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

    df = pd.read_csv("data/bitcoin.csv")

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