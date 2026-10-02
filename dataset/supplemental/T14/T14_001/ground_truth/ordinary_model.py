from __future__ import annotations

import json
from time import perf_counter

from common_model import build_arrays, load_data, objective_from_consensus


def dense_solve(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(b)
    for i in range(n):
        pivot = i
        pivot_abs = abs(a[i][i])
        for r in range(i + 1, n):
            candidate = abs(a[r][i])
            if candidate > pivot_abs:
                pivot = r
                pivot_abs = candidate
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
    q, p = build_arrays(data)
    regions = int(data["regions"])
    periods = int(data["time_periods"])
    z = [0.0] * periods
    start = perf_counter()
    for h in range(periods):
        n = 2 * regions + 1
        a = [[0.0] * n for _ in range(n)]
        b = [0.0] * n
        z_index = regions
        lambda_offset = regions + 1
        for k in range(regions):
            a[k][k] = q[k][h]
            a[k][lambda_offset + k] = 1.0
            b[k] = q[k][h] * p[k][h]
        for k in range(regions):
            a[z_index][lambda_offset + k] = -1.0
        for k in range(regions):
            row = lambda_offset + k
            a[row][k] = 1.0
            a[row][z_index] = -1.0
        solution = dense_solve(a, b)
        z[h] = solution[z_index]
    wall_seconds = perf_counter() - start
    objective = objective_from_consensus(q, p, z)
    return {
        "objective": objective,
        "consensus_profile": z,
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": periods * (2 * regions + 1) ** 3,
        "iterations": periods,
        "variables": periods * (2 * regions + 1),
        "constraints": periods * (regions + 1),
        "nonzeros": periods * (4 * regions),
        "method": "centralized_dense_kkt",
    }


if __name__ == "__main__":
    result = solve()
    result.pop("consensus_profile")
    print(json.dumps(result, indent=2))
