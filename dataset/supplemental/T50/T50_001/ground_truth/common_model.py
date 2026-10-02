from __future__ import annotations

import json
import math
from pathlib import Path


def load_data() -> dict:
    return json.loads(Path("instance.json").read_text(encoding="utf-8"))


def build_factors(data: dict) -> tuple[list[list[float]], list[list[float]], list[list[float]]]:
    customers = int(data["customers"])
    products = int(data["products"])
    weeks = int(data["weeks"])
    rank = int(data["rank"])
    a = []
    for i in range(customers):
        a.append([
            math.sin((i + 1) * (r + 2) * 0.017)
            + 0.22 * math.cos((i + 3) * (r + 1) * 0.011)
            + 0.015 * (i % 6)
            for r in range(rank)
        ])
    b = []
    for j in range(products):
        b.append([
            math.cos((j + 2) * (r + 1) * 0.013)
            + 0.31 * math.sin((j + 5) * (r + 3) * 0.007)
            - 0.012 * (j % 5)
            for r in range(rank)
        ])
    c = []
    for k in range(weeks):
        c.append([
            math.sin((k + 4) * (r + 2) * 0.019)
            + 0.27 * math.cos((k + 1) * (r + 4) * 0.006)
            + 0.01 * (k % 4)
            for r in range(rank)
        ])
    return a, b, c


def cp_entry(a_row: list[float], b_row: list[float], c_row: list[float]) -> float:
    return sum(a_row[r] * b_row[r] * c_row[r] for r in range(len(a_row)))


def gram(factors: list[list[float]]) -> list[list[float]]:
    rank = len(factors[0])
    result = [[0.0] * rank for _ in range(rank)]
    for row in factors:
        for r in range(rank):
            vr = row[r]
            for s in range(rank):
                result[r][s] += vr * row[s]
    return result


def cp_norm_squared(a: list[list[float]], b: list[list[float]], c: list[list[float]]) -> float:
    ga = gram(a)
    gb = gram(b)
    gc = gram(c)
    rank = len(ga)
    total = 0.0
    for r in range(rank):
        for s in range(rank):
            total += ga[r][s] * gb[r][s] * gc[r][s]
    return total


def objective_from_target_norm(target_norm_sq: float, ridge_lambda: float) -> float:
    return 0.5 * ridge_lambda / (1.0 + ridge_lambda) * target_norm_sq
