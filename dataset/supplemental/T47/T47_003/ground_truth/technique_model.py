from __future__ import annotations

import json
from time import perf_counter

from common_model import build_factors, load_data, low_rank_norm_squared, objective_from_target_norm


def solve() -> dict:
    data = load_data()
    left, right = build_factors(data)
    ridge_lambda = float(data["ridge_lambda"])
    stores = len(left)
    products = len(right)
    rank = int(data["rank"])
    start = perf_counter()
    target_norm_sq = low_rank_norm_squared(left, right)
    objective = objective_from_target_norm(target_norm_sq, ridge_lambda)
    solution_norm_sq = target_norm_sq / ((1.0 + ridge_lambda) ** 2)
    wall_seconds = perf_counter() - start
    return {
        "objective": objective,
        "solution_norm_sq": solution_norm_sq,
        "solution_checksum": solution_norm_sq / max(1.0, stores * products),
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": (stores + products) * rank * rank + rank * rank,
        "iterations": 1,
        "variables": (stores + products) * rank,
        "constraints": 0,
        "nonzeros": (stores + products) * rank,
        "method": "low_rank_factor_gram_shrinkage",
        "structure_preserved": "rank-r target represented through two factor matrices and Gram products",
    }


if __name__ == "__main__":
    print(json.dumps(solve(), indent=2))
