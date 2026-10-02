from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .knowledge_base import TechniqueKnowledgeBase
from .classifier import DEFAULT_RELATIVE_TOLERANCE


def _paired_reference(ordinary: dict[str, Any], technique: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """Use paired successful results only when both objective values agree."""
    if any(str(row.get("solver_status") or "").upper() not in {"OPTIMAL", "SOLVED"}
           for row in (ordinary, technique)):
        return {}, "A paired successful ordinary/technique reference is unavailable."
    try:
        ordinary_value = float(ordinary["objective_value"])
        technique_value = float(technique["objective_value"])
    except (KeyError, TypeError, ValueError):
        return {}, "A paired reference objective is missing or nonnumeric."
    if not all(math.isfinite(value) for value in (ordinary_value, technique_value)):
        return {}, "A paired reference objective is not finite."
    if abs(ordinary_value - technique_value) > DEFAULT_RELATIVE_TOLERANCE * max(1.0, abs(technique_value)):
        return {}, "Ordinary and technique reference objectives disagree; supply a verified reference.json."
    return {
        "objective_value": technique_value,
        "relative_tolerance": DEFAULT_RELATIVE_TOLERANCE,
    }, "Objective recovered from agreeing successful paired baseline results."


def _first_non_null(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _read(path: Path, limit: int | None = None) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text if limit is None or len(text) <= limit else text[:limit] + "\n...[truncated]..."


def _normalise_runner(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out["solver_runtime_seconds"] = row.get("solver_runtime_seconds", row.get("solver_s"))
    out["solver_status"] = row.get("solver_status", row.get("status"))
    return out


def _normalise_candidate(evaluation: dict[str, Any], parsed: dict[str, Any], code: str) -> dict[str, Any]:
    execution = evaluation.get("execution_result") if isinstance(evaluation.get("execution_result"), dict) else {}
    out = dict(evaluation)
    known_fields = (
        "objective_value", "num_variables", "num_constraints", "num_nonzeros",
        "num_binary_variables", "num_integer_variables", "num_continuous_variables",
        "node_count", "simplex_iterations", "work_units", "mip_gap",
        "rss_build_start_mb", "rss_before_solve_mb", "rss_after_solve_mb", "rss_max_snapshot_mb",
        "build_memory_delta_mb", "solve_memory_delta_mb", "gurobi_mem_used_mb", "gurobi_max_mem_used_mb",
        "gurobi_mem_after_build_gb", "gurobi_max_mem_after_build_gb", "gurobi_mem_after_solve_gb",
        "gurobi_max_mem_after_solve_gb", "gurobi_build_peak_above_current_gb",
        "gurobi_peak_increase_during_solve_gb", "gurobi_solve_extra_peak_gb",
        "notes", "error",
    )
    for field in known_fields:
        value = _first_non_null(execution.get(field), evaluation.get(field))
        if value is not None:
            out[field] = value
    out["solver_status"] = _first_non_null(execution.get("solver_status"), evaluation.get("solver_status"))
    out["solver_runtime_seconds"] = _first_non_null(
        execution.get("solver_runtime_seconds"), execution.get("solver_s"),
        evaluation.get("solver_runtime_seconds"), evaluation.get("solver_s"),
    )
    out["build_s"] = _first_non_null(
        execution.get("build_s"), execution.get("model_build_seconds"),
        evaluation.get("build_s"), evaluation.get("model_build_seconds"),
    )
    out["total_process_s"] = _first_non_null(
        execution.get("total_process_s"), execution.get("total_s"),
        evaluation.get("total_process_s"), evaluation.get("total_s"),
    )
    out["api_elapsed_s"] = _first_non_null(
        evaluation.get("api_elapsed_s"), evaluation.get("api_latency_seconds"),
    )
    out["end_to_end_s"] = _first_non_null(
        evaluation.get("end_to_end_s"), execution.get("end_to_end_s"),
    )
    peak_gb = _first_non_null(out.get("gurobi_max_mem_after_solve_gb"), out.get("gurobi_max_mem_used_gb"))
    peak_mb = _first_non_null(out.get("gurobi_max_mem_used_mb"), out.get("gurobi_max_mem_after_solve_mb"))
    out["memory_peak_gb"] = float(peak_gb) if peak_gb is not None else (float(peak_mb) / 1024.0 if peak_mb is not None else None)
    out["memory_peak_mb"] = float(peak_mb) if peak_mb is not None else (float(peak_gb) * 1024.0 if peak_gb is not None else None)
    out["candidate_code"] = code
    out["formulation_summary"] = parsed.get("formulation_summary") if isinstance(parsed, dict) else {}
    out["returncode"] = evaluation.get("returncode")
    return out


def load_case_bundle(
    *,
    problem_id: str,
    model_name: str,
    formal_root: str | Path,
    dataset_root: str | Path | None = None,
    public_root: str | Path | None = None,
    private_root: str | Path | None = None,
    baseline_root: str | Path | None = None,
    knowledge_base_path: str | Path | None = None,
) -> dict[str, Any]:
    problem_id = str(problem_id)
    tech_id = problem_id.split("_", 1)[0]
    if dataset_root is not None:
        public_dir = Path(dataset_root) / tech_id / problem_id
        private_dir = public_dir / "ground_truth"
    elif public_root is not None and private_root is not None:
        public_dir = Path(public_root) / tech_id / problem_id
        private_dir = Path(private_root) / tech_id / problem_id
    else:
        raise ValueError("Supply dataset_root containing Txx/Txx_nnn task folders.")
    formal_dir = Path(formal_root) / model_name / problem_id
    ordinary_path = Path(baseline_root) / "ordinary" / problem_id / "runner_result.json" if baseline_root is not None else None
    technique_path = Path(baseline_root) / "technique" / problem_id / "runner_result.json" if baseline_root is not None else None
    if ordinary_path is None or not ordinary_path.exists():
        ordinary_path = private_dir / "ordinary_result.json"
    if technique_path is None or not technique_path.exists():
        technique_path = private_dir / "technique_result.json"

    metadata = _load_json(private_dir / "metadata.json", {})
    reference_path = private_dir / "reference.json"
    reference = _load_json(reference_path, {})
    evaluation = _load_json(formal_dir / "evaluation.json", {})
    parsed = _load_json(formal_dir / "parsed.json", {})
    candidate_code = _read(formal_dir / "candidate_model.py")
    ordinary = _normalise_runner(_load_json(ordinary_path, {}))
    technique = _normalise_runner(_load_json(technique_path, {}))
    reference_source = "reference_json" if reference_path.exists() else "unavailable"
    reference_note = "Explicit reference.json takes precedence."
    if not reference_path.exists():
        reference, reference_note = _paired_reference(ordinary, technique)
        if reference:
            reference_source = "paired_baseline_results"
    primary_tech_id = str(metadata.get("primary_technique", tech_id))
    kb = None
    try:
        kb = TechniqueKnowledgeBase.from_json(knowledge_base_path) if knowledge_base_path else TechniqueKnowledgeBase.default()
        kb_entry = kb.get(primary_tech_id)
        kb_source = kb.source_path
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        kb_entry = {}
        kb_source = None
    technique_catalog = []
    if kb is not None:
        technique_catalog = [
            {
                key: entry.get(key)
                for key in ("tech_id", "name", "english", "category", "core_use", "semantic_equivalents")
                if entry.get(key) is not None
            }
            for entry in kb.all()
        ]
    technique_spec = {
        **kb_entry,
        "tech_id": primary_tech_id,
        "name": metadata.get("technique_name") or kb_entry.get("name", ""),
        "core_idea": _read(private_dir / "formulation.md", limit=10000) or kb_entry.get("core_idea", ""),
        "semantic_equivalents": kb_entry.get("semantic_equivalents", []),
        "knowledge_base_source": kb_source,
    }
    context_status = {
        "problem_statement": bool(_read(public_dir / "problem.md")),
        "formulation": bool(_read(private_dir / "formulation.md")),
        "reference": reference_path.exists() or bool(reference),
        "ordinary_baseline": ordinary_path.exists(),
        "technique_baseline": technique_path.exists(),
        "candidate_code": bool(candidate_code),
    }
    return {
        "problem_id": problem_id,
        "model_name": model_name,
        "problem_statement": _read(public_dir / "problem.md"),
        "technique": technique_spec,
        "technique_catalog": technique_catalog,
        "reference": reference,
        "reference_source": reference_source,
        "reference_note": reference_note,
        "context_status": context_status,
        "missing_context": [name for name, present in context_status.items() if not present],
        "reference_metadata": metadata,
        "reference_formulation": _read(private_dir / "formulation.md"),
        "candidate": _normalise_candidate(evaluation, parsed, candidate_code),
        "ordinary_baseline": ordinary,
        "technique_baseline": technique,
        "ordinary_reference_code": _read(private_dir / "ordinary_model.py"),
        "technique_reference_code": _read(private_dir / "technique_model.py"),
    }
