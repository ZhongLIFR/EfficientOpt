from __future__ import annotations

import json
from time import perf_counter

from common_model import build_blocks, cone_project, load_data, projection_objective


def solve() -> dict:
    data = load_data()
    blocks = build_blocks(data)
    start = perf_counter()
    projected = [cone_project(t, y) for t, y in blocks]
    wall_seconds = perf_counter() - start
    return {
        "objective": projection_objective(blocks, projected),
        "projected_blocks": projected,
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": len(blocks) * int(data["cone_dimension"]),
        "iterations": 1,
        "variables": len(blocks) * (int(data["cone_dimension"]) + 1),
        "constraints": len(blocks),
        "nonzeros": len(blocks) * int(data["cone_dimension"]),
        "method": "native_soc_projection_formula",
        "structure_preserved": "second-order cone blocks",
    }


if __name__ == "__main__":
    result = solve()
    result.pop("projected_blocks")
    print(json.dumps(result, indent=2))
