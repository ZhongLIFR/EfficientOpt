from __future__ import annotations

import json
from time import perf_counter

from common_model import build_arrays, load_data, objective, sparse_dual_solution


def solve() -> dict:
    data = load_data()
    d, p, budget = build_arrays(data)
    start = perf_counter()
    x = sparse_dual_solution(d, p, budget)
    wall_seconds = perf_counter() - start
    n = len(d)
    return {
        "objective": objective(d, p, x),
        "allocation": x,
        "total_allocation": sum(x),
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": 90 * n,
        "iterations": 90,
        "variables": n,
        "constraints": 1,
        "nonzeros": n,
        "method": "diagonal_cone_dual_search",
        "structure_preserved": "diagonal Hessian, single equality, nonnegative cone",
    }


if __name__ == "__main__":
    result = solve()
    result.pop("allocation")
    print(json.dumps(result, indent=2))
