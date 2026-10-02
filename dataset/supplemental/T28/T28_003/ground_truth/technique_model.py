from __future__ import annotations

import json
from time import perf_counter

from common_model import build_arrays, compute_shortfall, load_data, summarize


def solve() -> dict:
    data = load_data()
    required, available, critical = build_arrays(data)
    zones = int(data["zones"])
    products = int(data["products"])
    start = perf_counter()
    shortfall = compute_shortfall(required, available)
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
            "work": zones * products,
            "iterations": 1,
            "variables": zones * products,
            "constraints": zones * products,
            "nonzeros": zones * products,
            "method": "explicit_class_weighted_shortfall_slack",
            "slack_count": summary["violated_rows"],
            "critical_penalty": float(data["critical_penalty"]),
            "standard_penalty": float(data["standard_penalty"]),
        }
    )
    return summary


if __name__ == "__main__":
    result = solve()
    result.pop("shortfall")
    print(json.dumps(result, indent=2))
