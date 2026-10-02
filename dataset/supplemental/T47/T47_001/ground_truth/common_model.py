from __future__ import annotations

import json
import math
from pathlib import Path


def load_data() -> dict:
    return json.loads(Path("instance.json").read_text(encoding="utf-8"))


def build_features(data: dict) -> tuple[list[list[float]], list[list[float]], list[list[float]]]:
    segments = int(data["segments"])
    items = int(data["items"])
    rank = int(data["rank"])
    left = []
    for i in range(segments):
        left.append([
            0.6 * math.sin((i + 2) * (a + 1) * 0.021)
            + 0.4 * math.cos((i + 1) * (a + 3) * 0.009)
            + 0.03 * (i % 4)
            for a in range(rank)
        ])
    right = []
    for j in range(items):
        right.append([
            0.7 * math.cos((j + 4) * (b + 2) * 0.017)
            + 0.2 * math.sin((j + 1) * (b + 1) * 0.012)
            - 0.025 * (j % 5)
            for b in range(rank)
        ])
    core = []
    for a in range(rank):
        core.append([
            0.8 * math.sin((a + 1) * (b + 2)) + 0.35 * math.cos((a + 2) * (b + 1))
            for b in range(rank)
        ])
    return left, right, core


def gram(factors: list[list[float]]) -> list[list[float]]:
    rank = len(factors[0])
    result = [[0.0] * rank for _ in range(rank)]
    for row in factors:
        for a in range(rank):
            va = row[a]
            for b in range(rank):
                result[a][b] += va * row[b]
    return result


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


def flatten(matrix: list[list[float]]) -> list[float]:
    return [value for row in matrix for value in row]


def unflatten(values: list[float], rank: int) -> list[list[float]]:
    return [values[i * rank : (i + 1) * rank] for i in range(rank)]


def build_structured_system(
    left_gram: list[list[float]],
    right_gram: list[list[float]],
    core: list[list[float]],
    ridge_lambda: float,
) -> tuple[list[list[float]], list[float]]:
    rank = len(core)
    size = rank * rank
    normal = [[0.0] * size for _ in range(size)]
    rhs = [0.0] * size
    for a in range(rank):
        for b in range(rank):
            row = a * rank + b
            for c in range(rank):
                for d in range(rank):
                    col = c * rank + d
                    normal[row][col] = left_gram[a][c] * right_gram[b][d]
            normal[row][row] += ridge_lambda
            total = 0.0
            for c in range(rank):
                for d in range(rank):
                    total += left_gram[a][c] * core[c][d] * right_gram[d][b]
            rhs[row] = total
    return normal, rhs


def objective_from_core(
    left_gram: list[list[float]],
    right_gram: list[list[float]],
    core_solution: list[list[float]],
    core_target: list[list[float]],
    ridge_lambda: float,
) -> float:
    rank = len(core_solution)
    residual_norm = 0.0
    for a in range(rank):
        for b in range(rank):
            dab = core_solution[a][b] - core_target[a][b]
            for c in range(rank):
                for d in range(rank):
                    dcd = core_solution[c][d] - core_target[c][d]
                    residual_norm += dab * left_gram[a][c] * right_gram[b][d] * dcd
    ridge_norm = sum(value * value for row in core_solution for value in row)
    return 0.5 * residual_norm + 0.5 * ridge_lambda * ridge_norm


def core_checksum(core_solution: list[list[float]]) -> float:
    return sum((i + 1) * (j + 2) * value for i, row in enumerate(core_solution) for j, value in enumerate(row))
