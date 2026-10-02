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
    d, p, budget = build_arrays(data)
    n = len(d)
    start = perf_counter()
    free = list(range(n))
    x = [0.0] * n
    work = 0
    active_set_passes = 0
    while True:
        active_set_passes += 1
        m = len(free)
        matrix = [[0.0] * (m + 1) for _ in range(m + 1)]
        rhs = [0.0] * (m + 1)
        for local, idx in enumerate(free):
            matrix[local][local] = d[idx]
            matrix[local][m] = 1.0
            matrix[m][local] = 1.0
            rhs[local] = d[idx] * p[idx]
        rhs[m] = budget
        solution = dense_solve(matrix, rhs)
        work += (m + 1) ** 3
        negative = [idx for local, idx in enumerate(free) if solution[local] < -1e-10]
        if not negative:
            for local, idx in enumerate(free):
                x[idx] = max(0.0, solution[local])
            break
        negative_set = set(negative)
        free = [idx for idx in free if idx not in negative_set]
    wall_seconds = perf_counter() - start
    return {
        "objective": objective(d, p, x),
        "allocation": x,
        "total_allocation": sum(x),
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": work,
        "iterations": active_set_passes,
        "variables": n + 1,
        "constraints": n + 1,
        "nonzeros": 3 * n,
        "method": "dense_active_set_kkt",
    }


if __name__ == "__main__":
    result = solve()
    result.pop("allocation")
    print(json.dumps(result, indent=2))
