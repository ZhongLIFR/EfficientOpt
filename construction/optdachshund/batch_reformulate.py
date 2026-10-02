from __future__ import annotations

import argparse
import json
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from .agents import (
    FrameworkError,
    LLMQualityAuditAgent,
    LLMReferenceAuditAgent,
    LLMReferenceImplementationAgent,
    LLMRepairAgent,
    LLMReformulationDesignerAgent,
    LLMTechniqueMatcherAgent,
    summarize_reference_package,
    summarize_item_for_audit,
)
from .llm_client import LLMClientError
from .reference_bundle import (
    mirror_public_instance,
    run_reference_validation,
    write_bundle_outputs,
    write_jsonl as write_reference_jsonl,
    write_reference_attempt_package,
    write_reference_package,
)

JsonDict = dict[str, Any]


class ProgressReporter:
    """Small stdout reporter for long LLM-backed benchmark runs."""

    def __init__(self, *, enabled: bool = True, heartbeat_interval: int = 30) -> None:
        self.enabled = enabled
        self.heartbeat_interval = max(0, heartbeat_interval)

    def log(self, message: str) -> None:
        if not self.enabled:
            return
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}", flush=True)

    @contextmanager
    def span(self, message: str):
        if not self.enabled:
            yield
            return

        start = time.perf_counter()
        stop_event = threading.Event()
        thread: threading.Thread | None = None

        def heartbeat() -> None:
            while not stop_event.wait(self.heartbeat_interval):
                elapsed = time.perf_counter() - start
                self.log(f"WAIT  {message} ({elapsed:.1f}s elapsed)")

        self.log(f"START {message}")
        if self.heartbeat_interval > 0:
            thread = threading.Thread(target=heartbeat, daemon=True)
            thread.start()
        try:
            yield
        except Exception as exc:
            stop_event.set()
            if thread:
                thread.join(timeout=0.2)
            elapsed = time.perf_counter() - start
            self.log(f"FAIL  {message} ({elapsed:.1f}s): {type(exc).__name__}: {exc}")
            raise
        else:
            stop_event.set()
            if thread:
                thread.join(timeout=0.2)
            elapsed = time.perf_counter() - start
            self.log(f"DONE  {message} ({elapsed:.1f}s)")


def _model_label(agent: Any) -> str:
    cfg = getattr(agent, "model_cfg", {}) or {}
    model = cfg.get("model", "unknown-model")
    name = cfg.get("name")
    return f"{name}:{model}" if name else str(model)


def _short_issues(feedback: JsonDict, *, max_issues: int = 3) -> str:
    issues = feedback.get("issues", [])
    if not isinstance(issues, list):
        issues = [str(issues)]
    issues = [str(issue).strip() for issue in issues if str(issue).strip()]
    if not issues:
        return "no explicit issues returned"
    suffix = "" if len(issues) <= max_issues else f"; +{len(issues) - max_issues} more"
    return "; ".join(issues[:max_issues]) + suffix


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: str | Path) -> list[JsonDict]:
    rows: list[JsonDict] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_techniques(path: str | Path) -> dict[str, JsonDict]:
    raw = load_json(path)
    if isinstance(raw, dict) and "techniques" in raw:
        raw_items = raw["techniques"]
    elif isinstance(raw, list):
        raw_items = raw
    else:
        raise ValueError("Technique file must be a list or an object with key 'techniques'.")
    return {str(item["tech_id"]): item for item in raw_items}


def write_jsonl(path: str | Path, rows: list[JsonDict]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path: str | Path, obj: JsonDict) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def flush_incremental_outputs(
    *,
    out_dir: Path,
    plan_rows: list[JsonDict],
    item_rows: list[JsonDict],
    failed_rows: list[JsonDict],
    trace_rows: list[JsonDict],
    run_status: JsonDict,
    reference_rows: list[JsonDict] | None = None,
) -> None:
    write_jsonl(out_dir / "batch_plan.jsonl", plan_rows)
    write_jsonl(out_dir / "reformulated_items.jsonl", item_rows)
    write_jsonl(out_dir / "failed_items.jsonl", failed_rows)
    write_jsonl(out_dir / "agent_trace.jsonl", trace_rows)
    if reference_rows is not None:
        write_reference_jsonl(out_dir / "reference_records.jsonl", reference_rows)
    write_json(out_dir / "run_status.json", run_status)


def resolve_agent_model_config(model_cfg: JsonDict, agent_key: str) -> JsonDict:
    """Resolve a possibly heterogeneous LLM config for one agent.

    Backward compatible forms:
    1. Flat config: {"base_url": ..., "model": ...}
    2. Multi-agent config:
       {"default": {...}, "agents": {"technique_matcher": {...}, ...}}
    """
    if "agents" not in model_cfg:
        cfg = dict(model_cfg)
        cfg.setdefault("name", agent_key)
        return cfg

    default_cfg = dict(model_cfg.get("default", {}))
    agent_cfg = dict(model_cfg.get("agents", {}).get(agent_key, {}))
    merged = {**default_cfg, **agent_cfg}
    if not merged:
        raise ValueError(f"No model config found for agent: {agent_key}")
    merged.setdefault("name", agent_key)
    return merged


def _bool_pass(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "pass", "passed", "yes"}
    return False


