from __future__ import annotations

import math
from typing import Any

DEFAULT_RELATIVE_TOLERANCE = 1e-6

def _number(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _candidate_failed(candidate: dict[str, Any]) -> tuple[bool, str, list[str]]:
    status = str(candidate.get("solver_status") or "").upper()
    returncode = candidate.get("returncode")
    objective_correct = candidate.get("objective_correct")
    notes = str(candidate.get("notes") or "").lower()
    reasons: list[str] = []
    if status == "TIME_LIMIT":
        reasons.append("time_limit")
    elif status == "INFEASIBLE":
        reasons.append("infeasible_model")
    elif status not in {"OPTIMAL", "SOLVED"}:
        if any(token in notes for token in ("attributeerror", "modulenotfound", "traceback", "syntaxerror", "importerror")):
            reasons.append("code_error")
        else:
            reasons.append("solver_error")
    if objective_correct is False:
        reasons.append("wrong_objective_or_feasibility")
    if returncode not in (None, 0) and "code_error" not in reasons:
        reasons.append("nonzero_returncode")
    if "error" in notes or "exception" in notes or "traceback" in notes:
        if "code_error" not in reasons:
            reasons.append("code_error")
    if bool(candidate.get("uses_hardcoded_answer")):
        reasons.append("hardcoded_or_answer_only")
    return bool(reasons), (reasons[0] if reasons else ""), reasons


def _objective_check(candidate: dict[str, Any], reference: dict[str, Any]) -> tuple[bool | None, str]:
    reference_value = reference.get("objective", reference.get("objective_value"))
    candidate_value = candidate.get("objective_value")
    if candidate_value is not None:
        try:
            candidate_value = float(candidate_value)
        except (TypeError, ValueError):
            return False, "invalid_candidate_objective"
        if not math.isfinite(candidate_value):
            return False, "invalid_candidate_objective"
    if reference_value is None:
        return None, "evaluation_json"
    try:
        reference_value = float(reference_value)
        tolerance = float(reference.get("relative_tolerance", DEFAULT_RELATIVE_TOLERANCE))
    except (TypeError, ValueError):
        return None, "invalid_reference"
    if not math.isfinite(reference_value) or not math.isfinite(tolerance) or tolerance < 0:
        return None, "invalid_reference"
    if candidate_value is None:
        return False, "reference_json"
    ok = abs(candidate_value - reference_value) <= tolerance * max(1.0, abs(reference_value))
    return ok, "reference_json"


def _efficiency(candidate: dict[str, Any], ordinary: dict[str, Any], expert: dict[str, Any]) -> dict[str, Any]:
    cand_time = _number(candidate.get("solver_runtime_seconds"))
    expert_time = _number(expert.get("solver_runtime_seconds"))
    ordinary_time = _number(ordinary.get("solver_runtime_seconds"))
    cand_work = _number(candidate.get("work_units"))
    expert_work = _number(expert.get("work_units"))
    ratio = cand_time / expert_time if cand_time is not None and expert_time and expert_time > 0 else None
    ordinary_ratio = cand_time / ordinary_time if cand_time is not None and ordinary_time and ordinary_time > 0 else None
    work_ratio = cand_work / expert_work if cand_work is not None and expert_work and expert_work > 0 else None

    if ratio is None:
        verdict = "unavailable"
    elif ratio <= 1.5:
        verdict = "good"
    elif ratio < 2.0 and ordinary_ratio is not None and ordinary_ratio <= 0.8:
        verdict = "good"
    elif ratio >= 2.0 or (ordinary_ratio is not None and ordinary_ratio >= 1.0):
        verdict = "poor"
    else:
        verdict = "unavailable"
    return {
        "efficiency_verdict": verdict,
        "runtime_ratio_to_technique": ratio,
        "runtime_ratio_to_ordinary": ordinary_ratio,
        "work_ratio_to_technique": work_ratio,
        "efficiency_rule_version": "runtime_ratio_v1",
    }


def classify_candidate(context: dict[str, Any]) -> dict[str, Any]:
    candidate = dict(context.get("candidate") or {})
    independent_correct, validation_source = _objective_check(candidate, dict(context.get("reference") or {}))
    if validation_source == "reference_json":
        validation_source = str(context.get("reference_source") or validation_source)
    if independent_correct is not None:
        candidate["objective_correct"] = independent_correct
    correctness = candidate.get("objective_correct")
    correctness_known = correctness is True or correctness is False
    failed, reason, failure_reasons = _candidate_failed(candidate)
    efficiency = _efficiency(
        candidate,
        dict(context.get("ordinary_baseline") or {}),
        dict(context.get("technique_baseline") or {}),
    )

    category = 5 if failed else None

    return {
        "category": category,
        "hard_category": 5 if failed else None,
        "category_label": "solve_error" if failed else ("unjudged" if correctness_known else "needs_manual_review"),
        "hard_failure_reason": reason or None,
        "failure_reasons": failure_reasons,
        "objective_validation_source": validation_source,
        "objective_correct_independent": independent_correct,
        "objective_validation_status": "correct" if correctness is True else ("incorrect" if correctness is False else "unknown"),
        "deterministic_efficiency_review": efficiency["efficiency_verdict"] == "uncertain",
        "manual_review": not failed and not correctness_known,
        "manual_review_reason": "objective_correctness_unknown" if not failed and not correctness_known else None,
        **efficiency,
    }
