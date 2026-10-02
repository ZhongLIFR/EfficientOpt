from __future__ import annotations

import json
from time import perf_counter

from common_model import block_solution, build_arrays, load_data, objective


def solve() -> dict:
    data = load_data()
    d, p, demand = build_arrays(data)
    microgrids = int(data["microgrids"])
    periods = int(data["periods"])
    start = perf_counter()
    x = block_solution(d, p, demand)
    wall_seconds = perf_counter() - start
    block_size = periods + 1
    return {
        "objective": objective(d, p, x),
        "generation": x,
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": microgrids * block_size**3,
        "iterations": microgrids,
        "variables": microgrids * block_size,
        "constraints": microgrids,
        "nonzeros": 3 * microgrids * periods,
        "method": "block_diagonal_kkt",
        "structure_preserved": "independent equality-constrained diagonal QP blocks",
    }


if __name__ == "__main__":
    result = solve()
    result.pop("generation")
    print(json.dumps(result, indent=2))