def _feedback_from_error(error: str, phase: str) -> JsonDict:
    return {
        "pass": False,
        "phase": phase,
        "issues": [error],
        "repair_instructions": [
            "Return only valid JSON matching the requested full item schema.",
            "Fix the reported issue before changing any other part of the item.",
        ],
    }


def build_coverage_snapshot(
    *,
    plan_rows: list[JsonDict],
    item_rows: list[JsonDict],
    failed_rows: list[JsonDict],
    rules: JsonDict,
    target_techniques: list[str],
    technique_counts: dict[str, int],
) -> JsonDict:
    advisory_min_items = int(rules.get("coverage_rules", {}).get("min_items_per_technique", 5))
    if not target_techniques:
        target_techniques = sorted(
            {str(row.get("candidate", {}).get("tech_id")) for row in plan_rows if row.get("candidate")}
        )
    undercovered = {
        tech_id: {
            "current_count": technique_counts.get(tech_id, 0),
            "advisory_target_count": advisory_min_items,
            "suggested_more_items": max(0, advisory_min_items - technique_counts.get(tech_id, 0)),
        }
        for tech_id in target_techniques
        if technique_counts.get(tech_id, 0) < advisory_min_items
    }
    return {
        "generated_items": len(item_rows),
        "planned_items": len(plan_rows),
        "failed_items": len(failed_rows),
        "technique_counts": technique_counts,
        "target_techniques": target_techniques,
        "advisory_min_items_per_technique": advisory_min_items,
        "undercovered_techniques": undercovered,
        "coverage_is_hard_constraint": False,
        "note": "Coverage is an advisory signal for incremental benchmark construction, not a hard acceptance condition.",
    }


def audit_candidate_item(
    *,
    item: JsonDict,
    source_problem: JsonDict,
    technique: JsonDict,
    rules: JsonDict,
    quality_auditor: LLMQualityAuditAgent,
    accepted_item_summaries: list[JsonDict],
    coverage_snapshot: JsonDict,
) -> tuple[bool, JsonDict]:
    audit = quality_auditor.run(
        source_problem,
        technique,
        item,
        rules,
        accepted_item_summaries=accepted_item_summaries,
        coverage_snapshot=coverage_snapshot,
    )
    audit_ok = _bool_pass(audit.get("pass"))
    issues = audit.get("issues", [])
    if not isinstance(issues, list):
        issues = [str(issues)]
    repair_instructions = audit.get("repair_instructions", [])
    if not isinstance(repair_instructions, list):
        repair_instructions = [str(repair_instructions)]
    feedback = {
        "pass": audit_ok,
        "quality_audit_pass": audit_ok,
        "issues": issues,
        "repair_instructions": repair_instructions,
        "quality_audit": audit,
    }
    return bool(feedback["pass"]), feedback


