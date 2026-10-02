from __future__ import annotations

import json
from time import perf_counter

from common_model import build_arrays, direct_repair, load_data, summarize


def solve() -> dict:
    data = load_data()
    demand, base, max_overtime = build_arrays(data)
    products = int(data["products"])
    periods = int(data["periods"])
    overtime_penalty = float(data["overtime_penalty"])
    shortage_penalty = float(data["shortage_penalty"])
    start = perf_counter()
    overtime, shortage = direct_repair(demand, base, max_overtime)
    wall_seconds = perf_counter() - start
    summary = summarize(overtime, shortage, overtime_penalty, shortage_penalty)
    summary.update(
        {
            "overtime": overtime,
            "shortage": shortage,
            "wall_seconds": wall_seconds,
            "runtime": wall_seconds,
            "work": products * periods,
            "iterations": 1,
            "variables": 2 * products * periods,
            "constraints": 3 * products * periods,
            "nonzeros": 4 * products * periods,
            "method": "explicit_overtime_and_shortage_slacks",
            "overtime_penalty": overtime_penalty,
            "shortage_penalty": shortage_penalty,
        }
    )
    return summary


if __name__ == "__main__":
    result = solve()
    result.pop("overtime")
    result.pop("shortage")
    print(json.dumps(result, indent=2))
