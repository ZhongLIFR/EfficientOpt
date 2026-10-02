from __future__ import annotations

import json
from time import perf_counter

from common_model import build_marginals, dense_objective_and_errors, load_data


def solve() -> dict:
    data = load_data()
    region_totals, channel_totals, period_totals, total = build_marginals(data)
    regions = len(region_totals)
    channels = len(channel_totals)
    periods = len(period_totals)
    start = perf_counter()
    result = dense_objective_and_errors(region_totals, channel_totals, period_totals, total)
    wall_seconds = perf_counter() - start
    return {
        "objective": result["objective"],
        "max_region_error": result["max_region_error"],
        "max_channel_error": result["max_channel_error"],
        "max_period_error": result["max_period_error"],
        "solution_checksum": result["checksum"],
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": regions * channels * periods,
        "iterations": 1,
        "variables": regions * channels * periods,
        "constraints": regions + channels + periods,
        "nonzeros": 3 * regions * channels * periods,
        "method": "dense_flattened_tensor_marginal_projection",
    }


if __name__ == "__main__":
    print(json.dumps(solve(), indent=2))
