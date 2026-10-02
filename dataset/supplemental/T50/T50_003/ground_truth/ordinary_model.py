from __future__ import annotations

import json
from time import perf_counter

from common_model import (
    build_features,
    core_checksum,
    core_index,
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
    normal = [[0.0] * size for _ in range(size)]
    rhs = [0.0] * size
    for i in range(len(a)):
        ai = a[i]
        for j in range(len(b)):
            bj = b[j]
            for k in range(len(c)):
                ck = c[k]
                features = [0.0] * size
                target = 0.0
                for ra in range(rank_region):
                    for rb in range(rank_product):
                        for rc in range(rank_week):
                            idx = core_index(ra, rb, rc, rank_product, rank_week)
                            feature = ai[ra] * bj[rb] * ck[rc]
                            features[idx] = feature
                            target += feature * core_target[ra][rb][rc]
                for u in range(size):
                    fu = features[u]
                    rhs[u] += fu * target
                    row_u = normal[u]
                    for v in range(size):
                        row_u[v] += fu * features[v]
    for u in range(size):
        normal[u][u] += ridge_lambda
    solution = dense_solve(normal, rhs)
    core_solution = unflatten_core(solution, rank_region, rank_product, rank_week)
    ga = gram(a)
    gb = gram(b)
    gc = gram(c)
    objective = objective_from_core(ga, gb, gc, core_solution, core_target, ridge_lambda)
    wall_seconds = perf_counter() - start
    entries = len(a) * len(b) * len(c)
    return {
        "objective": objective,
        "core_checksum": core_checksum(core_solution),
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": entries * size * size,
        "iterations": 1,
        "variables": entries + size,
        "constraints": entries,
        "nonzeros": entries * size,
        "method": "dense_tucker_entrywise_design",
    }


if __name__ == "__main__":
    print(json.dumps(solve(), indent=2))
