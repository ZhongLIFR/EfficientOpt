from __future__ import annotations

import json
import math
from pathlib import Path


def load_data() -> dict:
    return json.loads(Path("instance.json").read_text(encoding="utf-8"))


def build_features(data: dict) -> tuple[list[list[float]], list[list[float]], list[list[float]], list[list[list[float]]]]:
    regions = int(data["regions"])
    products = int(data["products"])
    weeks = int(data["weeks"])
    rank_region = int(data["rank_region"])
    rank_product = int(data["rank_product"])
    rank_week = int(data["rank_week"])
    a = []
    for i in range(regions):
        a.append([
            0.65 * math.sin((i + 2) * (ra + 1) * 0.023)
            + 0.33 * math.cos((i + 1) * (ra + 3) * 0.010)
            + 0.02 * (i % 5)
            for ra in range(rank_region)
        ])
    b = []
    for j in range(products):
        b.append([
            0.58 * math.cos((j + 4) * (rb + 2) * 0.019)
            + 0.27 * math.sin((j + 1) * (rb + 1) * 0.014)
            - 0.017 * (j % 6)
            for rb in range(rank_product)
        ])
    c = []
    for k in range(weeks):
        c.append([
            0.61 * math.sin((k + 3) * (rc + 2) * 0.021)
            + 0.21 * math.cos((k + 5) * (rc + 1) * 0.008)
            + 0.012 * (k % 4)
            for rc in range(rank_week)
        ])
    core = []
    for ra in range(rank_region):
        core_ab = []
        for rb in range(rank_product):
            core_ab.append([
                0.45 * math.sin((ra + 1) * (rb + 2) * (rc + 1))
                + 0.25 * math.cos((ra + 2) * (rb + 1) * (rc + 3))
                for rc in range(rank_week)
            ])
        core.append(core_ab)
    return a, b, c, core


def gram(factors: list[list[float]]) -> list[list[float]]:
    rank = len(factors[0])
    result = [[0.0] * rank for _ in range(rank)]
    for row in factors:
        for p in range(rank):
            vp = row[p]
            for q in range(rank):
                result[p][q] += vp * row[q]
    return result


def flatten_core(core: list[list[list[float]]]) -> list[float]:
    return [value for plane in core for row in plane for value in row]


def unflatten_core(values: list[float], rank_region: int, rank_product: int, rank_week: int) -> list[list[list[float]]]:
    out = []
    idx = 0
    for _ in range(rank_region):
        plane = []
        for _ in range(rank_product):
            plane.append(values[idx : idx + rank_week])
            idx += rank_week
        out.append(plane)
    return out


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


def core_index(a: int, b: int, c: int, rank_product: int, rank_week: int) -> int:
    return (a * rank_product + b) * rank_week + c


def build_structured_system(
    ga: list[list[float]],
    gb: list[list[float]],
    gc: list[list[float]],
    core_target: list[list[list[float]]],
    ridge_lambda: float,
) -> tuple[list[list[float]], list[float]]:
    rank_region = len(ga)
    rank_product = len(gb)
    rank_week = len(gc)
    size = rank_region * rank_product * rank_week
    target_flat = flatten_core(core_target)
    normal = [[0.0] * size for _ in range(size)]
    rhs = [0.0] * size
    for a1 in range(rank_region):
        for b1 in range(rank_product):
            for c1 in range(rank_week):
                row = core_index(a1, b1, c1, rank_product, rank_week)
                for a2 in range(rank_region):
                    for b2 in range(rank_product):
                        for c2 in range(rank_week):
                            col = core_index(a2, b2, c2, rank_product, rank_week)
                            value = ga[a1][a2] * gb[b1][b2] * gc[c1][c2]
                            normal[row][col] = value
                            rhs[row] += value * target_flat[col]
                normal[row][row] += ridge_lambda
    return normal, rhs


def objective_from_core(
    ga: list[list[float]],
    gb: list[list[float]],
    gc: list[list[float]],
    core_solution: list[list[list[float]]],
    core_target: list[list[list[float]]],
    ridge_lambda: float,
) -> float:
    rank_region = len(ga)
    rank_product = len(gb)
    rank_week = len(gc)
    solution_flat = flatten_core(core_solution)
    target_flat = flatten_core(core_target)
    residual_norm = 0.0
    for a1 in range(rank_region):
        for b1 in range(rank_product):
            for c1 in range(rank_week):
                idx1 = core_index(a1, b1, c1, rank_product, rank_week)
                diff1 = solution_flat[idx1] - target_flat[idx1]
                for a2 in range(rank_region):
                    for b2 in range(rank_product):
                        for c2 in range(rank_week):
                            idx2 = core_index(a2, b2, c2, rank_product, rank_week)
                            diff2 = solution_flat[idx2] - target_flat[idx2]
                            residual_norm += diff1 * ga[a1][a2] * gb[b1][b2] * gc[c1][c2] * diff2
    ridge_norm = sum(value * value for value in solution_flat)
    return 0.5 * residual_norm + 0.5 * ridge_lambda * ridge_norm


def core_checksum(core_solution: list[list[list[float]]]) -> float:
    total = 0.0
    for a, plane in enumerate(core_solution):
        for b, row in enumerate(plane):
            for c, value in enumerate(row):
                total += (a + 1) * (b + 2) * (c + 3) * value
    return total
