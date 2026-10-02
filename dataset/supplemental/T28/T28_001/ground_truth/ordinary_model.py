from __future__ import annotations

import json
from time import perf_counter

from common_model import build_arrays, load_data, summarize


def solve() -> dict:
    data = load_data()
    required, available = build_arrays(data)
    penalty = float(data["shortage_penalty_per_nurse_hour"])
    wards = int(data["wards"])
    shifts = int(data["shifts"])
    shortage = [[0] * shifts for _ in range(wards)]
    start = perf_counter()
    work = 0
    for w in range(wards):
        for h in range(shifts):
            budget = 0
            while available[w][h] + budget < required[w][h]:
                budget += 1
                work += 1
            shortage[w][h] = budget
    wall_seconds = perf_counter() - start
    summary = summarize(shortage, penalty)
    summary.update(
        {
            "shortage": shortage,
            "wall_seconds": wall_seconds,
            "runtime": wall_seconds,
            "work": work,
            "iterations": work,
            "variables": wards * shifts,
            "constraints": wards * shifts,
            "nonzeros": wards * shifts,
            "method": "unit_budget_feasibility_search",
        }
    )
    return summary


if __name__ == "__main__":
    result = solve()
    result.pop("shortage")
    print(json.dumps(result, indent=2))
