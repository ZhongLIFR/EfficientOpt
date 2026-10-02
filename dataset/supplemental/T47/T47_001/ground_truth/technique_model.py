from __future__ import annotations

import json
from time import perf_counter

from common_model import (
    build_features,
    build_structured_system,
    core_checksum,
    dense_solve,
    gram,
    load_data,
    objective_from_core,
    unflatten,
)


def solve() -> dict:
    data = load_data()
    left, right, core_target = build_features(data)
    ridge_lambda = float(data["ridge_lambda"])
    rank = int(data["rank"])
    size = rank * rank
    start = perf_counter()
    left_gram = gram(left)
    right_gram = gram(right)
    normal, rhs = build_structured_system(left_gram, right_gram, core_target, ridge_lambda)
    solution = dense_solve(normal, rhs)
    core_solution = unflatten(solution, rank)
    objective = objective_from_core(left_gram, right_gram, core_solution, core_target, ridge_lambda)
    wall_seconds = perf_counter() - start
    return {
        "objective": objective,
        "core_checksum": core_checksum(core_solution),
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": (len(left) + len(right)) * rank * rank + size**3,
        "iterations": 1,
        "variables": size,
        "constraints": 0,
        "nonzeros": size * size,
        "method": "gram_matrix_core_normal_equation",
        "structure_preserved": "P C Q^T matrix form with only the small low-rank core optimized",
    }


if __name__ == "__main__":
    print(json.dumps(solve(), indent=2))
