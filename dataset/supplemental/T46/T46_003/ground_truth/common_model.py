from __future__ import annotations

import json
import math
from pathlib import Path


def load_data() -> dict:
    return json.loads(Path("instance.json").read_text(encoding="utf-8"))


def build_blocks(data: dict) -> list[tuple[float, list[float]]]:
    cones = int(data["cones"])
    dim = int(data["cone_dimension"])
    return [
        (((37 * k) % 100) / 10.0 - 2.0, [(((17 * k + 11 * i) % 101) - 50) / 25.0 for i in range(dim)])
        for k in range(cones)
    ]


def cone_project(t: float, y: list[float]) -> tuple[float, list[float]]:
    norm = math.sqrt(sum(v * v for v in y))
    if norm <= t:
        return t, y[:]
    if norm <= -t:
        return 0.0, [0.0] * len(y)
    scale = (norm + t) / (2.0 * norm)
    return 0.5 * (norm + t), [scale * v for v in y]


def projection_objective(blocks: list[tuple[float, list[float]]], projected: list[tuple[float, list[float]]]) -> float:
    total = 0.0
    for (t, y), (u, v) in zip(blocks, projected):
        total += 0.5 * (u - t) ** 2
        total += 0.5 * sum((v[i] - y[i]) ** 2 for i in range(len(y)))
    return total
