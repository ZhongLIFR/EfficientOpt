from __future__ import annotations

import json
from pathlib import Path


def load_data() -> dict:
    return json.loads(Path("instance.json").read_text(encoding="utf-8"))


def build_arrays(data: dict) -> tuple[list[list[int]], list[list[int]], list[list[int]]]:
    products = int(data["products"])
    periods = int(data["periods"])
    demand = [
        [900 + ((29 * i + 31 * t) % 500) for t in range(periods)]
        for i in range(products)
    ]
    base = [
        [demand[i][t] - (100 + ((17 * i + 13 * t) % 250)) for t in range(periods)]
        for i in range(products)
    ]
    max_overtime = [
        [80 + ((19 * i + 7 * t) % 160) for t in range(periods)]
        for i in range(products)
    ]
    return demand, base, max_overtime


def direct_repair(
    demand: list[list[int]],
    base: list[list[int]],
    max_overtime: list[list[int]],
) -> tuple[list[list[int]], list[list[int]]]:
    products = len(demand)
    periods = len(demand[0])
    overtime = [[0] * periods for _ in range(products)]
    shortage = [[0] * periods for _ in range(products)]
    for i in range(products):
        for t in range(periods):
            gap = max(0, demand[i][t] - base[i][t])
            overtime[i][t] = min(gap, max_overtime[i][t])
            shortage[i][t] = max(0, gap - overtime[i][t])
    return overtime, shortage


def summarize(overtime: list[list[int]], shortage: list[list[int]], overtime_penalty: float, shortage_penalty: float) -> dict:
    total_overtime = sum(sum(row) for row in overtime)
    total_shortage = sum(sum(row) for row in shortage)
    return {
        "objective": overtime_penalty * total_overtime + shortage_penalty * total_shortage,
        "total_overtime": total_overtime,
        "total_shortage": total_shortage,
        "rows_with_overtime": sum(1 for row in overtime for value in row if value > 0),
        "rows_with_shortage": sum(1 for row in shortage for value in row if value > 0),
    }
