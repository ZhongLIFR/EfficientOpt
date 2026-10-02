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
    unflatten_core,
)


def solve() -> dict:
    data = load_data()
    a, b, c, core_target = build_features(data)
    ridge_lambda = float(data["ridge_lambda"])
    rank_region = int(data["rank_region"])
    rank_product = int(data["rank_product"])
    rank_week = int(data["rank_week"])
    size = rank_region * rank_product * rank_week
    start = perf_counter()
    ga = gram(a)
    gb = gram(b)
    gc = gram(c)
    normal, rhs = build_structured_system(ga, gb, gc, core_target, ridge_lambda)
    solution = dense_solve(normal, rhs)
    core_solution = unflatten_core(solution, rank_region, rank_product, rank_week)
    objective = objective_from_core(ga, gb, gc, core_solution, core_target, ridge_lambda)
    wall_seconds = perf_counter() - start
    return {
        "objective": objective,
        "core_checksum": core_checksum(core_solution),
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": (len(a) * rank_region * rank_region + len(b) * rank_product * rank_product + len(c) * rank_week * rank_week) + size**3,
        "iterations": 1,
        "variables": size,
        "constraints": 0,
        "nonzeros": size * size,
        "method": "tucker_core_gram_normal_equation",
        "structure_preserved": "Tucker tensor form with three factor matrices and a small core tensor",
    }


if __name__ == "__main__":
    print(json.dumps(solve(), indent=2))
