from __future__ import annotations

import json
from time import perf_counter

from common_model import build_arrays, load_data, shortage_matrix, summarize


def solve() -> dict:
    data = load_data()
    required, available = build_arrays(data)
    penalty = float(data["shortage_penalty_per_nurse_hour"])
    wards = int(data["wards"])
    shifts = int(data["shifts"])
    start = perf_counter()
    shortage = shortage_matrix(required, available)
    wall_seconds = perf_counter() - start
    summary = summarize(shortage, penalty)
    summary.update(
        {
            "shortage": shortage,
            "wall_seconds": wall_seconds,
            "runtime": wall_seconds,
            "work": wards * shifts,
            "iterations": 1,
            "variables": wards * shifts,
            "constraints": wards * shifts,
            "nonzeros": wards * shifts,
            "method": "explicit_shortage_slack_penalty",
            "slack_count": sum(1 for row in shortage for value in row if value > 0),
            "penalty_per_unit": penalty,
        }
    )
    return summary


if __name__ == "__main__":
    result = solve()
    result.pop("shortage")
    print(json.dumps(result, indent=2))
