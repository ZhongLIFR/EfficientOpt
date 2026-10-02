from __future__ import annotations

import json
from time import perf_counter

from common_model import (
    build_features,
    core_checksum,
    dense_solve,
    flatten,
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
    segments = len(left)
    items = len(right)
    start = perf_counter()
    normal = [[0.0] * size for _ in range(size)]
    rhs = [0.0] * size
    for i in range(segments):
        p = left[i]
        for j in range(items):
            q = right[j]
            features = []
            target = 0.0
            for a in range(rank):
                pa = p[a]
                core_row = core_target[a]
                for b in range(rank):
                    feature = pa * q[b]
                    features.append(feature)
                    target += feature * core_row[b]
            for u in range(size):
                fu = features[u]
                rhs[u] += fu * target
                normal_row = normal[u]
                for v in range(size):
                    normal_row[v] += fu * features[v]
    for u in range(size):
        normal[u][u] += ridge_lambda
    solution = dense_solve(normal, rhs)
    core_solution = unflatten(solution, rank)
    left_gram = gram(left)
    right_gram = gram(right)
    objective = objective_from_core(left_gram, right_gram, core_solution, core_target, ridge_lambda)
    wall_seconds = perf_counter() - start
    return {
        "objective": objective,
        "core_checksum": core_checksum(core_solution),
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": segments * items * size * size,
        "iterations": 1,
        "variables": segments * items + size,
        "constraints": segments * items,
        "nonzeros": segments * items * size,
        "method": "dense_entrywise_design_with_matrix_equalities",
        "core_vector_length": len(flatten(core_solution)),
    }


if __name__ == "__main__":
    print(json.dumps(solve(), indent=2))
