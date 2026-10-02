from __future__ import annotations

import json
from pathlib import Path


def load_data() -> dict:
    return json.loads(Path("instance.json").read_text(encoding="utf-8"))


def build_arrays(data: dict) -> tuple[list[list[float]], list[list[float]], list[float]]:
    microgrids = int(data["microgrids"])
    periods = int(data["periods"])
    d = [
        [1.0 + ((13 * g + 7 * t) % 19) / 10.0 for t in range(periods)]
        for g in range(microgrids)
    ]
    p = [
        [3.0 + ((17 * g + 23 * t) % 37) / 10.0 for t in range(periods)]
        for g in range(microgrids)
    ]
    demand = [float(data["demand_fraction"]) * sum(p[g]) for g in range(microgrids)]
    return d, p, demand


def objective(d: list[list[float]], p: list[list[float]], x: list[list[float]]) -> float:
    return sum(
        0.5 * d[g][t] * (x[g][t] - p[g][t]) ** 2
        for g in range(len(d))
        for t in range(len(d[0]))
    )


def block_solution(d: list[list[float]], p: list[list[float]], demand: list[float]) -> list[list[float]]:
    microgrids = len(d)
    periods = len(d[0])
    x = [[0.0] * periods for _ in range(microgrids)]
    for g in range(microgrids):
        multiplier = (sum(p[g][t] for t in range(periods)) - demand[g]) / sum(
            1.0 / d[g][t] for t in range(periods)
        )
        for t in range(periods):
            x[g][t] = p[g][t] - multiplier / d[g][t]
    return x
