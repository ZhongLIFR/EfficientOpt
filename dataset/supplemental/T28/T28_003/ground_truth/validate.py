from __future__ import annotations

import json
from pathlib import Path

from common_model import build_arrays, compute_shortfall, load_data, summarize
from ordinary_model import solve as solve_ordinary
from technique_model import solve as solve_technique


def compare(ordinary: dict, technique: dict, reference: dict) -> dict:
    scale = max(1.0, abs(reference["objective"]), abs(ordinary["objective"]), abs(technique["objective"]))
    runtime_speedup = 100.0 * (ordinary["runtime"] - technique["runtime"]) / max(ordinary["runtime"], 1e-12)
    work_reduction = 100.0 * (ordinary["work"] - technique["work"]) / max(ordinary["work"], 1e-12)
    checks = {
        "objective_match": abs(ordinary["objective"] - technique["objective"]) <= 1e-9 * scale,
        "ordinary_matches_reference": abs(ordinary["objective"] - reference["objective"]) <= 1e-9 * scale,
        "technique_matches_reference": abs(technique["objective"] - reference["objective"]) <= 1e-9 * scale,
        "same_critical_shortfall": ordinary["critical_shortfall"] == technique["critical_shortfall"] == reference["critical_shortfall"],
        "same_standard_shortfall": ordinary["standard_shortfall"] == technique["standard_shortfall"] == reference["standard_shortfall"],
        "runtime_speedup_at_least_10_percent": runtime_speedup >= 10.0,
        "deterministic_work_reduced": technique["work"] < ordinary["work"],
        "slack_is_reported": technique.get("slack_count", 0) == reference["violated_rows"],
    }
    return {
        "ordinary": {k: v for k, v in ordinary.items() if k != "shortfall"},
        "technique": {k: v for k, v in technique.items() if k != "shortfall"},
        "reference_objective": reference["objective"],
        "reference_total_shortfall": reference["total_shortfall"],
        "runtime_speedup_percent": runtime_speedup,
        "work_reduction_percent": work_reduction,
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> int:
    data = load_data()
    required, available, critical = build_arrays(data)
    reference = summarize(
        compute_shortfall(required, available),
        critical,
        float(data["critical_penalty"]),
        float(data["standard_penalty"]),
    )
    rounds = [compare(solve_ordinary(), solve_technique(), reference) for _ in range(2)]
    result = {
        "problem_id": data["problem_id"],
        "target_technique": data["target_technique"],
        "independent_rounds": rounds,
        "minimum_runtime_speedup_percent": min(r["runtime_speedup_percent"] for r in rounds),
        "minimum_work_reduction_percent": min(r["work_reduction_percent"] for r in rounds),
        "pass": all(r["pass"] for r in rounds),
    }
    Path("validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
