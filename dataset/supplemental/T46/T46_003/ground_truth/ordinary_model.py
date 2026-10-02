from __future__ import annotations

import json
import math
from time import perf_counter

from common_model import build_blocks, load_data, projection_objective


def generic_line_search_projection(t: float, y: list[float]) -> tuple[float, list[float], int]:
    norm = math.sqrt(sum(v * v for v in y))
    if norm <= t:
        return t, y[:], len(y)
    if norm <= -t:
        return 0.0, [0.0] * len(y), len(y)
    target = (norm + t) / (2.0 * norm)
    low = 0.0
    high = 1.0
    work = 0
    for _ in range(80):
        mid = 0.5 * (low + high)
        if mid < target:
            low = mid
        else:
            high = mid
        work += len(y)
    alpha = 0.5 * (low + high)
    return alpha * norm, [alpha * v for v in y], work


def solve() -> dict:
    data = load_data()
    blocks = build_blocks(data)
    start = perf_counter()
    projected = []
    work = 0
    for t, y in blocks:
        u, v, block_work = generic_line_search_projection(t, y)
        projected.append((u, v))
        work += block_work
    wall_seconds = perf_counter() - start
    return {
        "objective": projection_objective(blocks, projected),
        "projected_blocks": projected,
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": work,
        "iterations": 80 * len(blocks),
        "variables": len(blocks) * (int(data["cone_dimension"]) + 1),
        "constraints": len(blocks),
        "nonzeros": len(blocks) * int(data["cone_dimension"]),
        "method": "generic_norm_line_search",
    }


if __name__ == "__main__":
    result = solve()
    result.pop("projected_blocks")
    print(json.dumps(result, indent=2))
