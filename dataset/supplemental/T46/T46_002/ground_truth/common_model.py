from __future__ import annotations

import json
from pathlib import Path


def load_data() -> dict:
    return json.loads(Path("instance.json").read_text(encoding="utf-8"))


def build_arrays(data: dict) -> tuple[list[float], list[float], float]:
    n = int(data["assets"])
    d = [1.0 + (i % 23) / 10.0 for i in range(n)]
    p = [0.1 + ((37 * i) % 101) / 20.0 for i in range(n)]
    budget = float(data["budget_fraction"]) * sum(p)
    return d, p, budget


def objective(d: list[float], p: list[float], x: list[float]) -> float:
    return sum(0.5 * d[i] * (x[i] - p[i]) ** 2 for i in range(len(x)))


def sparse_dual_solution(d: list[float], p: list[float], budget: float) -> list[float]:
    low = -max(d[i] * p[i] for i in range(len(d))) - 10.0
    high = max(d[i] * abs(p[i]) for i in range(len(d))) + 10.0
    for _ in range(90):
        mid = 0.5 * (low + high)
        total = sum(max(0.0, p[i] - mid / d[i]) for i in range(len(d)))
        if total > budget:
            low = mid
        else:
            high = mid
    lam = 0.5 * (low + high)
    return [max(0.0, p[i] - lam / d[i]) for i in range(len(d))]
