from __future__ import annotations

import json
from pathlib import Path

from common_model import build_blocks, cone_project, load_data, projection_objective
from ordinary_model import solve as solve_ordinary
from technique_model import solve as solve_technique


def compare(ordinary: dict, technique: dict, reference_objective: float) -> dict:
    scale = max(1.0, abs(reference_objective), abs(ordinary["objective"]), abs(technique["objective"]))
    runtime_speedup = 100.0 * (ordinary["runtime"] - technique["runtime"]) / max(ordinary["runtime"], 1e-12)
    work_reduction = 100.0 * (ordinary["work"] - technique["work"]) / max(ordinary["work"], 1e-12)
    checks = {
        "objective_match": abs(ordinary["objective"] - technique["objective"]) <= 1e-8 * scale,
        "ordinary_matches_reference": abs(ordinary["objective"] - reference_objective) <= 1e-8 * scale,
        "technique_matches_reference": abs(technique["objective"] - reference_objective) <= 1e-8 * scale,
        "runtime_speedup_at_least_10_percent": runtime_speedup >= 10.0,
        "deterministic_work_reduced": technique["work"] < ordinary["work"],
    }
    return {
        "ordinary": {k: v for k, v in ordinary.items() if k != "projected_blocks"},
        "technique": {k: v for k, v in technique.items() if k != "projected_blocks"},
        "reference_objective": reference_objective,
        "runtime_speedup_percent": runtime_speedup,
        "work_reduction_percent": work_reduction,
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> int:
    data = load_data()
    blocks = build_blocks(data)
    reference = [cone_project(t, y) for t, y in blocks]
    reference_objective = projection_objective(blocks, reference)
    rounds = [compare(solve_ordinary(), solve_technique(), reference_objective) for _ in range(2)]
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
