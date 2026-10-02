from __future__ import annotations

import json
from pathlib import Path


def load_data() -> dict:
    return json.loads(Path("instance.json").read_text(encoding="utf-8"))


def build_arrays(data: dict) -> tuple[list[list[float]], list[list[float]]]:
    sites = int(data["sites"])
    features = int(data["features"])
    a = [
        [1.0 + ((17 * k + 13 * j) % 19) / 10.0 for j in range(features)]
        for k in range(sites)
    ]
    b = [
        [(((37 * k + 23 * j) % 101) - 50) / 10.0 for j in range(features)]
        for k in range(sites)
    ]
    return a, b


def objective_from_shared(a: list[list[float]], b: list[list[float]], z: list[float]) -> float:
    return sum(
        0.5 * a[k][j] * (z[j] - b[k][j]) ** 2
        for k in range(len(a))
        for j in range(len(z))
    )


def exact_shared_solution(a: list[list[float]], b: list[list[float]]) -> list[float]:
    features = len(b[0])
    return [
        sum(a[k][j] * b[k][j] for k in range(len(a))) / sum(a[k][j] for k in range(len(a)))
        for j in range(features)
    ]
