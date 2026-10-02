from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


def _mean(rows: list[dict[str, Any]], key: str) -> float | None:
    values: list[float] = []
    for row in rows:
        value = row.get(key)
        if isinstance(value, (int, float)):
            values.append(float(value))
    return mean(values) if values else None


def aggregate_results(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("model_name") or "unknown")].append(row)
    out: list[dict[str, Any]] = []
    for model_name, model_rows in sorted(grouped.items()):
        categories = Counter(str(row.get("category")) for row in model_rows)
        classified_n = sum(categories.get(str(i), 0) for i in range(1, 6))
        out.append({
            "model_name": model_name,
            "n": len(model_rows),
            "classified_n": classified_n,
            "unjudged_count": len(model_rows) - classified_n,
            "objective_unknown_count": sum(row.get("objective_validation_status") == "unknown" for row in model_rows),
            "category_counts": {str(i): categories.get(str(i), 0) for i in range(1, 6)},
            "category_proportions": {str(i): categories.get(str(i), 0) / classified_n if classified_n else None for i in range(1, 6)},
            "mean_model_runtime_seconds": _mean(model_rows, "candidate_solver_runtime_seconds"),
            "mean_build_seconds": _mean(model_rows, "candidate_build_seconds"),
            "mean_api_seconds": _mean(model_rows, "api_elapsed_seconds"),
            "mean_end_to_end_seconds": _mean(model_rows, "end_to_end_seconds"),
            "mean_runtime_ratio_to_technique": _mean(model_rows, "runtime_ratio_to_technique"),
            "manual_review_count": sum(1 for row in model_rows if row.get("manual_review")),
            "error_reason_counts": dict(Counter(str(row.get("hard_failure_reason")) for row in model_rows if row.get("hard_failure_reason"))),
        })
    return out


def write_reports(rows: list[dict[str, Any]], out_dir: str | Path) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "judge_results.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    summary = aggregate_results(rows)
    (out / "judge_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = ["model_name", "n", "classified_n", "unjudged_count", "objective_unknown_count", "category_counts", "category_proportions", "mean_model_runtime_seconds", "mean_build_seconds", "mean_api_seconds", "mean_end_to_end_seconds", "mean_runtime_ratio_to_technique", "manual_review_count", "error_reason_counts"]
    with (out / "judge_summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in summary:
            writer.writerow({key: json.dumps(row[key], ensure_ascii=False) if isinstance(row.get(key), dict) else row.get(key) for key in fields})
