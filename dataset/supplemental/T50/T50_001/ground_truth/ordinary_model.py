from __future__ import annotations

import json
from time import perf_counter

from common_model import build_factors, cp_entry, load_data


def solve() -> dict:
    data = load_data()
    a, b, c = build_factors(data)
    ridge_lambda = float(data["ridge_lambda"])
    shrink = 1.0 / (1.0 + ridge_lambda)
    customers = len(a)
    products = len(b)
    weeks = len(c)
    rank = int(data["rank"])
    start = perf_counter()
    objective = 0.0
    solution_norm_sq = 0.0
    checksum = 0.0
    materialized_slices = []
    for i in range(customers):
        customer_slice = []
        for j in range(products):
            row = []
            for k in range(weeks):
                target = cp_entry(a[i], b[j], c[k])
                value = shrink * target
                residual = value - target
                objective += 0.5 * residual * residual + 0.5 * ridge_lambda * value * value
                solution_norm_sq += value * value
                if (i * 131 + j * 29 + k * 7) % 4099 == 0:
                    checksum += value
                row.append(value)
            customer_slice.append(row)
        materialized_slices.append(customer_slice)
    wall_seconds = perf_counter() - start
    return {
        "objective": objective,
        "solution_norm_sq": solution_norm_sq,
        "solution_checksum": checksum,
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": customers * products * weeks * rank,
        "iterations": 1,
        "variables": customers * products * weeks,
        "constraints": 0,
        "nonzeros": customers * products * weeks,
        "method": "dense_full_tensor_cp_shrinkage",
        "materialized_customer_slices": len(materialized_slices),
    }


if __name__ == "__main__":
    print(json.dumps(solve(), indent=2))