def generate_with_feedback_loop(
    *,
    source_problem: JsonDict,
    technique: JsonDict,
    rules: JsonDict,
    designer: LLMReformulationDesignerAgent,
    quality_auditor: LLMQualityAuditAgent,
    repairer: LLMRepairAgent,
    accepted_item_summaries: list[JsonDict],
    coverage_snapshot: JsonDict,
    repair_rounds: int,
    trace_rows: list[JsonDict],
    source_id: str,
    tech_id: str,
    reporter: ProgressReporter,
    problem_index: int,
    problem_total: int,
    candidate_index: int,
    candidate_total: int,
) -> tuple[JsonDict | None, JsonDict]:
    item: JsonDict | None = None
    feedback: JsonDict = {}
    last_error: JsonDict = {}
    prefix = (
        f"source {problem_index}/{problem_total} {source_id} | "
        f"candidate {candidate_index}/{candidate_total} {tech_id}"
    )

    for attempt in range(repair_rounds + 1):
        try:
            if item is None:
                with reporter.span(
                    f"{prefix} | attempt {attempt + 1}/{repair_rounds + 1} | "
                    f"{designer.name} [{_model_label(designer)}]"
                ):
                    item = designer.run(
                        source_problem,
                        technique,
                        rules,
                        revision_context=feedback or None,
                    )
                agent_name = designer.name
            else:
                with reporter.span(
                    f"{prefix} | repair {attempt}/{repair_rounds} | "
                    f"{repairer.name} [{_model_label(repairer)}]"
                ):
                    item = repairer.run(
                        source_problem,
                        technique,
                        rejected_item=item,
                        rules=rules,
                        feedback=feedback,
                        repair_round=attempt,
                    )
                agent_name = repairer.name

            trace_rows.append({
                "source_id": source_id,
                "tech_id": tech_id,
                "agent": agent_name,
                "attempt": attempt,
                "status": "ok",
                "output": {
                    "problem_id": item.get("problem_id"),
                    "llm": item.get("_llm", {}),
                },
            })
            reporter.log(
                f"GENERATED {prefix} | problem_id={item.get('problem_id', 'unknown_problem_id')}"
            )
        except (LLMClientError, FrameworkError, json.JSONDecodeError, KeyError, TypeError) as exc:
            feedback = _feedback_from_error(str(exc), phase="generation_or_json_parse")
            last_error = {
                "source_id": source_id,
                "tech_id": tech_id,
                "attempt": attempt,
                "error": "generation_or_json_parse_failed",
                "details": str(exc),
                "feedback": feedback,
            }
            trace_rows.append({
                "source_id": source_id,
                "tech_id": tech_id,
                "agent": "generation_feedback_loop",
                "attempt": attempt,
                "status": "fail",
                "error": str(exc),
            })
            item = None
            reporter.log(
                f"GENERATION_FAILED {prefix} | attempt {attempt + 1}/{repair_rounds + 1} | {exc}"
            )
            continue

        try:
            with reporter.span(
                f"{prefix} | attempt {attempt + 1}/{repair_rounds + 1} | "
                f"{quality_auditor.name} [{_model_label(quality_auditor)}]"
            ):
                ok, feedback = audit_candidate_item(
                    item=item,
                    source_problem=source_problem,
                    technique=technique,
                    rules=rules,
                    quality_auditor=quality_auditor,
                    accepted_item_summaries=accepted_item_summaries,
                    coverage_snapshot=coverage_snapshot,
                )
            trace_rows.append({
                "source_id": source_id,
                "tech_id": tech_id,
                "agent": quality_auditor.name,
                "attempt": attempt,
                "status": "ok" if feedback.get("pass") else "fail",
                "feedback": feedback,
            })
        except (LLMClientError, FrameworkError, json.JSONDecodeError, KeyError, TypeError) as exc:
            feedback = _feedback_from_error(str(exc), phase="quality_audit")
            ok = False
            trace_rows.append({
                "source_id": source_id,
                "tech_id": tech_id,
                "agent": quality_auditor.name,
                "attempt": attempt,
                "status": "fail",
                "error": str(exc),
            })
            reporter.log(f"AUDIT_FAILED {prefix} | attempt {attempt + 1}/{repair_rounds + 1} | {exc}")

        if ok:
            reporter.log(
                f"ACCEPTED {prefix} | attempts_used={attempt + 1} | "
                f"problem_id={item.get('problem_id', 'unknown_problem_id')}"
            )
            return item, {
                "status": "accepted",
                "attempts_used": attempt + 1,
                "feedback": feedback,
            }

        last_error = {
            "source_id": source_id,
            "tech_id": tech_id,
            "attempt": attempt,
            "error": "item_rejected_after_feedback_loop",
            "feedback": feedback,
            "item": item,
        }
        trace_rows.append({
            "source_id": source_id,
            "tech_id": tech_id,
            "agent": "feedback_loop",
            "attempt": attempt,
            "status": "repair_requested" if attempt < repair_rounds else "failed",
            "feedback": feedback,
        })
        if attempt < repair_rounds:
            reporter.log(
                f"REPAIR_REQUESTED {prefix} | attempt {attempt + 1}/{repair_rounds + 1} | "
                f"issues={_short_issues(feedback)}"
            )
        else:
            reporter.log(
                f"FAILED {prefix} | exhausted {repair_rounds + 1} attempts | "
                f"issues={_short_issues(feedback)}"
            )

    return None, last_error


def _reference_feedback_from_error(error: str, phase: str) -> JsonDict:
    return {
        "pass": False,
        "phase": phase,
        "issues": [error],
        "repair_instructions": [
            "Return a complete replacement reference package matching the requested schema.",
            "Keep the same accepted reformulated problem and primary target technique.",
            "Fix all Python syntax, import, solve() interface, validation, and objective-consistency issues.",
        ],
    }


def _validation_feedback(validation_result: JsonDict, *, skip_reference_validation: bool) -> JsonDict:
    if skip_reference_validation:
        return {
            "pass": True,
            "issues": [],
            "repair_instructions": [],
        }
    issues: list[str] = []
    repair_instructions: list[str] = []
    if not validation_result.get("ok"):
        issues.append(
            "Local validate.py did not complete successfully: "
            f"status={validation_result.get('status')} stderr={str(validation_result.get('stderr') or '')[:1200]}"
        )
        repair_instructions.append(
            "Repair ordinary_model.py, technique_model.py, and validate.py so local validation exits with code 0."
        )
    validation_json = validation_result.get("validation_json")
    if not isinstance(validation_json, dict):
        issues.append("validate.py did not write a valid validation.json object.")
        repair_instructions.append("Ensure validate.py writes validation.json in the required two-round schema.")
    else:
        rounds = validation_json.get("rounds")
        if not isinstance(rounds, list) or len(rounds) < 2:
            issues.append("validation.json must contain at least two sequential rounds.")
            repair_instructions.append("Run ordinary and technique models twice and record both rounds.")
        if not validation_json.get("ok", True):
            issues.append("validation.json reports ok=false.")
            repair_instructions.append("Make the two reference models agree on objective value and feasibility.")
    return {
        "pass": not issues,
        "issues": issues,
        "repair_instructions": repair_instructions,
    }


def _merge_feedback(*feedback_objects: JsonDict) -> JsonDict:
    issues: list[str] = []
    repair_instructions: list[str] = []
    merged: JsonDict = {"pass": True, "issues": issues, "repair_instructions": repair_instructions}
    for feedback in feedback_objects:
        if not feedback:
            continue
        merged["pass"] = bool(merged["pass"] and _bool_pass(feedback.get("pass")))
        raw_issues = feedback.get("issues", [])
        if not isinstance(raw_issues, list):
            raw_issues = [str(raw_issues)]
        raw_repairs = feedback.get("repair_instructions", [])
        if not isinstance(raw_repairs, list):
            raw_repairs = [str(raw_repairs)]
        issues.extend(str(issue) for issue in raw_issues if str(issue).strip())
        repair_instructions.extend(str(step) for step in raw_repairs if str(step).strip())
    return merged


