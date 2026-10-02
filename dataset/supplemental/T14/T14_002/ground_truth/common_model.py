from __future__ import annotations

import json
from pathlib import Path


def load_data() -> dict:
    return json.loads(Path("instance.json").read_text(encoding="utf-8"))


def build_arrays(data: dict) -> tuple[list[list[float]], list[list[float]], list[float]]:
    warehouses = int(data["warehouses"])
    periods = int(data["periods"])
    q = [
        [1.0 + ((11 * k + 7 * h) % 23) / 10.0 for h in range(periods)]
        for k in range(warehouses)
    ]
    p = [
        [(83 + ((19 * k + 31 * h) % 157)) / 10.0 for h in range(periods)]
        for k in range(warehouses)
    ]
    demand = [
        sum(p[k][h] for k in range(warehouses)) + (((17 * h) % 41) - 20) * 0.35
        for h in range(periods)
    ]
    return q, p, demand


def objective(q: list[list[float]], p: list[list[float]], x: list[list[float]]) -> float:
    return sum(
        0.5 * q[k][h] * (x[k][h] - p[k][h]) ** 2
        for k in range(len(q))
        for h in range(len(q[0]))
    )


def exact_solution(q: list[list[float]], p: list[list[float]], demand: list[float]) -> list[list[float]]:
    warehouses = len(q)
    periods = len(q[0])
    x = [[0.0] * periods for _ in range(warehouses)]
    for h in range(periods):
        multiplier = (sum(p[k][h] for k in range(warehouses)) - demand[h]) / sum(
            1.0 / q[k][h] for k in range(warehouses)
        )
        for k in range(warehouses):
            x[k][h] = p[k][h] - multiplier / q[k][h]
    return x
