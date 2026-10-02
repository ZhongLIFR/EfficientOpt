from __future__ import annotations

import json
from time import perf_counter

from common_model import build_factors, cp_norm_squared, load_data, objective_from_target_norm


def solve() -> dict:
    data = load_data()
    a, b, c = build_factors(data)
    ridge_lambda = float(data["ridge_lambda"])
    customers = len(a)
    products = len(b)
    weeks = len(c)
    rank = int(data["rank"])
    start = perf_counter()
    target_norm_sq = cp_norm_squared(a, b, c)
    objective = objective_from_target_norm(target_norm_sq, ridge_lambda)
    solution_norm_sq = target_norm_sq / ((1.0 + ridge_lambda) ** 2)
    wall_seconds = perf_counter() - start
    return {
        "objective": objective,
        "solution_norm_sq": solution_norm_sq,
        "solution_checksum": solution_norm_sq / max(1.0, customers * products * weeks),
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": (customers + products + weeks) * rank * rank + rank * rank,
        "iterations": 1,
        "variables": (customers + products + weeks) * rank,
        "constraints": 0,
        "nonzeros": (customers + products + weeks) * rank,
        "method": "cp_factor_gram_shrinkage",
        "structure_preserved": "rank-R CP tensor represented by three factor matrices",
    }


if __name__ == "__main__":
    print(json.dumps(solve(), indent=2))