def _reference_record_summary(record: JsonDict) -> JsonDict:
    validation_result = record.get("validation_result") if isinstance(record.get("validation_result"), dict) else {}
    return {
        "problem_id": record.get("problem_id"),
        "tech_id": record.get("tech_id"),
        "reference_dir": record.get("reference_dir"),
        "public_instance": record.get("public_instance"),
        "validation_status": validation_result.get("status"),
        "validation_ok": validation_result.get("ok"),
        "llm": (record.get("reference_package") or {}).get("_llm", {}),
    }


def generate_reference_with_feedback_loop(
    *,
    item: JsonDict,
    source_problem: JsonDict,
    technique: JsonDict,
    rules: JsonDict,
    reference_implementation_agent: LLMReferenceImplementationAgent,
    reference_auditor: LLMReferenceAuditAgent,
    out_dir: Path,
    reference_repair_rounds: int,
    reference_validation_timeout: int,
    skip_reference_validation: bool,
    questions_filename: str,
    trace_rows: list[JsonDict],
    source_id: str,
    tech_id: str,
    reporter: ProgressReporter,
    problem_index: int,
    problem_total: int,
    candidate_index: int,
    candidate_total: int,
) -> tuple[JsonDict | None, JsonDict]:
    reference_package: JsonDict | None = None
    feedback: JsonDict = {}
    last_error: JsonDict = {}
    problem_id = str(item.get("problem_id") or "unknown_problem_id")
    prefix = (
        f"source {problem_index}/{problem_total} {source_id} | "
        f"candidate {candidate_index}/{candidate_total} {tech_id} | "
        f"problem_id={problem_id}"
    )

    for attempt in range(reference_repair_rounds + 1):
        try:
            with reporter.span(
                f"{prefix} | reference attempt {attempt + 1}/{reference_repair_rounds + 1} | "
                f"{reference_implementation_agent.name} [{_model_label(reference_implementation_agent)}]"
            ):
                reference_package = reference_implementation_agent.run(
                    item,
                    technique,
                    rules,
                    feedback=feedback or None,
                    repair_round=attempt,
                )
            reference_package["problem_id"] = reference_package.get("problem_id") or problem_id
            trace_rows.append({
                "source_id": source_id,
                "tech_id": tech_id,
                "problem_id": problem_id,
                "agent": reference_implementation_agent.name,
                "attempt": attempt,
                "status": "ok",
                "output": summarize_reference_package(reference_package),
            })
            reporter.log(f"REFERENCE_GENERATED {prefix}")
        except (LLMClientError, FrameworkError, json.JSONDecodeError, KeyError, TypeError) as exc:
            feedback = _reference_feedback_from_error(str(exc), phase="reference_generation_or_json_parse")
            last_error = {
                "source_id": source_id,
                "tech_id": tech_id,
                "problem_id": problem_id,
                "attempt": attempt,
                "error": "reference_generation_or_json_parse_failed",
                "details": str(exc),
                "feedback": feedback,
            }
            trace_rows.append({
                "source_id": source_id,
                "tech_id": tech_id,
                "problem_id": problem_id,
                "agent": reference_implementation_agent.name,
                "attempt": attempt,
                "status": "fail",
                "error": str(exc),
            })
            reporter.log(
                f"REFERENCE_GENERATION_FAILED {prefix} | "
                f"attempt {attempt + 1}/{reference_repair_rounds + 1} | {exc}"
            )
            continue

        try:
            attempt_dir = write_reference_attempt_package(
                out_dir=out_dir,
                item=item,
                reference_package=reference_package,
                attempt=attempt,
            )
            if skip_reference_validation:
                validation_result: JsonDict = {
                    "status": "skipped",
                    "ok": True,
                    "validation_json": reference_package.get("validation_json"),
                    "note": "Reference validation was skipped by CLI flag.",
                }
                reporter.log(f"REFERENCE_VALIDATION_SKIPPED {prefix}")
            else:
                with reporter.span(
                    f"{prefix} | local validate.py attempt {attempt + 1}/{reference_repair_rounds + 1}"
                ):
                    validation_result = run_reference_validation(attempt_dir, reference_validation_timeout)
                reporter.log(
                    f"REFERENCE_VALIDATED {prefix} | "
                    f"status={validation_result.get('status')} ok={validation_result.get('ok')}"
                )
        except (FrameworkError, OSError, RuntimeError, json.JSONDecodeError, TypeError) as exc:
            validation_result = {
                "status": "error",
                "ok": False,
                "error": str(exc),
                "validation_json": None,
            }
            reporter.log(f"REFERENCE_VALIDATION_SETUP_FAILED {prefix} | {exc}")

        validation_feedback = _validation_feedback(
            validation_result,
            skip_reference_validation=skip_reference_validation,
        )
        if isinstance(validation_result.get("validation_json"), dict):
            reference_package["validation_json"] = validation_result["validation_json"]

        try:
            with reporter.span(
                f"{prefix} | reference audit attempt {attempt + 1}/{reference_repair_rounds + 1} | "
                f"{reference_auditor.name} [{_model_label(reference_auditor)}]"
            ):
                audit = reference_auditor.run(
                    item,
                    technique,
                    reference_package,
                    validation_result,
                    rules,
                )
            audit_feedback = {
                "pass": _bool_pass(audit.get("pass")),
                "issues": audit.get("issues", []),
                "repair_instructions": audit.get("repair_instructions", []),
                "reference_audit": audit,
            }
            trace_rows.append({
                "source_id": source_id,
                "tech_id": tech_id,
                "problem_id": problem_id,
                "agent": reference_auditor.name,
                "attempt": attempt,
                "status": "ok" if audit_feedback["pass"] else "fail",
                "feedback": audit_feedback,
                "validation_result": {
                    "status": validation_result.get("status"),
                    "ok": validation_result.get("ok"),
                },
            })
        except (LLMClientError, FrameworkError, json.JSONDecodeError, KeyError, TypeError) as exc:
            audit_feedback = _reference_feedback_from_error(str(exc), phase="reference_audit")
            trace_rows.append({
                "source_id": source_id,
                "tech_id": tech_id,
                "problem_id": problem_id,
                "agent": reference_auditor.name,
                "attempt": attempt,
                "status": "fail",
                "error": str(exc),
            })
            reporter.log(f"REFERENCE_AUDIT_FAILED {prefix} | {exc}")

        feedback = _merge_feedback(validation_feedback, audit_feedback)
        if _bool_pass(feedback.get("pass")):
            final_dir = write_reference_package(
                out_dir=out_dir,
                item=item,
                reference_package=reference_package,
                validation_result=validation_result,
            )
            public_instance = mirror_public_instance(
                out_dir=out_dir,
                item=item,
                reference_dir=final_dir,
                questions_filename=questions_filename,
            )
            record = {
                "status": "accepted",
                "problem_id": problem_id,
                "source_id": source_problem.get("source_id"),
                "tech_id": tech_id,
                "item": item,
                "reference_package": reference_package,
                "validation_result": validation_result,
                "reference_dir": str(final_dir),
                "public_instance": str(public_instance),
                "attempts_used": attempt + 1,
            }
            reporter.log(
                f"REFERENCE_ACCEPTED {prefix} | attempts_used={attempt + 1} | "
                f"dir={final_dir}"
            )
            return record, {
                "status": "accepted",
                "attempts_used": attempt + 1,
                "feedback": feedback,
            }

        last_error = {
            "source_id": source_id,
            "tech_id": tech_id,
            "problem_id": problem_id,
            "attempt": attempt,
            "error": "reference_rejected_after_feedback_loop",
            "feedback": feedback,
            "validation_result": validation_result,
            "reference_package_summary": summarize_reference_package(reference_package or {}),
        }
        trace_rows.append({
            "source_id": source_id,
            "tech_id": tech_id,
            "problem_id": problem_id,
            "agent": "reference_feedback_loop",
            "attempt": attempt,
            "status": "repair_requested" if attempt < reference_repair_rounds else "failed",
            "feedback": feedback,
        })
        if attempt < reference_repair_rounds:
            reporter.log(
                f"REFERENCE_REPAIR_REQUESTED {prefix} | "
                f"attempt {attempt + 1}/{reference_repair_rounds + 1} | "
                f"issues={_short_issues(feedback)}"
            )
        else:
            reporter.log(
                f"REFERENCE_FAILED {prefix} | exhausted {reference_repair_rounds + 1} attempts | "
                f"issues={_short_issues(feedback)}"
            )

    return None, last_error


