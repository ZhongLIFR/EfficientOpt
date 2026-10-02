from __future__ import annotations

import json
from time import perf_counter

from common_model import build_arrays, load_data, objective


def dense_solve(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(b)
    for i in range(n):
        pivot = i
        pivot_abs = abs(a[i][i])
        for r in range(i + 1, n):
            value = abs(a[r][i])
            if value > pivot_abs:
                pivot = r
                pivot_abs = value
        if pivot != i:
            a[i], a[pivot] = a[pivot], a[i]
            b[i], b[pivot] = b[pivot], b[i]
        inv = 1.0 / a[i][i]
        row_i = a[i]
        for j in range(i, n):
            row_i[j] *= inv
        b[i] *= inv
        for r in range(n):
            if r == i:
                continue
            factor = a[r][i]
            if factor == 0.0:
                continue
            row_r = a[r]
            for j in range(i, n):
                row_r[j] -= factor * row_i[j]
            b[r] -= factor * b[i]
    return b


def solve() -> dict:
    data = load_data()
    d, p, demand = build_arrays(data)
    microgrids = int(data["microgrids"])
    periods = int(data["periods"])
    n_x = microgrids * periods
    n = n_x + microgrids
    matrix = [[0.0] * n for _ in range(n)]
    rhs = [0.0] * n
    for g in range(microgrids):
        lambda_index = n_x + g
        for t in range(periods):
            idx = g * periods + t
            matrix[idx][idx] = d[g][t]
            matrix[idx][lambda_index] = 1.0
            matrix[lambda_index][idx] = 1.0
            rhs[idx] = d[g][t] * p[g][t]
        rhs[lambda_index] = demand[g]
    start = perf_counter()
    solution = dense_solve(matrix, rhs)
    wall_seconds = perf_counter() - start
    x = [[solution[g * periods + t] for t in range(periods)] for g in range(microgrids)]
    return {
        "objective": objective(d, p, x),
        "generation": x,
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": n**3,
        "iterations": 1,
        "variables": n,
        "constraints": microgrids,
        "nonzeros": 3 * n_x,
        "method": "dense_global_kkt",
    }


if __name__ == "__main__":
    result = solve()
    result.pop("generation")
    print(json.dumps(result, indent=2))
