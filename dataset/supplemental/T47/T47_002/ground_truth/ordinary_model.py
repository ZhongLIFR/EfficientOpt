from __future__ import annotations

import json
from time import perf_counter

from common_model import build_marginals, dense_objective_and_errors, load_data


def solve() -> dict:
    data = load_data()
    row_totals, col_totals, total = build_marginals(data)
    rows = len(row_totals)
    cols = len(col_totals)
    start = perf_counter()
    result = dense_objective_and_errors(row_totals, col_totals, total)
    wall_seconds = perf_counter() - start
    return {
        "objective": result["objective"],
        "max_row_error": result["max_row_error"],
        "max_column_error": result["max_column_error"],
        "solution_checksum": result["checksum"],
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": rows * cols,
        "iterations": 1,
        "variables": rows * cols,
        "constraints": rows + cols,
        "nonzeros": 2 * rows * cols,
        "method": "dense_flattened_matrix_projection",
    }


if __name__ == "__main__":
    print(json.dumps(solve(), indent=2))
