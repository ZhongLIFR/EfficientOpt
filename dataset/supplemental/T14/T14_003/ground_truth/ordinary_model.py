from __future__ import annotations

import json
from time import perf_counter

from common_model import build_arrays, load_data, objective_from_shared


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
    a, b = build_arrays(data)
    sites = int(data["sites"])
    features = int(data["features"])
    z = [0.0] * features
    start = perf_counter()
    for j in range(features):
        n = 2 * sites + 1
        matrix = [[0.0] * n for _ in range(n)]
        rhs = [0.0] * n
        z_index = sites
        lambda_offset = sites + 1
        for k in range(sites):
            matrix[k][k] = a[k][j]
            matrix[k][lambda_offset + k] = 1.0
            rhs[k] = a[k][j] * b[k][j]
        for k in range(sites):
            matrix[z_index][lambda_offset + k] = -1.0
        for k in range(sites):
            row = lambda_offset + k
            matrix[row][k] = 1.0
            matrix[row][z_index] = -1.0
        solution = dense_solve(matrix, rhs)
        z[j] = solution[z_index]
    wall_seconds = perf_counter() - start
    objective = objective_from_shared(a, b, z)
    return {
        "objective": objective,
        "shared_coefficients": z,
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": features * (2 * sites + 1) ** 3,
        "iterations": features,
        "variables": features * (2 * sites + 1),
        "constraints": features * (sites + 1),
        "nonzeros": features * (4 * sites),
        "method": "centralized_dense_kkt",
    }


if __name__ == "__main__":
    result = solve()
    result.pop("shared_coefficients")
    print(json.dumps(result, indent=2))
