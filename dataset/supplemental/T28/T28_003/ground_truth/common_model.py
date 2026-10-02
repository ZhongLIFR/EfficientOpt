from __future__ import annotations

import json
from pathlib import Path


def load_data() -> dict:
    return json.loads(Path("instance.json").read_text(encoding="utf-8"))


def build_arrays(data: dict) -> tuple[list[list[int]], list[list[int]], list[list[bool]]]:
    zones = int(data["zones"])
    products = int(data["products"])
    required = [
        [650 + ((41 * z + 29 * p) % 500) for p in range(products)]
        for z in range(zones)
    ]
    available = [
        [
            max(0, required[z][p] - 3 * (70 + ((17 * z + 31 * p) % 260)))
            for p in range(products)
        ]
        for z in range(zones)
    ]
    critical = [[(z + 2 * p) % 5 == 0 for p in range(products)] for z in range(zones)]
    return required, available, critical


def compute_shortfall(required: list[list[int]], available: list[list[int]]) -> list[list[int]]:
    return [
        [max(0, required[z][p] - available[z][p]) for p in range(len(required[0]))]
        for z in range(len(required))
    ]


def summarize(shortfall: list[list[int]], critical: list[list[bool]], critical_penalty: float, standard_penalty: float) -> dict:
    critical_shortfall = 0
    standard_shortfall = 0
    for z in range(len(shortfall)):
        for p in range(len(shortfall[0])):
            if critical[z][p]:
                critical_shortfall += shortfall[z][p]
            else:
                standard_shortfall += shortfall[z][p]
    return {
        "objective": critical_penalty * critical_shortfall + standard_penalty * standard_shortfall,
        "critical_shortfall": critical_shortfall,
        "standard_shortfall": standard_shortfall,
        "total_shortfall": critical_shortfall + standard_shortfall,
        "violated_rows": sum(1 for row in shortfall for value in row if value > 0),
    }