def run_batch(args: argparse.Namespace) -> None:
    raw_problems = load_jsonl(args.raw_problems)
    techniques = load_techniques(args.techniques)
    rules = load_json(args.rules)
    model_cfg = load_json(args.model)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    reporter = ProgressReporter(
        enabled=not args.quiet,
        heartbeat_interval=args.progress_interval,
    )
    matcher = LLMTechniqueMatcherAgent(
        resolve_agent_model_config(model_cfg, "technique_matcher"),
        api_timeout=args.api_timeout,
    )
    designer = LLMReformulationDesignerAgent(
        resolve_agent_model_config(model_cfg, "reformulation_designer"),
        api_timeout=args.api_timeout,
    )
    quality_auditor = LLMQualityAuditAgent(
        resolve_agent_model_config(model_cfg, "quality_auditor"),
        api_timeout=args.api_timeout,
    )
    repairer = LLMRepairAgent(
        resolve_agent_model_config(model_cfg, "repair"),
        api_timeout=args.api_timeout,
    )
    reference_implementation_agent = LLMReferenceImplementationAgent(
        resolve_agent_model_config(model_cfg, "reference_implementation"),
        api_timeout=args.api_timeout,
    )
    reference_auditor = LLMReferenceAuditAgent(
        resolve_agent_model_config(model_cfg, "reference_auditor"),
        api_timeout=args.api_timeout,
    )

    plan_rows: list[JsonDict] = []
    item_rows: list[JsonDict] = []
    accepted_item_summaries: list[JsonDict] = []
    reference_records: list[JsonDict] = []
    reference_record_summaries: list[JsonDict] = []
    failed_rows: list[JsonDict] = []
    trace_rows: list[JsonDict] = []
    technique_counts: dict[str, int] = {}
    target_techniques = [item.strip() for item in args.target_techniques.split(",") if item.strip()]
    selected_problems = raw_problems[: args.limit] if args.limit else raw_problems
    run_status: JsonDict = {
        "state": "running",
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "out_dir": str(out_dir),
        "raw_problem_count": len(raw_problems),
        "selected_problem_count": len(selected_problems),
        "technique_count": len(techniques),
        "techniques_per_problem": args.techniques_per_problem,
        "repair_rounds": args.repair_rounds,
        "reference_repair_rounds": args.reference_repair_rounds,
        "reference_validation_timeout_seconds": args.reference_validation_timeout,
        "skip_reference_validation": args.skip_reference_validation,
        "api_timeout_seconds": args.api_timeout,
        "benchmark_id": args.benchmark_id,
        "questions_filename": args.questions_filename,
        "current_stage": "initializing",
        "generated_items": 0,
        "reference_packages": 0,
        "failed_items": 0,
    }

    reporter.log(
        "Run started | "
        f"sources={len(selected_problems)} | techniques={len(techniques)} | "
        f"techniques_per_problem={args.techniques_per_problem} | repair_rounds={args.repair_rounds}"
    )
    reporter.log(
        "Agent models | "
        f"matcher={_model_label(matcher)} | designer={_model_label(designer)} | "
        f"auditor={_model_label(quality_auditor)} | repair={_model_label(repairer)} | "
        f"reference_implementation={_model_label(reference_implementation_agent)} | "
        f"reference_auditor={_model_label(reference_auditor)}"
    )
    flush_incremental_outputs(
        out_dir=out_dir,
        plan_rows=plan_rows,
        item_rows=item_rows,
        failed_rows=failed_rows,
        trace_rows=trace_rows,
        run_status=run_status,
    )

    for problem_index, problem in enumerate(selected_problems, start=1):
        source_id = problem.get("source_id", "unknown_source")
        run_status.update({
            "current_stage": "technique_matching",
            "current_source_id": source_id,
            "current_problem_index": problem_index,
            "selected_problem_count": len(selected_problems),
        })
        flush_incremental_outputs(
            out_dir=out_dir,
            plan_rows=plan_rows,
            item_rows=item_rows,
            failed_rows=failed_rows,
            trace_rows=trace_rows,
            run_status=run_status,
        )
        try:
            with reporter.span(
                f"source {problem_index}/{len(selected_problems)} {source_id} | "
                f"{matcher.name} [{_model_label(matcher)}]"
            ):
                match_obj = matcher.run(
                    problem,
                    techniques,
                    rules,
                    techniques_per_problem=args.techniques_per_problem,
                )
            trace_rows.append({
                "source_id": source_id,
                "agent": matcher.name,
                "status": "ok",
                "output": match_obj,
            })
            candidates = match_obj.get("candidate_techniques", [])[: args.techniques_per_problem]
            candidate_ids = [str(candidate.get("tech_id")) for candidate in candidates]
            reporter.log(
                f"MATCHED source {problem_index}/{len(selected_problems)} {source_id} | "
                f"candidates={candidate_ids}"
            )
            flush_incremental_outputs(
                out_dir=out_dir,
                plan_rows=plan_rows,
                item_rows=item_rows,
                failed_rows=failed_rows,
                trace_rows=trace_rows,
                run_status=run_status,
            )
            if not candidates:
                failed_rows.append({
                    "source_id": source_id,
                    "error": "technique matcher returned no candidate techniques",
                })
                reporter.log(f"FAILED source {problem_index}/{len(selected_problems)} {source_id} | no candidates")
                run_status.update({
                    "current_stage": "source_failed_no_candidates",
                    "failed_items": len(failed_rows),
                })
                flush_incremental_outputs(
                    out_dir=out_dir,
                    plan_rows=plan_rows,
                    item_rows=item_rows,
                    failed_rows=failed_rows,
                    trace_rows=trace_rows,
                    run_status=run_status,
                )
                continue
            for candidate_index, candidate in enumerate(candidates, start=1):
                tech_id = str(candidate.get("tech_id"))
                run_status.update({
                    "current_stage": "candidate_generation",
                    "current_source_id": source_id,
                    "current_tech_id": tech_id,
                    "current_candidate_index": candidate_index,
                    "candidate_count_for_source": len(candidates),
                    "generated_items": len(item_rows),
                    "failed_items": len(failed_rows),
                })
                technique = techniques.get(tech_id)
                if not technique:
                    failed_rows.append({"source_id": source_id, "tech_id": tech_id, "error": "unknown technique"})
                    reporter.log(
                        f"SKIP source {problem_index}/{len(selected_problems)} {source_id} | "
                        f"candidate {candidate_index}/{len(candidates)} {tech_id} | unknown technique"
                    )
                    flush_incremental_outputs(
                        out_dir=out_dir,
                        plan_rows=plan_rows,
                        item_rows=item_rows,
                        failed_rows=failed_rows,
                        trace_rows=trace_rows,
                        run_status=run_status,
                    )
                    continue
                if technique_counts.get(tech_id, 0) >= args.max_items_per_technique:
                    reporter.log(
                        f"SKIP source {problem_index}/{len(selected_problems)} {source_id} | "
                        f"candidate {candidate_index}/{len(candidates)} {tech_id} | "
                        f"max_items_per_technique reached"
                    )
                    continue
                plan_rows.append({"source_id": source_id, "candidate": candidate})
                if args.plan_only:
                    reporter.log(
                        f"PLANNED source {problem_index}/{len(selected_problems)} {source_id} | "
                        f"candidate {candidate_index}/{len(candidates)} {tech_id}"
                    )
                    flush_incremental_outputs(
                        out_dir=out_dir,
                        plan_rows=plan_rows,
                        item_rows=item_rows,
                        failed_rows=failed_rows,
                        trace_rows=trace_rows,
                        run_status=run_status,
                    )
                    continue
                coverage_snapshot = build_coverage_snapshot(
                    plan_rows=plan_rows,
                    item_rows=item_rows,
                    failed_rows=failed_rows,
                    rules=rules,
                    target_techniques=target_techniques,
                    technique_counts=technique_counts,
                )
                item, generation_status = generate_with_feedback_loop(
                    source_problem=problem,
                    technique=technique,
                    rules=rules,
                    designer=designer,
                    quality_auditor=quality_auditor,
                    repairer=repairer,
                    accepted_item_summaries=accepted_item_summaries,
                    coverage_snapshot=coverage_snapshot,
                    repair_rounds=args.repair_rounds,
                    trace_rows=trace_rows,
                    source_id=str(source_id),
                    tech_id=tech_id,
                    reporter=reporter,
                    problem_index=problem_index,
                    problem_total=len(selected_problems),
                    candidate_index=candidate_index,
                    candidate_total=len(candidates),
                )
                if item is None:
                    failed_rows.append({
                        "source_id": source_id,
                        "tech_id": tech_id,
                        **generation_status,
                    })
                    run_status.update({
                        "current_stage": "candidate_failed",
                        "generated_items": len(item_rows),
                        "failed_items": len(failed_rows),
                    })
                    flush_incremental_outputs(
                        out_dir=out_dir,
                        plan_rows=plan_rows,
                        item_rows=item_rows,
                        failed_rows=failed_rows,
                        trace_rows=trace_rows,
                        run_status=run_status,
                    )
                    continue
                run_status.update({
                    "current_stage": "reference_generation",
                    "current_problem_id": item.get("problem_id"),
                    "generated_items": len(item_rows),
                    "reference_packages": len(reference_records),
                    "failed_items": len(failed_rows),
                })
                flush_incremental_outputs(
                    out_dir=out_dir,
                    plan_rows=plan_rows,
                    item_rows=item_rows,
                    failed_rows=failed_rows,
                    trace_rows=trace_rows,
                    run_status=run_status,
                    reference_rows=reference_record_summaries,
                )
                reference_record, reference_status = generate_reference_with_feedback_loop(
                    item=item,
                    source_problem=problem,
                    technique=technique,
                    rules=rules,
                    reference_implementation_agent=reference_implementation_agent,
                    reference_auditor=reference_auditor,
                    out_dir=out_dir,
                    reference_repair_rounds=args.reference_repair_rounds,
                    reference_validation_timeout=args.reference_validation_timeout,
                    skip_reference_validation=args.skip_reference_validation,
                    questions_filename=args.questions_filename,
                    trace_rows=trace_rows,
                    source_id=str(source_id),
                    tech_id=tech_id,
                    reporter=reporter,
                    problem_index=problem_index,
                    problem_total=len(selected_problems),
                    candidate_index=candidate_index,
                    candidate_total=len(candidates),
                )
                if reference_record is None:
                    failed_rows.append({
                        "source_id": source_id,
                        "tech_id": tech_id,
                        "problem_id": item.get("problem_id"),
                        "phase": "reference_generation",
                        **reference_status,
                    })
                    run_status.update({
                        "current_stage": "reference_failed",
                        "generated_items": len(item_rows),
                        "reference_packages": len(reference_records),
                        "failed_items": len(failed_rows),
                    })
                    flush_incremental_outputs(
                        out_dir=out_dir,
                        plan_rows=plan_rows,
                        item_rows=item_rows,
                        failed_rows=failed_rows,
                        trace_rows=trace_rows,
                        run_status=run_status,
                        reference_rows=reference_record_summaries,
                    )
                    continue
                reference_records.append(reference_record)
                reference_record_summaries.append(_reference_record_summary(reference_record))
                item_rows.append(item)
                accepted_item_summaries.append(summarize_item_for_audit(item))
                technique_counts[tech_id] = technique_counts.get(tech_id, 0) + 1
                run_status.update({
                    "current_stage": "candidate_and_reference_accepted",
                    "generated_items": len(item_rows),
                    "reference_packages": len(reference_records),
                    "failed_items": len(failed_rows),
                    "technique_counts": technique_counts,
                    "last_accepted_problem_id": item.get("problem_id"),
                })
                flush_incremental_outputs(
                    out_dir=out_dir,
                    plan_rows=plan_rows,
                    item_rows=item_rows,
                    failed_rows=failed_rows,
                    trace_rows=trace_rows,
                    run_status=run_status,
                    reference_rows=reference_record_summaries,
                )
        except (LLMClientError, FrameworkError, json.JSONDecodeError, KeyError, TypeError) as exc:
            trace_rows.append({
                "source_id": source_id,
                "agent": "batch_orchestration",
                "status": "fail",
                "error": str(exc),
            })
            failed_rows.append({"source_id": source_id, "error": str(exc)})
            reporter.log(
                f"FAILED source {problem_index}/{len(selected_problems)} {source_id} | batch error: {exc}"
            )
            run_status.update({
                "current_stage": "source_failed",
                "generated_items": len(item_rows),
                "failed_items": len(failed_rows),
                "last_error": str(exc),
            })
            flush_incremental_outputs(
                out_dir=out_dir,
                plan_rows=plan_rows,
                item_rows=item_rows,
                failed_rows=failed_rows,
                trace_rows=trace_rows,
                run_status=run_status,
            )

    coverage = build_coverage_snapshot(
        plan_rows=plan_rows,
        item_rows=item_rows,
        failed_rows=failed_rows,
        rules=rules,
        target_techniques=target_techniques,
        technique_counts=technique_counts,
    )
    if not args.plan_only and not args.skip_final_review:
        try:
            run_status.update({
                "current_stage": "final_batch_review",
                "generated_items": len(item_rows),
                "failed_items": len(failed_rows),
            })
            flush_incremental_outputs(
                out_dir=out_dir,
                plan_rows=plan_rows,
                item_rows=item_rows,
                failed_rows=failed_rows,
                trace_rows=trace_rows,
                run_status=run_status,
            )
            with reporter.span(f"final batch review | {quality_auditor.name} [{_model_label(quality_auditor)}]"):
                coverage["llm_batch_review"] = quality_auditor.review_batch(
                    item_summaries=accepted_item_summaries,
                    failed_rows=failed_rows,
                    rules=rules,
                    target_techniques=target_techniques,
                    coverage_snapshot=coverage,
                )
        except (LLMClientError, FrameworkError, json.JSONDecodeError, KeyError, TypeError) as exc:
            coverage["llm_batch_review_error"] = str(exc)
            reporter.log(f"FINAL_REVIEW_FAILED {exc}")
    run_status.update({
        "state": "finished",
        "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "current_stage": "finished",
        "generated_items": len(item_rows),
        "reference_packages": len(reference_records),
        "failed_items": len(failed_rows),
        "planned_items": len(plan_rows),
        "technique_counts": technique_counts,
    })
    if not args.plan_only:
        bundle_manifest = write_bundle_outputs(
            out_dir=out_dir,
            item_rows=item_rows,
            reference_records=reference_records,
            failed_rows=failed_rows,
            rules=rules,
            benchmark_id=args.benchmark_id,
            questions_filename=args.questions_filename,
        )
        run_status["bundle_manifest"] = bundle_manifest
    flush_incremental_outputs(
        out_dir=out_dir,
        plan_rows=plan_rows,
        item_rows=item_rows,
        failed_rows=failed_rows,
        trace_rows=trace_rows,
        run_status=run_status,
        reference_rows=reference_record_summaries,
    )
    (out_dir / "coverage_report.json").write_text(
        json.dumps(coverage, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    reporter.log(
        "Run finished | "
        f"planned={len(plan_rows)} | accepted={len(item_rows)} | failed={len(failed_rows)}"
    )
    reporter.log(f"Wrote plan to {out_dir / 'batch_plan.jsonl'}")
    reporter.log(f"Wrote reformulated items to {out_dir / 'reformulated_items.jsonl'}")
    reporter.log(f"Wrote agent trace to {out_dir / 'agent_trace.jsonl'}")
    reporter.log(f"Wrote failed items to {out_dir / 'failed_items.jsonl'}")
    reporter.log(f"Wrote coverage report to {out_dir / 'coverage_report.json'}")
    reporter.log(f"Wrote live run status to {out_dir / 'run_status.json'}")
    if not args.plan_only:
        reporter.log(f"Wrote blind questions to {out_dir / 'questions' / args.questions_filename}")
        reporter.log(f"Wrote human reference tree to {out_dir / 'human_reference' / 'accepted'}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LLM-driven batch reformulation agent.")
    parser.add_argument("--raw-problems", default="optdachshund/data/source_benchmarks/raw_problem_inputs.jsonl")
    parser.add_argument("--techniques", default="optdachshund/data/techniques/techniques.json")
    parser.add_argument("--rules", default="optdachshund/configs/reformulation_rules.json")
    parser.add_argument("--model", default="optdachshund/configs/reformulation_model.json")
    parser.add_argument("--out-dir", default="optdachshund/outputs/reformulated_benchmark")
    parser.add_argument("--benchmark-id", default="optdachshund_llm_multi_agent")
    parser.add_argument("--questions-filename", default="efficientopt_blind.jsonl")
    parser.add_argument("--techniques-per-problem", type=int, default=3)
    parser.add_argument("--max-items-per-technique", type=int, default=999999)
    parser.add_argument("--target-techniques", default="", help="Comma-separated technique ids that must satisfy coverage.")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--api-timeout", type=int, default=180)
    parser.add_argument("--repair-rounds", type=int, default=2, help="LLM repair rounds per generated item.")
    parser.add_argument("--reference-repair-rounds", type=int, default=2, help="LLM repair rounds per generated reference package.")
    parser.add_argument("--reference-validation-timeout", type=int, default=300, help="Seconds allowed for each local validate.py run.")
    parser.add_argument("--skip-reference-validation", action="store_true", help="Write reference files without running local validate.py.")
    parser.add_argument("--skip-final-review", action="store_true", help="Skip final LLM batch coverage/diversity review.")
    parser.add_argument(
        "--progress-interval",
        type=int,
        default=30,
        help="Seconds between heartbeat messages while waiting for a long LLM call. Use 0 to disable heartbeats.",
    )
    parser.add_argument("--quiet", action="store_true", help="Disable command-line progress messages.")
    parser.add_argument("--plan-only", action="store_true")
    return parser


def main() -> None:
    run_batch(build_parser().parse_args())


if __name__ == "__main__":
    main()
