from __future__ import annotations

import json
from time import perf_counter

from common_model import build_factors, dot, load_data


def solve() -> dict:
    data = load_data()
    left, right = build_factors(data)
    ridge_lambda = float(data["ridge_lambda"])
    shrink = 1.0 / (1.0 + ridge_lambda)
    stores = len(left)
    products = len(right)
    rank = int(data["rank"])
    start = perf_counter()
    objective = 0.0
    solution_norm_sq = 0.0
    checksum = 0.0
    dense_solution = []
    for i in range(stores):
        row_values = []
        for j in range(products):
            target = dot(left[i], right[j])
            value = shrink * target
            residual = value - target
            objective += 0.5 * residual * residual + 0.5 * ridge_lambda * value * value
            solution_norm_sq += value * value
            if (i * 113 + j * 19) % 1237 == 0:
                checksum += value
            row_values.append(value)
        dense_solution.append(row_values)
    wall_seconds = perf_counter() - start
    return {
        "objective": objective,
        "solution_norm_sq": solution_norm_sq,
        "solution_checksum": checksum,
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": stores * products * rank,
        "iterations": 1,
        "variables": stores * products,
        "constraints": 0,
        "nonzeros": stores * products,
        "method": "dense_full_matrix_ridge_shrinkage",
        "materialized_rows": len(dense_solution),
    }


if __name__ == "__main__":
    print(json.dumps(solve(), indent=2))
