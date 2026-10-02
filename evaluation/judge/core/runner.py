from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Iterable

from .classifier import classify_candidate
from .discovery import discover_case_keys
from .llm_judge import judge_bundle
from .loaders import load_case_bundle
from .report import write_reports


def _safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in value)


def load_case_file(path: str | Path) -> list[tuple[str, str]]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    if source.suffix.lower() == ".jsonl":
        values = [json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        values = json.loads(text)
    if isinstance(values, dict):
        values = values.get("cases", [])
    result: set[tuple[str, str]] = set()
    for value in values:
        if isinstance(value, dict):
            model, problem = value.get("model_name"), value.get("problem_id")
        elif isinstance(value, (list, tuple)) and len(value) >= 2:
            model, problem = value[0], value[1]
        else:
            continue
        if model and problem:
            result.add((str(model), str(problem)))
    return sorted(result)


def select_case_keys(
    formal_root: str | Path,
    *,
    case_file: str | Path | None = None,
    models: Iterable[str] = (),
    problems: Iterable[str] = (),
    limit: int | None = None,
) -> list[tuple[str, str]]:
    model_filter = {str(value) for value in models if str(value)}
    problem_filter = {str(value) for value in problems if str(value)}
    keys = load_case_file(case_file) if case_file else discover_case_keys(
        formal_root,
        model_filter=model_filter or None,
        problem_filter=problem_filter or None,
    )
    keys = [key for key in keys if (not model_filter or key[0] in model_filter) and (not problem_filter or key[1] in problem_filter)]
    return keys[:limit] if limit is not None else keys


def _result_row(bundle: dict[str, Any], result: dict[str, Any], dataset_id: str) -> dict[str, Any]:
    candidate = bundle.get("candidate") or {}
    ordinary = bundle.get("ordinary_baseline") or {}
    expert = bundle.get("technique_baseline") or {}
    category_labels = {
        1: "target_technique",
        2: "alternative_technique_efficient",
        3: "alternative_technique_inefficient",
        4: "correct_without_meaningful_technique",
        5: "solve_error",
    }
    return {
        **result,
        "dataset_id": dataset_id,
        "problem_id": bundle.get("problem_id"),
        "model_name": bundle.get("model_name"),
        "technique_id": (bundle.get("technique") or {}).get("tech_id"),
        "technique_name": (bundle.get("technique") or {}).get("name"),
        "category_label": category_labels.get(result.get("category"), result.get("category_label", "unjudged")),
        "candidate_solver_status": candidate.get("solver_status"),
        "candidate_objective_correct": candidate.get("objective_correct"),
        "candidate_objective_correct_independent": result.get("objective_correct_independent"),
        "candidate_solver_runtime_seconds": candidate.get("solver_runtime_seconds"),
        "candidate_build_seconds": candidate.get("build_s"),
        "candidate_total_process_seconds": candidate.get("total_process_s"),
        "candidate_num_variables": candidate.get("num_variables"),
        "candidate_num_constraints": candidate.get("num_constraints"),
        "candidate_num_nonzeros": candidate.get("num_nonzeros"),
        "candidate_work_units": candidate.get("work_units"),
        "candidate_memory_peak_mb": candidate.get("memory_peak_mb"),
        "candidate_memory_peak_gb": candidate.get("memory_peak_gb"),
        "api_elapsed_seconds": candidate.get("api_elapsed_s"),
        "end_to_end_seconds": candidate.get("end_to_end_s"),
        "ordinary_solver_runtime_seconds": ordinary.get("solver_runtime_seconds"),
        "technique_solver_runtime_seconds": expert.get("solver_runtime_seconds"),
        "missing_context": bundle.get("missing_context", []),
        "reference_source": bundle.get("reference_source"),
        "reference_note": bundle.get("reference_note"),
    }


def run_judge(
    *,
    formal_root: str | Path,
    judge_config_path: str | Path,
    out_dir: str | Path,
    dataset_root: str | Path | None = None,
    public_root: str | Path | None = None,
    private_root: str | Path | None = None,
    baseline_root: str | Path | None = None,
    knowledge_base_path: str | Path | None = None,
    dataset_id: str = "dataset",
    case_file: str | Path | None = None,
    models: Iterable[str] = (),
    problems: Iterable[str] = (),
    limit: int | None = None,
    timeout: int = 180,
    api_retries: int = 2,
    resume: bool = False,
    max_direct_code_chars: int = 24000,
    code_chunk_chars: int = 12000,
) -> list[dict[str, Any]]:
    config_path = Path(judge_config_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    keys = select_case_keys(formal_root, case_file=case_file, models=models, problems=problems, limit=limit)
    output = Path(out_dir)
    cases_dir = output / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for index, (model_name, problem_id) in enumerate(keys, start=1):
        case_path = cases_dir / f"{_safe_name(model_name)}__{_safe_name(problem_id)}.json"
        if resume and case_path.exists():
            rows.append(json.loads(case_path.read_text(encoding="utf-8")))
            continue
        bundle = load_case_bundle(
            problem_id=problem_id,
            model_name=model_name,
            dataset_root=dataset_root,
            public_root=public_root,
            private_root=private_root,
            formal_root=formal_root,
            baseline_root=baseline_root,
            knowledge_base_path=knowledge_base_path,
        )
        context = {
            "problem_id": problem_id,
            "technique": bundle.get("technique"),
            "candidate": bundle.get("candidate"),
            "ordinary_baseline": bundle.get("ordinary_baseline"),
            "technique_baseline": bundle.get("technique_baseline"),
            "reference": bundle.get("reference"),
            "reference_source": bundle.get("reference_source"),
        }
        hard = classify_candidate(context)
        print(f"[{index}/{len(keys)}] START {model_name}/{problem_id}", flush=True)
        result: dict[str, Any] | None = None
        last_error = ""
        for attempt in range(api_retries + 1):
            try:
                result = judge_bundle(
                    bundle,
                    config,
                    config_path=config_path,
                    timeout_seconds=timeout,
                    max_direct_code_chars=max_direct_code_chars,
                    code_chunk_chars=code_chunk_chars,
                )
                result["judge_source"] = "llm"
                break
            except Exception as exc:
                last_error = str(exc)
                if attempt < api_retries:
                    time.sleep(min(2 ** attempt, 8))
        if result is None:
            result = {
                **hard,
                "judge_source": "unjudged",
                "judge_api_error": last_error,
                "llm_category": None,
                "manual_review": True,
            }
        row = _result_row(bundle, result, dataset_id)
        rows.append(row)
        case_path.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{index}/{len(keys)}] DONE {model_name}/{problem_id} category={row.get('category')}", flush=True)
    write_reports(rows, output)
    return rows
