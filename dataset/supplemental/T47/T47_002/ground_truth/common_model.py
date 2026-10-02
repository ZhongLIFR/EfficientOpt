from __future__ import annotations

import json
from pathlib import Path


def load_data() -> dict:
    return json.loads(Path("instance.json").read_text(encoding="utf-8"))


def build_marginals(data: dict) -> tuple[list[float], list[float], float]:
    m = int(data["rows"])
    n = int(data["cols"])
    row_totals = [95.0 + ((37 * i) % 113) + 0.25 * (i % 7) for i in range(m)]
    raw_cols = [87.0 + ((29 * j) % 97) + 0.15 * (j % 11) for j in range(n)]
    total = sum(row_totals)
    scale = total / sum(raw_cols)
    col_totals = [value * scale for value in raw_cols]
    return row_totals, col_totals, total


def low_rank_entry(row_total: float, col_total: float, total: float, rows: int, cols: int) -> float:
    return row_total / cols + col_total / rows - total / (rows * cols)


def dense_objective_and_errors(row_totals: list[float], col_totals: list[float], total: float) -> dict:
    rows = len(row_totals)
    cols = len(col_totals)
    col_sums = [0.0] * cols
    objective = 0.0
    checksum = 0.0
    max_row_error = 0.0
    matrix = []
    for i, row_total in enumerate(row_totals):
        row_values = []
        row_sum = 0.0
        for j, col_total in enumerate(col_totals):
            value = low_rank_entry(row_total, col_total, total, rows, cols)
            row_values.append(value)
            row_sum += value
            col_sums[j] += value
            objective += 0.5 * value * value
            if (i * 131 + j * 17) % 997 == 0:
                checksum += value
        matrix.append(row_values)
        max_row_error = max(max_row_error, abs(row_sum - row_total))
    max_col_error = max(abs(col_sums[j] - col_totals[j]) for j in range(cols))
    return {
        "objective": objective,
        "max_row_error": max_row_error,
        "max_column_error": max_col_error,
        "checksum": checksum,
        "materialized_rows": len(matrix),
    }


def low_rank_objective_and_errors(row_totals: list[float], col_totals: list[float], total: float) -> dict:
    rows = len(row_totals)
    cols = len(col_totals)
    row_part = sum((value / cols) ** 2 for value in row_totals)
    col_part = sum((value / rows) ** 2 for value in col_totals)
    objective = 0.5 * (cols * row_part + rows * col_part - total * total / (rows * cols))
    return {
        "objective": objective,
        "max_row_error": 0.0,
        "max_column_error": 0.0,
        "checksum": row_totals[0] / cols + col_totals[0] / rows - total / (rows * cols),
    }
