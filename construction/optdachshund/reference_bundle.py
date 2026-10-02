from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from statistics import median
from pathlib import Path
from typing import Any

from .agents import FrameworkError

JsonDict = dict[str, Any]

REQUIRED_REFERENCE_FILES = {
    "problem_md": "problem.md",
    "ordinary_model_py": "ordinary_model.py",
    "technique_model_py": "technique_model.py",
    "validate_py": "validate.py",
    "review_md": "review.md",
}


def safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in value)


def strip_code_fence(value: str) -> str:
    text = value.strip()
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1 :]
        if text.endswith("```"):
            text = text[:-3]
    return text.strip() + "\n"


def write_jsonl(path: str | Path, rows: list[JsonDict]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def reference_objective_value(item: JsonDict, reference_package: JsonDict | None = None) -> Any:
    if reference_package:
        metadata = reference_package.get("reference_metadata")
        if isinstance(metadata, dict) and metadata.get("reference_objective_value") is not None:
            return metadata["reference_objective_value"]
        validation_json = reference_package.get("validation_json")
        if isinstance(validation_json, dict):
            summary = validation_json.get("summary")
            if isinstance(summary, dict) and summary.get("reference_objective_value") is not None:
                return summary["reference_objective_value"]
            if validation_json.get("reference_objective_value") is not None:
                return validation_json["reference_objective_value"]
    verification = item.get("verification")
    if isinstance(verification, dict):
        if verification.get("reference_objective_value") is not None:
            return verification["reference_objective_value"]
        for key in ("answer_check", "optimality_check"):
            value = verification.get(key)
            parsed = _parse_objective_from_text(value)
            if parsed is not None:
                return parsed
    technique_solution = item.get("technique_solution")
    if isinstance(technique_solution, dict):
        for key in ("objective_value", "minimum_cost", "optimal_value"):
            if technique_solution.get(key) is not None:
                return technique_solution[key]
        answer = technique_solution.get("answer")
        if isinstance(answer, dict) and answer.get("objective_value") is not None:
            return answer["objective_value"]
        parsed = _parse_objective_from_text(answer)
        if parsed is not None:
            return parsed
    mathematical_model = item.get("mathematical_model")
    if isinstance(mathematical_model, dict):
        parsed = _parse_objective_from_text(mathematical_model.get("solution"))
        if parsed is not None:
            return parsed
    parsed = _parse_objective_from_text(item.get("natural_language_answer"))
    return parsed


def _parse_objective_from_text(value: Any) -> float | None:
    if not isinstance(value, str):
        return None
    import re

    patterns = [
        r"objective(?: value)?\s*(?:=|is|:)?\s*([-+]?\d+(?:,\d{3})*(?:\.\d+)?)",
        r"minimum(?: total)?(?: cost| objective| value)?\s*(?:=|is|:)?\s*\$?\s*([-+]?\d+(?:,\d{3})*(?:\.\d+)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, value, re.I)
        if match:
            return float(match.group(1).replace(",", ""))
    return None


def blind_item_from_reformulated(
    item: JsonDict,
    reference_package: JsonDict | None = None,
    *,
    out_dir: Path,
    public_instance_dir_name: str,
    blind_source: str,
) -> JsonDict:
    problem_id = str(item.get("problem_id") or "")
    if not problem_id:
        raise FrameworkError("Cannot export blind item without problem_id.")
    target = item.get("target_technique") if isinstance(item.get("target_technique"), dict) else {}
    verification: JsonDict = {}
    if isinstance(item.get("verification"), dict):
        verification.update(item["verification"])
    objective = reference_objective_value(item, reference_package)
    if objective is not None:
        verification["reference_objective_value"] = objective

    public_instance_path = (
        out_dir
        / "questions"
        / public_instance_dir_name
        / safe_name(problem_id)
        / "instance.json"
    ).resolve()
    return {
        "problem_id": problem_id,
        "natural_language_problem": item.get("natural_language_problem"),
        "natural_language_answer": None,
        "target_technique": {
            "tech_id": target.get("tech_id"),
            "name": target.get("name"),
            "chinese_name": target.get("chinese_name"),
        },
        "verification": verification,
        "execution_data_files": [
            {
                "source_path": str(public_instance_path),
                "relative_path": "instance.json",
                "role": "fixed public benchmark input",
            }
        ],
        "blind_export": {
            "source": blind_source,
            "instance_inlined": False,
            "fixed_data_inlined": False,
            "fixed_data_attached_at_execution": True,
            "technique_text_exposed_to_model": False,
            "internal_instance_metadata_removed": True,
        },
    }


def write_reference_package_to_dir(
    *,
    ref_dir: Path,
    item: JsonDict,
    reference_package: JsonDict,
    validation_result: JsonDict | None = None,
) -> Path:
    problem_id = str(item.get("problem_id") or reference_package.get("problem_id") or "")
    if not problem_id:
        raise FrameworkError("Cannot write reference package without problem_id.")
    ref_dir.mkdir(parents=True, exist_ok=True)

    instance = reference_package.get("instance_json")
    if isinstance(instance, dict) and "data" in instance:
        instance = instance["data"]
    if instance is None:
        instance = {}
    (ref_dir / "instance.json").write_text(json.dumps(instance, ensure_ascii=False, indent=2), encoding="utf-8")

    for key, filename in REQUIRED_REFERENCE_FILES.items():
        content = reference_package.get(key)
        if not isinstance(content, str) or not content.strip():
            raise FrameworkError(f"Reference package missing non-empty {key}.")
        (ref_dir / filename).write_text(strip_code_fence(content), encoding="utf-8")

    validation_json = None
    if validation_result and isinstance(validation_result.get("validation_json"), dict):
        validation_json = validation_result["validation_json"]
    elif isinstance(reference_package.get("validation_json"), dict):
        validation_json = reference_package["validation_json"]
    if validation_json is not None:
        (ref_dir / "validation.json").write_text(
            json.dumps(validation_json, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    target = item.get("target_technique") if isinstance(item.get("target_technique"), dict) else {}
    metadata = {
        "problem_id": problem_id,
        "target_technique": target,
        "reference_metadata": reference_package.get("reference_metadata", {}),
        "validation_result": validation_result,
        "generated_by": reference_package.get("_llm", {}),
    }
    (ref_dir / "reference_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return ref_dir


def write_reference_package(
    *,
    out_dir: Path,
    item: JsonDict,
    reference_package: JsonDict,
    validation_result: JsonDict | None = None,
) -> Path:
    problem_id = str(item.get("problem_id") or reference_package.get("problem_id") or "")
    if not problem_id:
        raise FrameworkError("Cannot write reference package without problem_id.")
    target = item.get("target_technique") if isinstance(item.get("target_technique"), dict) else {}
    tech_id = str(target.get("tech_id") or "unknown_technique")
    ref_dir = out_dir / "human_reference" / "accepted" / safe_name(tech_id) / safe_name(problem_id)
    return write_reference_package_to_dir(
        ref_dir=ref_dir,
        item=item,
        reference_package=reference_package,
        validation_result=validation_result,
    )


def write_reference_attempt_package(
    *,
    out_dir: Path,
    item: JsonDict,
    reference_package: JsonDict,
    attempt: int,
    validation_result: JsonDict | None = None,
) -> Path:
    problem_id = str(item.get("problem_id") or reference_package.get("problem_id") or "")
    if not problem_id:
        raise FrameworkError("Cannot write reference attempt without problem_id.")
    ref_dir = out_dir / "_reference_attempts" / safe_name(problem_id) / f"attempt_{attempt:02d}"
    return write_reference_package_to_dir(
        ref_dir=ref_dir,
        item=item,
        reference_package=reference_package,
        validation_result=validation_result,
    )


def public_instance_dir_name(questions_filename: str) -> str:
    return f"{Path(questions_filename).stem}_public_instances"


def mirror_public_instance(
    *,
    out_dir: Path,
    item: JsonDict,
    reference_dir: Path,
    questions_filename: str,
) -> Path:
    problem_id = str(item.get("problem_id"))
    public_dir = out_dir / "questions" / public_instance_dir_name(questions_filename) / safe_name(problem_id)
    public_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(reference_dir / "instance.json", public_dir / "instance.json")
    return public_dir / "instance.json"


def run_reference_validation(reference_dir: Path, timeout_seconds: int) -> JsonDict:
    validate_py = reference_dir / "validate.py"
    if not validate_py.exists():
        return {
            "status": "not_run",
            "ok": False,
            "error": "validate.py not found",
        }
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, str(validate_py.resolve())],
            cwd=str(reference_dir),
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "timeout",
            "ok": False,
            "runtime_seconds": time.perf_counter() - start,
            "stdout": (exc.stdout or "")[-8000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-5000:] if isinstance(exc.stderr, str) else "",
        }
    elapsed = time.perf_counter() - start
    validation_path = reference_dir / "validation.json"
    validation = None
    if validation_path.exists():
        try:
            validation = json.loads(validation_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            validation = {"json_error": str(exc)}
    return {
        "status": "ok" if proc.returncode == 0 else "error",
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "runtime_seconds": elapsed,
        "stdout": proc.stdout[-8000:],
        "stderr": proc.stderr[-5000:],
        "validation_json": validation,
    }


def _safe_percent_reduction(before: Any, after: Any) -> float | None:
    try:
        b = float(before)
        a = float(after)
    except (TypeError, ValueError):
        return None
    if b <= 0:
        return None
    return 100.0 * (b - a) / b


def _rounds_from_validation(validation_json: JsonDict | None) -> list[JsonDict]:
    if not isinstance(validation_json, dict):
        return []
    rounds = validation_json.get("rounds")
    return rounds if isinstance(rounds, list) else []


def summarize_validation_metrics(validation_result: JsonDict | None) -> JsonDict:
    validation_json = None
    if isinstance(validation_result, dict) and isinstance(validation_result.get("validation_json"), dict):
        validation_json = validation_result["validation_json"]
    if not validation_json:
        return {}

    summary = validation_json.get("summary") if isinstance(validation_json.get("summary"), dict) else {}
    rounds = _rounds_from_validation(validation_json)
    runtime_speedups: list[float] = []
    work_reductions: list[float] = []
    ordinary_solver_times: list[float] = []
    technique_solver_times: list[float] = []
    ordinary_code_times: list[float] = []
    technique_code_times: list[float] = []
    ordinary_vars = summary.get("ordinary_num_variables")
    technique_vars = summary.get("technique_num_variables")
    ordinary_constraints = summary.get("ordinary_num_constraints")
    technique_constraints = summary.get("technique_num_constraints")

    for row in rounds:
        if not isinstance(row, dict):
            continue
        ordinary = row.get("ordinary") if isinstance(row.get("ordinary"), dict) else {}
        technique = row.get("technique") if isinstance(row.get("technique"), dict) else {}
        speedup = row.get("runtime_speedup_percent")
        if speedup is None:
            speedup = _safe_percent_reduction(
                ordinary.get("solver_runtime_seconds"),
                technique.get("solver_runtime_seconds"),
            )
        if speedup is not None:
            runtime_speedups.append(float(speedup))
        work_reduction = row.get("work_reduction_percent")
        if work_reduction is None:
            work_reduction = _safe_percent_reduction(
                ordinary.get("work_units"),
                technique.get("work_units"),
            )
        if work_reduction is not None:
            work_reductions.append(float(work_reduction))
        for src, dest, key in (
            (ordinary, ordinary_solver_times, "solver_runtime_seconds"),
            (technique, technique_solver_times, "solver_runtime_seconds"),
            (ordinary, ordinary_code_times, "code_run_time_seconds"),
            (technique, technique_code_times, "code_run_time_seconds"),
        ):
            value = src.get(key)
            if isinstance(value, (int, float)):
                dest.append(float(value))
        ordinary_vars = ordinary_vars if ordinary_vars is not None else ordinary.get("num_variables")
        technique_vars = technique_vars if technique_vars is not None else technique.get("num_variables")
        ordinary_constraints = ordinary_constraints if ordinary_constraints is not None else ordinary.get("num_constraints")
        technique_constraints = technique_constraints if technique_constraints is not None else technique.get("num_constraints")

    return {
        "reference_objective_value": summary.get("reference_objective_value")
        if summary.get("reference_objective_value") is not None
        else validation_json.get("reference_objective_value"),
        "minimum_runtime_speedup_percent": summary.get("minimum_runtime_speedup_percent")
        if summary.get("minimum_runtime_speedup_percent") is not None
        else (min(runtime_speedups) if runtime_speedups else None),
        "minimum_work_reduction_percent": summary.get("minimum_work_reduction_percent")
        if summary.get("minimum_work_reduction_percent") is not None
        else (min(work_reductions) if work_reductions else None),
        "ordinary_median_solver_runtime_seconds": summary.get("ordinary_median_solver_runtime_seconds")
        if summary.get("ordinary_median_solver_runtime_seconds") is not None
        else (median(ordinary_solver_times) if ordinary_solver_times else None),
        "technique_median_solver_runtime_seconds": summary.get("technique_median_solver_runtime_seconds")
        if summary.get("technique_median_solver_runtime_seconds") is not None
        else (median(technique_solver_times) if technique_solver_times else None),
        "ordinary_median_code_run_time_seconds": summary.get("ordinary_median_code_run_time_seconds")
        if summary.get("ordinary_median_code_run_time_seconds") is not None
        else (median(ordinary_code_times) if ordinary_code_times else None),
        "technique_median_code_run_time_seconds": summary.get("technique_median_code_run_time_seconds")
        if summary.get("technique_median_code_run_time_seconds") is not None
        else (median(technique_code_times) if technique_code_times else None),
        "ordinary_num_variables": ordinary_vars,
        "technique_num_variables": technique_vars,
        "ordinary_num_constraints": ordinary_constraints,
        "technique_num_constraints": technique_constraints,
    }


def build_human_reference_manifest(
    *,
    benchmark_id: str,
    item_rows: list[JsonDict],
    reference_records: list[JsonDict],
    failed_rows: list[JsonDict],
) -> JsonDict:
    counts_by_technique: dict[str, int] = {}
    problems: list[JsonDict] = []
    for record in reference_records:
        item = record.get("item") if isinstance(record.get("item"), dict) else {}
        problem_id = str(record.get("problem_id") or item.get("problem_id") or "")
        target = item.get("target_technique") if isinstance(item.get("target_technique"), dict) else {}
        tech_id = str(target.get("tech_id") or record.get("tech_id") or "unknown")
        counts_by_technique[tech_id] = counts_by_technique.get(tech_id, 0) + 1
        metrics = summarize_validation_metrics(record.get("validation_result"))
        source = item.get("source") if isinstance(item.get("source"), dict) else {}
        problems.append({
            "problem_id": problem_id,
            "source_id": source.get("source_id"),
            "target_technique": tech_id,
            "reference_dir": record.get("reference_dir"),
            "public_instance": record.get("public_instance"),
            "validation_ok": bool((record.get("validation_result") or {}).get("ok")),
            "minimum_runtime_speedup_percent": metrics.get("minimum_runtime_speedup_percent"),
            "minimum_work_reduction_percent": metrics.get("minimum_work_reduction_percent"),
        })
    return {
        "benchmark_id": benchmark_id,
        "problem_count": len(reference_records),
        "reformulated_item_count": len(item_rows),
        "technique_count": len(counts_by_technique),
        "counts_by_technique": counts_by_technique,
        "acceptance_rule": (
            "LLM reformulation quality audit passed; LLM reference audit passed; "
            "validate.py runs two sequential rounds when local validation is enabled; "
            "ordinary and technique reference models must agree on objective/feasibility."
        ),
        "problems": problems,
        "failed_items": len(failed_rows),
    }


def write_bundle_outputs(
    *,
    out_dir: Path,
    item_rows: list[JsonDict],
    reference_records: list[JsonDict],
    failed_rows: list[JsonDict],
    rules: JsonDict,
    benchmark_id: str = "optdachshund_llm_multi_agent",
    questions_filename: str = "efficientopt_blind.jsonl",
) -> JsonDict:
    questions_dir = out_dir / "questions"
    questions_dir.mkdir(parents=True, exist_ok=True)
    reference_by_id = {
        str(record.get("problem_id")): record.get("reference_package")
        for record in reference_records
        if record.get("reference_package")
    }
    public_dir_name = public_instance_dir_name(questions_filename)
    accepted_items = [
        item for item in item_rows
        if str(item.get("problem_id") or "") in reference_by_id
    ]
    blind_rows = [
        blind_item_from_reformulated(
            item,
            reference_by_id.get(str(item.get("problem_id"))),
            out_dir=out_dir,
            public_instance_dir_name=public_dir_name,
            blind_source=benchmark_id,
        )
        for item in accepted_items
    ]
    write_jsonl(questions_dir / questions_filename, blind_rows)
    write_jsonl(out_dir / questions_filename, blind_rows)

    counts_by_technique: dict[str, int] = {}
    for item in accepted_items:
        target = item.get("target_technique") if isinstance(item.get("target_technique"), dict) else {}
        tech_id = str(target.get("tech_id") or "unknown")
        counts_by_technique[tech_id] = counts_by_technique.get(tech_id, 0) + 1
    human_reference_manifest = build_human_reference_manifest(
        benchmark_id=benchmark_id,
        item_rows=item_rows,
        reference_records=reference_records,
        failed_rows=failed_rows,
    )
    human_reference_dir = out_dir / "human_reference"
    human_reference_dir.mkdir(parents=True, exist_ok=True)
    (human_reference_dir / "manifest.json").write_text(
        json.dumps(human_reference_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    reference_dir = out_dir / "reference"
    reference_dir.mkdir(parents=True, exist_ok=True)
    (reference_dir / "human_reference_manifest.json").write_text(
        json.dumps(human_reference_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    manifest = {
        "benchmark_id": benchmark_id,
        "problem_count": len(blind_rows),
        "reformulated_item_count": len(item_rows),
        "reference_package_count": len(reference_records),
        "technique_count": len(counts_by_technique),
        "counts_by_technique": counts_by_technique,
        "format": "efficientopt_blind_v1",
        "questions": str(Path("questions") / questions_filename),
        "questions_root_copy": questions_filename,
        "public_instances": str(Path("questions") / public_dir_name),
        "human_reference": "human_reference/accepted/",
        "reference_generation_rules": rules.get("reference_generation_rules", {}),
        "failed_items": len(failed_rows),
        "blind_fields": [
            "problem_id",
            "natural_language_problem",
            "natural_language_answer",
            "target_technique",
            "verification",
            "execution_data_files",
            "blind_export",
        ],
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "PACKAGE_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest
