from __future__ import annotations

import json
from time import perf_counter

from common_model import build_arrays, load_data, summarize


def solve() -> dict:
    data = load_data()
    required, available, critical = build_arrays(data)
    zones = int(data["zones"])
    products = int(data["products"])
    shortfall = [[0] * products for _ in range(zones)]
    start = perf_counter()
    work = 0
    for z in range(zones):
        for p in range(products):
            low = 0
            high = max(0, required[z][p] - available[z][p])
            while low < high:
                mid = (low + high) // 2
                work += 1
                if available[z][p] + mid >= required[z][p]:
                    high = mid
                else:
                    low = mid + 1
            # Verification scan mimics repeated feasibility checks often used when soft rows are not modeled explicitly.
            for budget in range(low + 1):
                work += 1
                if available[z][p] + budget >= required[z][p]:
                    shortfall[z][p] = budget
                    break
    wall_seconds = perf_counter() - start
    summary = summarize(
        shortfall,
        critical,
        float(data["critical_penalty"]),
        float(data["standard_penalty"]),
    )
    summary.update(
        {
            "shortfall": shortfall,
            "wall_seconds": wall_seconds,
            "runtime": wall_seconds,
            "work": work,
            "iterations": work,
            "variables": zones * products,
            "constraints": zones * products,
            "nonzeros": zones * products,
            "method": "feasibility_budget_search",
        }
    )
    return summary


if __name__ == "__main__":
    result = solve()
    result.pop("shortfall")
    print(json.dumps(result, indent=2))
