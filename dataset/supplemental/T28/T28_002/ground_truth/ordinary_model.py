from __future__ import annotations

import json
from time import perf_counter

from common_model import build_arrays, load_data, summarize


def solve() -> dict:
    data = load_data()
    demand, base, max_overtime = build_arrays(data)
    products = int(data["products"])
    periods = int(data["periods"])
    overtime = [[0] * periods for _ in range(products)]
    shortage = [[0] * periods for _ in range(products)]
    overtime_penalty = float(data["overtime_penalty"])
    shortage_penalty = float(data["shortage_penalty"])
    start = perf_counter()
    work = 0
    for i in range(products):
        for t in range(periods):
            gap = max(0, demand[i][t] - base[i][t])
            best_value = None
            best_overtime = 0
            best_shortage = gap
            for candidate_overtime in range(max_overtime[i][t] + 1):
                candidate_shortage = max(0, gap - candidate_overtime)
                value = overtime_penalty * candidate_overtime + shortage_penalty * candidate_shortage
                work += 1
                if best_value is None or value < best_value:
                    best_value = value
                    best_overtime = candidate_overtime
                    best_shortage = candidate_shortage
            overtime[i][t] = best_overtime
            shortage[i][t] = best_shortage
    wall_seconds = perf_counter() - start
    summary = summarize(overtime, shortage, overtime_penalty, shortage_penalty)
    summary.update(
        {
            "overtime": overtime,
            "shortage": shortage,
            "wall_seconds": wall_seconds,
            "runtime": wall_seconds,
            "work": work,
            "iterations": work,
            "variables": 2 * products * periods,
            "constraints": 3 * products * periods,
            "nonzeros": 4 * products * periods,
            "method": "enumerated_repair_budget_search",
        }
    )
    return summary


if __name__ == "__main__":
    result = solve()
    result.pop("overtime")
    result.pop("shortage")
    print(json.dumps(result, indent=2))
