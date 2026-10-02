from __future__ import annotations

import json
from pathlib import Path


def load_data() -> dict:
    return json.loads(Path("instance.json").read_text(encoding="utf-8"))


def build_arrays(data: dict) -> tuple[list[list[int]], list[list[int]]]:
    wards = int(data["wards"])
    shifts = int(data["shifts"])
    required = [
        [800 + ((37 * w + 19 * h) % 420) for h in range(shifts)]
        for w in range(wards)
    ]
    available = [
        [
            max(0, required[w][h] - 4 * (80 + ((23 * w + 11 * h) % 220)))
            for h in range(shifts)
        ]
        for w in range(wards)
    ]
    return required, available


def shortage_matrix(required: list[list[int]], available: list[list[int]]) -> list[list[int]]:
    return [
        [max(0, required[w][h] - available[w][h]) for h in range(len(required[0]))]
        for w in range(len(required))
    ]


def summarize(shortage: list[list[int]], penalty: float) -> dict:
    total_shortage = sum(sum(row) for row in shortage)
    violated_rows = sum(1 for row in shortage for value in row if value > 0)
    max_shortage = max(value for row in shortage for value in row)
    return {
        "objective": total_shortage * penalty,
        "total_shortage": total_shortage,
        "violated_rows": violated_rows,
        "max_shortage": max_shortage,
    }
