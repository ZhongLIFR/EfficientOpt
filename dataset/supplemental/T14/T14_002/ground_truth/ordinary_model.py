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
    q, p, demand = build_arrays(data)
    warehouses = int(data["warehouses"])
    periods = int(data["periods"])
    x_out = [[0.0] * periods for _ in range(warehouses)]
    start = perf_counter()
    for h in range(periods):
        n = 3 * warehouses + 1
        matrix = [[0.0] * n for _ in range(n)]
        rhs = [0.0] * n
        x_offset = 0
        y_offset = warehouses
        mu_offset = 2 * warehouses
        lambda_index = 3 * warehouses
        for k in range(warehouses):
            matrix[x_offset + k][x_offset + k] = q[k][h]
            matrix[x_offset + k][mu_offset + k] = 1.0
            rhs[x_offset + k] = q[k][h] * p[k][h]
            matrix[y_offset + k][mu_offset + k] = -1.0
            matrix[y_offset + k][lambda_index] = 1.0
            row = mu_offset + k
            matrix[row][x_offset + k] = 1.0
            matrix[row][y_offset + k] = -1.0
            matrix[lambda_index][y_offset + k] = 1.0
        rhs[lambda_index] = demand[h]
        solution = dense_solve(matrix, rhs)
        for k in range(warehouses):
            x_out[k][h] = solution[y_offset + k]
    wall_seconds = perf_counter() - start
    return {
        "objective": objective(q, p, x_out),
        "shipments": x_out,
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": periods * (3 * warehouses + 1) ** 3,
        "iterations": periods,
        "variables": periods * (3 * warehouses + 1),
        "constraints": periods * (2 * warehouses + 1),
        "nonzeros": periods * (7 * warehouses),
        "method": "centralized_copied_variable_dense_kkt",
    }


if __name__ == "__main__":
    result = solve()
    result.pop("shipments")
    print(json.dumps(result, indent=2))
