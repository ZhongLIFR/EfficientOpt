from __future__ import annotations

import json
import math
from pathlib import Path


def load_data() -> dict:
    return json.loads(Path("instance.json").read_text(encoding="utf-8"))


def build_factors(data: dict) -> tuple[list[list[float]], list[list[float]]]:
    m = int(data["stores"])
    n = int(data["products"])
    rank = int(data["rank"])
    left = []
    for i in range(m):
        left.append([
            math.sin((i + 1) * (k + 2) * 0.013)
            + 0.35 * math.cos((i + 3) * (k + 1) * 0.007)
            + 0.02 * (i % 5)
            for k in range(rank)
        ])
    right = []
    for j in range(n):
        right.append([
            math.cos((j + 2) * (k + 1) * 0.011)
            + 0.25 * math.sin((j + 5) * (k + 3) * 0.005)
            - 0.015 * (j % 7)
            for k in range(rank)
        ])
    return left, right


def dot(a: list[float], b: list[float]) -> float:
    return sum(a[k] * b[k] for k in range(len(a)))


def gram(factors: list[list[float]]) -> list[list[float]]:
    rank = len(factors[0])
    result = [[0.0] * rank for _ in range(rank)]
    for row in factors:
        for a in range(rank):
            va = row[a]
            for b in range(rank):
                result[a][b] += va * row[b]
    return result


def low_rank_norm_squared(left: list[list[float]], right: list[list[float]]) -> float:
    left_gram = gram(left)
    right_gram = gram(right)
    rank = len(left_gram)
    total = 0.0
    for a in range(rank):
        for b in range(rank):
            total += left_gram[a][b] * right_gram[a][b]
    return total


def objective_from_target_norm(target_norm_sq: float, ridge_lambda: float) -> float:
    return 0.5 * ridge_lambda / (1.0 + ridge_lambda) * target_norm_sq
