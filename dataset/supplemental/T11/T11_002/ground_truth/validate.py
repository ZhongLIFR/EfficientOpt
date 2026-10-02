from __future__ import annotations

import json
from pathlib import Path

from common_model import load_data
from ordinary_model import solve as solve_ordinary
from technique_model import solve as solve_technique


def compare(ordinary: dict, technique: dict, reference: dict) -> dict:
    scale = max(1.0, abs(reference["objective"]), abs(ordinary["objective"]), abs(technique["objective"]))
    runtime_speedup = 100.0 * (ordinary["runtime"] - technique["runtime"]) / max(ordinary["runtime"], 1e-12)
    work_reduction = 100.0 * (ordinary["work"] - technique["work"]) / max(ordinary["work"], 1e-12)
    checks = {
        "objective_match": abs(ordinary["objective"] - technique["objective"]) <= 1e-7 * scale,
        "ordinary_matches_reference": abs(ordinary["objective"] - reference["objective"]) <= 1e-7 * scale,
        "technique_matches_reference": abs(technique["objective"] - reference["objective"]) <= 1e-9 * scale,
        "runtime_speedup_at_least_10_percent": runtime_speedup >= 10.0,
        "deterministic_work_reduced": technique["work"] < ordinary["work"],
        "model_size_not_larger": technique["variables"] <= ordinary["variables"],
    }
    if "max_feasibility_error" in ordinary:
        checks["ordinary_feasible"] = ordinary["max_feasibility_error"] <= 1e-6
        checks["technique_feasible"] = technique.get("max_feasibility_error", 0.0) <= 1e-6
    if "max_vi_residual" in ordinary:
        checks["ordinary_vi_residual_small"] = ordinary["max_vi_residual"] <= 1e-6
        checks["technique_vi_residual_small"] = technique.get("max_vi_residual", 0.0) <= 1e-6
    if "lex_tuple" in ordinary:
        checks["same_lex_tuple"] = ordinary["lex_tuple"] == technique["lex_tuple"] == reference["lex_tuple"]
    if "cq_valid" in ordinary:
        checks["cq_failure_detected"] = ordinary["cq_valid"] is False and technique["cq_valid"] is False
    return {
        "ordinary": ordinary,
        "technique": technique,
        "reference_objective": reference["objective"],
        "runtime_speedup_percent": runtime_speedup,
        "work_reduction_percent": work_reduction,
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> int:
    data = load_data()
    reference = solve_technique()
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
