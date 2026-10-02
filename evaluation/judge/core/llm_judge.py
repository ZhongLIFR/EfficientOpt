from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .classifier import classify_candidate


def split_document(text: str, chunk_chars: int) -> list[str]:
    if chunk_chars <= 0:
        raise ValueError("chunk_chars must be positive")
    return [text[start : start + chunk_chars] for start in range(0, len(text), chunk_chars)] or [""]


def _resolve_key(config: dict[str, Any], config_path: str | Path | None = None) -> str:
    direct = str(config.get("api_key") or "").strip()
    if direct:
        return direct
    env_name = str(config.get("api_key_env") or "").strip()
    if env_name and os.environ.get(env_name):
        return os.environ[env_name]
    source = config.get("api_key_from_model_config")
    if not source:
        raise RuntimeError("Judge API key is not configured.")
    source_path = Path(str(source))
    if not source_path.is_absolute() and config_path:
        source_path = Path(config_path).resolve().parent / source_path
    data = json.loads(source_path.read_text(encoding="utf-8"))
    models = data.get("models") if isinstance(data, dict) else data
    preferred = str(config.get("api_key_model_name") or "")
    if isinstance(models, list):
        candidates = [row for row in models if isinstance(row, dict)]
        for row in candidates:
            if preferred and row.get("name") == preferred and row.get("api_key"):
                return str(row["api_key"])
        for row in candidates:
            if row.get("api_key"):
                return str(row["api_key"])
    raise RuntimeError("No judge API key found in the configured model file.")


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start < 0 or end <= start:
            raise
        value = json.loads(cleaned[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("Judge response is not a JSON object.")
    return value


def merge_llm_judgement(hard_result: dict[str, Any], llm_result: dict[str, Any]) -> dict[str, Any]:
    hard_value = hard_result.get("hard_category", hard_result.get("category"))
    hard_category = int(hard_value) if hard_value is not None else None
    raw_category = llm_result.get("category")
    try:
        llm_category = int(raw_category)
    except (TypeError, ValueError):
        llm_category = None

    merged = dict(hard_result)
    merged["llm_category"] = llm_category
    merged["llm_judgement"] = llm_result
    merged["llm_manual_review"] = bool(llm_result.get("recommended_manual_review", False))
    merged["llm_efficiency_verdict"] = llm_result.get("efficiency_verdict")
    merged["efficiency_verdict"] = hard_result.get("efficiency_verdict", "unavailable")
    technique_match = str(llm_result.get("technique_match") or "").lower()
    if hard_category == 5:
        merged["category"] = 5
        merged["category_label"] = "solve_error"
        merged["hard_gate_applied"] = True
    elif hard_result.get("objective_validation_status") == "unknown":
        # Technique attribution cannot establish a missing numerical correctness target.
        merged["category"] = None
        merged["category_label"] = "needs_manual_review"
        merged["hard_gate_applied"] = False
        merged["manual_review"] = True
    elif technique_match == "target":
        merged["category"] = 1
        merged["category_label"] = {
            1: "target_technique",
        }[1]
        merged["hard_gate_applied"] = False
    elif technique_match == "alternative" and merged["efficiency_verdict"] == "good":
        merged["category"] = 2
        merged["category_label"] = "alternative_technique_efficient"
        merged["hard_gate_applied"] = False
    elif technique_match == "alternative" and merged["efficiency_verdict"] == "poor":
        merged["category"] = 3
        merged["category_label"] = "alternative_technique_inefficient"
        merged["hard_gate_applied"] = False
    elif technique_match in {"none", "not_applicable"}:
        merged["category"] = 4
        merged["category_label"] = "correct_without_meaningful_technique"
        merged["hard_gate_applied"] = False
    elif llm_category in {1, 2, 3, 4} and technique_match == "":
        # Backward-compatible fallback for older judge responses that omitted technique_match.
        merged["category"] = llm_category if llm_category != 2 or merged["efficiency_verdict"] == "good" else None
        merged["category_label"] = {
            1: "target_technique",
            2: "alternative_technique_efficient",
            3: "alternative_technique_inefficient",
            4: "correct_without_meaningful_technique",
        }.get(merged["category"], "unjudged")
        merged["hard_gate_applied"] = False
    else:
        merged["category"] = None
        merged["category_label"] = "unjudged"
        merged["hard_gate_applied"] = False
        merged["manual_review"] = True
    merged["hard_gate_conflict"] = hard_category == 5 and llm_category not in {None, 5}
    merged["manual_review"] = bool(
        merged.get("manual_review", False)
        or merged["llm_manual_review"]
        or merged["hard_gate_conflict"]
        or merged.get("category") is None
    )
    return merged


def build_judge_messages(bundle: dict[str, Any], hard_result: dict[str, Any]) -> list[dict[str, str]]:
    candidate = bundle.get("candidate") or {}
    technique = bundle.get("technique") or {}
    prompt = {
        "task": "Classify one completed optimization-modeling result into exactly one of five categories.",
        "categories": {
            "1": "Correct result and actual semantic use of the predefined technique; equivalent implementations count.",
            "2": "No predefined technique, but another valid modeling technique and good efficiency.",
            "3": "No predefined technique, another technique is present, but efficiency is poor.",
            "4": "Correct result without a meaningful optimization technique.",
            "5": "Solve/model error, infeasible or wrong objective, non-executable code, or answer-only shortcut.",
        },
        "hard_gate": "If hard_verification indicates a code, solver, feasibility, timeout, or objective failure, assign category 5 even if the proposed technique sounds plausible.",
        "efficiency_policy": "Use the deterministic runtime rule: good means candidate_runtime/expert_runtime <= 1.5, or (1.5 < ratio < 2.0 and candidate_runtime/ordinary_runtime <= 0.8); poor means candidate_runtime/expert_runtime >= 2.0 or candidate_runtime >= ordinary_runtime; otherwise efficiency is unavailable and categories 2/3 must not be assigned.",
        "semantic_equivalence_policy": "Judge the technique idea, not literal code matching. Native solver support and mathematically equivalent formulations count when they implement the same idea. The target technique's listed semantic_equivalents are all valid target implementations.",
        "static_analysis_policy": "No regex-based technique classification is supplied. Do not infer technique use from isolated keywords. Inspect the mathematical structure, variable roles, constraints, transformations, solver constructs, and executable code.",
        "problem_id": bundle.get("problem_id"),
        "problem_statement": str(bundle.get("problem_statement") or ""),
        "target_technique": technique,
        "candidate": {
            "solver_status": candidate.get("solver_status"),
            "objective_correct": candidate.get("objective_correct"),
            "objective_correct_independent": hard_result.get("objective_correct_independent"),
            "returncode": candidate.get("returncode"),
            "notes": candidate.get("notes"),
            "solver_runtime_seconds": candidate.get("solver_runtime_seconds"),
            "work_units": candidate.get("work_units"),
            "num_variables": candidate.get("num_variables"),
            "num_constraints": candidate.get("num_constraints"),
            "num_nonzeros": candidate.get("num_nonzeros"),
            "memory_peak_mb": candidate.get("memory_peak_mb"),
            "code_total_chars": len(str(candidate.get("candidate_code") or "")),
            "formulation_summary": candidate.get("formulation_summary"),
            "code": str(candidate.get("candidate_code") or ""),
        },
        "baselines": {
            "ordinary": bundle.get("ordinary_baseline"),
            "predefined_technique": bundle.get("technique_baseline"),
        },
        "reference_implementations": {
            "ordinary_code": str(bundle.get("ordinary_reference_code") or ""),
            "technique_code": str(bundle.get("technique_reference_code") or ""),
        },
        "code_review_observations": bundle.get("code_review_observations", []),
        "hard_verification": {
            "hard_failure_reason": hard_result.get("hard_failure_reason"),
            "failure_reasons": hard_result.get("failure_reasons", []),
            "objective_correct_independent": hard_result.get("objective_correct_independent"),
            "objective_validation_source": hard_result.get("objective_validation_source"),
            "solver_status": candidate.get("solver_status"),
        },
        "technique_catalog": bundle.get("technique_catalog", []),
        "context_status": bundle.get("context_status", {}),
        "missing_context": bundle.get("missing_context", []),
        "reference_objective": (bundle.get("reference") or {}).get("objective"),
        "reference_tolerance": (bundle.get("reference") or {}).get("relative_tolerance"),
        "hidden_reference_formulation": str(bundle.get("reference_formulation") or ""),
        "required_output": {
            "category": "integer 1-5",
            "technique_match": "target | alternative | none | not_applicable",
            "target_technique_name": "string or none",
            "alternative_technique_name": "string or none",
            "efficiency_verdict": "good | poor | uncertain",
            "evidence": ["short structural evidence strings"],
            "brief_reason": "short reason",
            "confidence": "number 0-1",
            "recommended_manual_review": "boolean",
        },
    }
    system = (
        "You are a strict optimization-modeling judge. Return only valid JSON. "
        "Do not reward technique names without structural implementation."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
    ]


def build_code_reader_messages(
    bundle: dict[str, Any],
    document_name: str,
    chunk_index: int,
    chunk_count: int,
    chunk_text: str,
) -> list[dict[str, str]]:
    payload = {
        "task": "Read this complete code chunk as part of an optimization-modeling solution. Extract structural facts only; do not assign a final category.",
        "problem_id": bundle.get("problem_id"),
        "target_technique": bundle.get("technique", {}),
        "document_name": document_name,
        "chunk_index": chunk_index,
        "chunk_count": chunk_count,
        "code_chunk": chunk_text,
        "required_output": {
            "structural_observations": ["variables, constraints, transformations, solver constructs, decomposition or algorithm structure"],
            "technique_candidates": ["possible technique IDs/names with code evidence"],
            "uncertainties": ["facts that cannot be established from this chunk"],
        },
    }
    return [
        {"role": "system", "content": "You are a code-reading assistant for an optimization-modeling judge. Return only JSON and never infer a final score from keywords alone."},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


def call_judge_api(
    config: dict[str, Any],
    messages: list[dict[str, str]],
    *,
    config_path: str | Path | None = None,
    timeout_seconds: int = 180,
) -> dict[str, Any]:
    key = _resolve_key(config, config_path)
    base_url = str(config.get("base_url") or "").strip()
    if not base_url:
        env_name = str(config.get("base_url_env") or "").strip()
        base_url = os.environ.get(env_name, "").strip() if env_name else ""
    base_url = base_url.rstrip("/")
    if not base_url:
        raise RuntimeError("Judge base_url is empty.")
    payload: dict[str, Any] = {
        "model": config["model"],
        "messages": messages,
        "temperature": config.get("temperature", 0.0),
        "max_tokens": config.get("max_tokens", 1200),
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Judge HTTP {exc.code}: {body[:500]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Judge URL error: {exc}") from exc
    choice = (data.get("choices") or [{}])[0]
    content = ((choice.get("message") or {}).get("content") or "")
    return {
        "parsed": _extract_json(content),
        "latency_seconds": time.perf_counter() - started,
        "usage": data.get("usage", {}),
        "model": config.get("model"),
    }


def judge_bundle(
    bundle: dict[str, Any],
    config: dict[str, Any],
    *,
    config_path: str | Path | None = None,
    timeout_seconds: int = 180,
    max_direct_code_chars: int = 24000,
    code_chunk_chars: int = 12000,
) -> dict[str, Any]:
    context = {
        "problem_id": bundle.get("problem_id"),
        "technique": bundle.get("technique"),
        "candidate": bundle.get("candidate"),
        "ordinary_baseline": bundle.get("ordinary_baseline"),
        "technique_baseline": bundle.get("technique_baseline"),
        "reference": bundle.get("reference"),
        "reference_source": bundle.get("reference_source"),
    }
    hard = classify_candidate(context)
    documents = {
        "candidate_code": str((bundle.get("candidate") or {}).get("candidate_code") or ""),
        "ordinary_reference_code": str(bundle.get("ordinary_reference_code") or ""),
        "technique_reference_code": str(bundle.get("technique_reference_code") or ""),
    }
    total_chars = sum(len(text) for text in documents.values())
    code_reviews: list[dict[str, Any]] = []
    code_read_mode = "direct"
    code_review_calls = 0
    judge_bundle_payload = dict(bundle)
    if total_chars > max_direct_code_chars:
        code_read_mode = "chunked_llm_review"
        for document_name, document_text in documents.items():
            chunks = split_document(document_text, code_chunk_chars)
            for index, chunk in enumerate(chunks, start=1):
                review_response = call_judge_api(
                    config,
                    build_code_reader_messages(bundle, document_name, index, len(chunks), chunk),
                    config_path=config_path,
                    timeout_seconds=timeout_seconds,
                )
                code_reviews.append({
                    "document_name": document_name,
                    "chunk_index": index,
                    "chunk_count": len(chunks),
                    "review": review_response.get("parsed", {}),
                })
                code_review_calls += 1
        judge_bundle_payload["code_review_observations"] = code_reviews
        candidate_without_code = dict(judge_bundle_payload.get("candidate") or {})
        candidate_without_code["candidate_code"] = ""
        judge_bundle_payload["candidate"] = candidate_without_code
        judge_bundle_payload["ordinary_reference_code"] = ""
        judge_bundle_payload["technique_reference_code"] = ""
    judge_bundle_payload["code_read_mode"] = code_read_mode
    judge_bundle_payload["code_documents"] = {
        name: {"chars": len(text), "chunked": code_read_mode == "chunked_llm_review"}
        for name, text in documents.items()
    }
    messages = build_judge_messages(judge_bundle_payload, hard)
    response = call_judge_api(config, messages, config_path=config_path, timeout_seconds=timeout_seconds)
    result = merge_llm_judgement(hard, response["parsed"])
    result.update({
        "problem_id": bundle.get("problem_id"),
        "model_name": bundle.get("model_name"),
        "llm_latency_seconds": response.get("latency_seconds"),
        "llm_usage": response.get("usage", {}),
        "judge_model": response.get("model"),
        "code_read_mode": code_read_mode,
        "code_review_calls": code_review_calls,
        "code_documents": judge_bundle_payload["code_documents"],
    })
    return result
