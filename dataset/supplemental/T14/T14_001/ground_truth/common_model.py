from __future__ import annotations

import json
from pathlib import Path


def load_data() -> dict:
    return json.loads(Path("instance.json").read_text(encoding="utf-8"))


def build_arrays(data: dict) -> tuple[list[list[float]], list[list[float]]]:
    regions = int(data["regions"])
    periods = int(data["time_periods"])
    q = [
        [1.0 + ((17 * k + 13 * h) % 19) / 10.0 for h in range(periods)]
        for k in range(regions)
    ]
    p = [
        [(((37 * k + 23 * h) % 101) - 50) / 10.0 for h in range(periods)]
        for k in range(regions)
    ]
    return q, p


def objective_from_consensus(q: list[list[float]], p: list[list[float]], z: list[float]) -> float:
    return sum(
        0.5 * q[k][h] * (z[h] - p[k][h]) ** 2
        for k in range(len(q))
        for h in range(len(z))
    )


def exact_consensus_solution(q: list[list[float]], p: list[list[float]]) -> list[float]:
    periods = len(p[0])
    return [
        sum(q[k][h] * p[k][h] for k in range(len(q))) / sum(q[k][h] for k in range(len(q)))
        for h in range(periods)
    ]
