from __future__ import annotations

import json
from typing import Any

from .llm_client import call_openai_compatible_chat, extract_json

JsonDict = dict[str, Any]


class FrameworkError(RuntimeError):
    pass


REFORMULATED_ITEM_SCHEMA: JsonDict = {
    "problem_id": "EffiOpt_<tech_id>_<source_id>_<short_suffix>",
    "source": {
        "source_id": "string",
        "dataset": "string",
        "split": "string",
        "source_question": "string",
        "source_answer": "string",
    },
    "target_technique": "technique object",
    "natural_language_problem": "new English problem statement; do not reveal technique name",
    "natural_language_answer": "plain-language answer to the new problem",
    "source_trace": {
        "kept": ["at least three source elements"],
        "changed": ["what was changed"],
    },
    "mathematical_model": {
        "sets": ["index sets, if any"],
        "parameters": ["named data and constants"],
        "decision_variables": ["variables with domains and meanings"],
        "objective": {
            "sense": "minimize | maximize",
            "expression": "mathematical objective expression",
        },
        "constraints": [
            {
                "name": "constraint name",
                "expression": "mathematical constraint expression",
                "meaning": "business or modeling interpretation",
            }
        ],
        "variable_domains": ["domain declarations"],
        "solution": "optimal solution mapped to variables",
    },
    "technique_solution": {
        "technique_use": "how the target technique is used",
        "formulation": "math formulation",
        "derivation": "concise derivation",
        "answer": "numeric or structured answer",
        "efficiency_advantage": "why this should be faster/better",
    },
    "verification": {
        "pass": True,
        "feasibility_check": "string",
        "optimality_check": "string",
        "answer_check": "string",
        "notes": "string",
    },
    "efficiency_profile": {
        "expected_general_llm_failure": "string",
        "efficiency_signals": ["strings"],
        "suggested_metrics": ["strings"],
    },
    "diversity_profile": {
        "novelty_axis": "changed domain / variable structure / constraint structure / scale / uncertainty / network-time pattern",
        "source_template_changes": ["specific changes that prevent simple number substitution"],
        "anti_template_notes": "why the new item is not merely the source problem with different numbers",
    },
    "hidden_metadata": {
        "do_not_show_to_candidate_model": ["target_technique", "technique_solution"]
    },
}


REFERENCE_IMPLEMENTATION_SCHEMA: JsonDict = {
    "problem_id": "same as reformulated item",
    "instance_json": {
        "description": "fixed public instance data; use only JSON-serializable values",
        "data": "object or array used by both reference models",
    },
    "problem_md": "public problem statement text; must match natural_language_problem",
    "ordinary_model_py": "complete Python source for a valid but intentionally ordinary/general formulation",
    "technique_model_py": "complete Python source for the target-technique reference formulation",
    "validate_py": "complete Python source that runs ordinary_model.py and technique_model.py twice, checks objective agreement, feasibility, runtime, work, and writes validation.json",
    "validation_json": {
        "optional": "only include if the value can be derived without executing code; otherwise validate.py writes it",
        "required_runtime_fields": [
            "objective_value",
            "solver_runtime_seconds",
            "code_run_time_seconds",
            "work_units",
            "num_variables",
            "num_constraints",
        ],
    },
    "review_md": "short review explaining the ordinary formulation, technique formulation, expected efficiency contrast, and validation assumptions",
    "reference_metadata": {
        "reference_objective_value": "numeric optimum if known",
        "ordinary_modeling_pattern": "what makes ordinary model slower or less structured",
        "technique_modeling_pattern": "how the target technique is used",
        "expected_efficiency_metrics": ["solver_runtime_seconds", "work_units", "num_variables", "num_constraints", "num_nonzeros"],
    },
}


def llm_metadata(model_cfg: JsonDict, response: JsonDict) -> JsonDict:
    return {
        "model": model_cfg.get("model"),
        "model_config_name": model_cfg.get("name"),
        "latency_seconds": response.get("latency_seconds"),
        "finish_reason": response.get("finish_reason"),
        "usage": response.get("usage", {}),
    }


def summarize_techniques(techniques: dict[str, JsonDict]) -> list[JsonDict]:
    return [
        {
            "tech_id": item["tech_id"],
            "name": item.get("name"),
            "chinese_name": item.get("chinese_name"),
            "category": item.get("category"),
            "core_idea": item.get("core_idea"),
            "core_idea_cn": item.get("core_idea_cn"),
            "low_efficiency_symptoms": item.get("low_efficiency_symptoms", []),
            "low_efficiency_symptoms_cn": item.get("low_efficiency_symptoms_cn", []),
            "expert_actions": item.get("expert_actions", []),
            "expert_actions_cn": item.get("expert_actions_cn", []),
            "benchmark_pattern": item.get("benchmark_pattern"),
            "benchmark_usage_cn": item.get("benchmark_usage_cn"),
            "applicable_examples_cn": item.get("applicable_examples_cn"),
            "math_model_example": item.get("math_model_example"),
            "math_model_audit": item.get("math_model_audit"),
        }
        for item in techniques.values()
    ]


def summarize_item_for_audit(item: JsonDict) -> JsonDict:
    target = item.get("target_technique") or {}
    return {
        "problem_id": item.get("problem_id"),
        "source_id": (item.get("source") or {}).get("source_id"),
        "tech_id": target.get("tech_id"),
        "technique_name": target.get("name"),
        "problem_statement": item.get("natural_language_problem"),
        "novelty_axis": (item.get("diversity_profile") or {}).get("novelty_axis"),
    }


class LLMTechniqueMatcherAgent:
    """Backbone-LLM agent that maps one raw problem to multiple useful techniques."""

    name = "LLM Technique Matcher Agent"

    def __init__(self, model_cfg: JsonDict, api_timeout: int = 180):
        self.model_cfg = model_cfg
        self.api_timeout = api_timeout

    def build_messages(
        self,
        source_problem: JsonDict,
        techniques: dict[str, JsonDict],
        rules: JsonDict,
        techniques_per_problem: int,
    ) -> list[JsonDict]:
        return [
            {
                "role": "system",
                "content": (
                    "You are the Technique Matching Agent in a multi-agent framework for "
                    "optimization-modeling benchmark reformulation. Select suitable "
                    "OptTips techniques for one raw benchmark problem. Return only valid JSON."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "source_problem": source_problem,
                        "required_candidate_count": techniques_per_problem,
                        "technique_matching_rules": rules.get("technique_matching_rules", {}),
                        "coverage_rules": rules.get("coverage_rules", {}),
                        "available_techniques": summarize_techniques(techniques),
                        "output_schema": {
                            "source_id": "string",
                            "candidate_techniques": [
                                {
                                    "tech_id": "Txx",
                                    "fit_score": 0.0,
                                    "reason": "why this source naturally supports this technique",
                                    "expected_general_llm_failure": "e.g. enumeration, loose Big-M, no dualization",
                                    "transformation_operator": "short operator name"
                                }
                            ]
                        },
                    },
                    ensure_ascii=False,
                ),
            },
        ]

    def run(
        self,
        source_problem: JsonDict,
        techniques: dict[str, JsonDict],
        rules: JsonDict,
        techniques_per_problem: int,
    ) -> JsonDict:
        response = call_openai_compatible_chat(
            self.model_cfg,
            self.build_messages(source_problem, techniques, rules, techniques_per_problem),
            timeout_seconds=self.api_timeout,
        )
        result = extract_json(response["content"])
        if not isinstance(result, dict):
            raise FrameworkError("Technique matcher did not return a JSON object.")
        result["_agent"] = self.name
        result["_llm"] = llm_metadata(self.model_cfg, response)
        return result


class LLMReformulationDesignerAgent:
    """Backbone-LLM agent that generates one technique-targeted reformulated item."""

    name = "LLM Reformulation Designer Agent"

    def __init__(self, model_cfg: JsonDict, api_timeout: int = 180):
        self.model_cfg = model_cfg
        self.api_timeout = api_timeout

    def build_messages(
        self,
        source_problem: JsonDict,
        technique: JsonDict,
        rules: JsonDict,
        revision_context: JsonDict | None = None,
    ) -> list[JsonDict]:
        payload: JsonDict = {
            "source_problem": source_problem,
            "target_technique": technique,
            "rules": rules,
            "output_schema": REFORMULATED_ITEM_SCHEMA,
        }
        if revision_context:
            payload["revision_context"] = revision_context
        return [
            {
                "role": "system",
                "content": (
                    "You are the Reformulation Designer Agent in a multi-agent benchmark "
                    "construction framework. Create one efficiency-sensitive optimization "
                    "problem from the raw source problem and target technique. Do not create "
                    "a naive/expert pair. Generate the technique-based solution, validation, "
                    "efficiency signals, and diversity evidence. Avoid shallow reformulation: "
                    "do not merely change numbers or copy the original template. Use the "
                    "target technique's math_model_example as modeling guidance, but create "
                    "a new problem-specific mathematical_model instead of copying the example. "
                    "Return only valid JSON."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(payload, ensure_ascii=False),
            },
        ]

    def run(
        self,
        source_problem: JsonDict,
        technique: JsonDict,
        rules: JsonDict,
        revision_context: JsonDict | None = None,
    ) -> JsonDict:
        response = call_openai_compatible_chat(
            self.model_cfg,
            self.build_messages(source_problem, technique, rules, revision_context=revision_context),
            timeout_seconds=self.api_timeout,
        )
        result = extract_json(response["content"])
        if not isinstance(result, dict):
            raise FrameworkError("Reformulation designer did not return a JSON object.")
        result["_agent"] = self.name
        result["_llm"] = llm_metadata(self.model_cfg, response)
        return result


class LLMQualityAuditAgent:
    """LLM agent that reviews item quality, uniqueness, and technique alignment."""

    name = "LLM Quality Audit Agent"

    def __init__(self, model_cfg: JsonDict, api_timeout: int = 180):
        self.model_cfg = model_cfg
        self.api_timeout = api_timeout

    def build_messages(
        self,
        source_problem: JsonDict,
        technique: JsonDict,
        candidate_item: JsonDict,
        rules: JsonDict,
        accepted_item_summaries: list[JsonDict],
        coverage_snapshot: JsonDict,
    ) -> list[JsonDict]:
        return [
            {
                "role": "system",
                "content": (
                    "You are the Quality Audit Agent in an LLM multi-agent benchmark "
                    "construction framework. You are the single LLM reviewer for generated "
                    "items. Review mathematical correctness, schema completeness, traceability, "
                    "technique alignment, leakage of technique names, duplicate risk, coverage "
                    "contribution, diversity, and whether the top-level mathematical_model is "
                    "consistent with the natural language problem and answer. Reject shallow "
                    "rewrites that merely copy the source template with changed numbers. Return only valid JSON."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "source_problem": source_problem,
                        "target_technique": technique,
                        "candidate_item": candidate_item,
                        "rules": rules,
                        "accepted_item_summaries": accepted_item_summaries,
                        "coverage_snapshot": coverage_snapshot,
                        "audit_policy": {
                            "reject_if_technique_name_leaks_in_problem": True,
                            "reject_if_missing_solution_or_verification": True,
                            "reject_if_missing_natural_language_answer": True,
                            "reject_if_missing_or_inconsistent_mathematical_model": True,
                            "reject_if_math_validation_is_weak": True,
                            "reject_if_target_technique_is_only_mentioned_but_not_structural": True,
                            "reject_if_duplicate_or_near_duplicate_of_accepted_item": True,
                            "reject_if_reformulation_is_only_number_substitution": True,
                            "coverage_is_advisory_not_a_hard_failure": True,
                        },
                        "output_schema": {
                            "pass": True,
                            "issues": ["specific issue strings; empty if pass"],
                            "repair_instructions": ["actionable revision steps; empty if pass"],
                            "schema_and_leakage": {
                                "score": 0.0,
                                "reason": "required fields, forbidden fields, and technique-name leakage",
                            },
                            "technique_alignment": {
                                "score": 0.0,
                                "reason": "why the target technique is or is not central",
                            },
                            "math_validation": {
                                "score": 0.0,
                                "reason": "feasibility and optimality concerns",
                            },
                            "mathematical_model_check": {
                                "score": 0.0,
                                "reason": "model variables, objective, constraints, domains, and solution consistency",
                            },
                            "novelty_and_traceability": {
                                "score": 0.0,
                                "reason": "source elements kept and modifications made",
                            },
                            "duplicate_and_diversity": {
                                "score": 0.0,
                                "reason": "similarity to source template and accepted items",
                            },
                            "coverage_advice": {
                                "tech_id": "Txx",
                                "contributes_to_undercovered_technique": True,
                                "reason": "coverage is advice only, not a hard rejection by itself",
                            },
                        },
                    },
                    ensure_ascii=False,
                ),
            },
        ]

    def run(
        self,
        source_problem: JsonDict,
        technique: JsonDict,
        candidate_item: JsonDict,
        rules: JsonDict,
        accepted_item_summaries: list[JsonDict],
        coverage_snapshot: JsonDict,
    ) -> JsonDict:
        response = call_openai_compatible_chat(
            self.model_cfg,
            self.build_messages(
                source_problem,
                technique,
                candidate_item,
                rules,
                accepted_item_summaries,
                coverage_snapshot,
            ),
            timeout_seconds=self.api_timeout,
        )
        result = extract_json(response["content"])
        if not isinstance(result, dict):
            raise FrameworkError("Quality auditor did not return a JSON object.")
        result["_agent"] = self.name
        result["_llm"] = llm_metadata(self.model_cfg, response)
        return result

    def build_batch_review_messages(
        self,
        item_summaries: list[JsonDict],
        failed_rows: list[JsonDict],
        rules: JsonDict,
        target_techniques: list[str],
        coverage_snapshot: JsonDict,
    ) -> list[JsonDict]:
        return [
            {
                "role": "system",
                "content": (
                    "You are the final Quality Audit Agent for an incremental benchmark "
                    "construction run. Review the batch after generation. Coverage is advisory: "
                    "do not fail the run only because not every technique has enough items. "
                    "Instead, identify gaps, diversity risks, and next-source selection advice. "
                    "Return only valid JSON."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "accepted_item_summaries": item_summaries,
                        "failed_items": failed_rows,
                        "rules": rules,
                        "target_techniques": target_techniques,
                        "coverage_snapshot": coverage_snapshot,
                        "output_schema": {
                            "overall_status": "acceptable | needs_more_generation | needs_manual_review",
                            "coverage_advisory": {
                                "undercovered_techniques": ["Txx"],
                                "notes": "coverage gaps are not hard failures for incremental runs",
                            },
                            "diversity_advisory": {
                                "risks": ["template repetition / narrow source family / weak technique contrast"],
                                "recommended_next_sources": ["what kinds of raw problems to add next"],
                            },
                            "quality_risks": ["specific risks for manual review"],
                            "next_actions": ["concrete next generation or review actions"],
                        },
                    },
                    ensure_ascii=False,
                ),
            },
        ]

    def review_batch(
        self,
        item_summaries: list[JsonDict],
        failed_rows: list[JsonDict],
        rules: JsonDict,
        target_techniques: list[str],
        coverage_snapshot: JsonDict,
    ) -> JsonDict:
        response = call_openai_compatible_chat(
            self.model_cfg,
            self.build_batch_review_messages(
                item_summaries,
                failed_rows,
                rules,
                target_techniques,
                coverage_snapshot,
            ),
            timeout_seconds=self.api_timeout,
        )
        result = extract_json(response["content"])
        if not isinstance(result, dict):
            raise FrameworkError("Batch quality review did not return a JSON object.")
        result["_agent"] = self.name
        result["_llm"] = llm_metadata(self.model_cfg, response)
        return result


class LLMRepairAgent:
    """LLM agent that repairs rejected reformulated items using explicit feedback."""

    name = "LLM Repair Agent"

    def __init__(self, model_cfg: JsonDict, api_timeout: int = 180):
        self.model_cfg = model_cfg
        self.api_timeout = api_timeout

    def build_messages(
        self,
        source_problem: JsonDict,
        technique: JsonDict,
        rejected_item: JsonDict,
        rules: JsonDict,
        feedback: JsonDict,
        repair_round: int,
    ) -> list[JsonDict]:
        return [
            {
                "role": "system",
                "content": (
                    "You are the Repair Agent in an LLM multi-agent benchmark construction "
                    "framework. Revise a rejected reformulated optimization problem. Fix all "
                    "reported issues, preserve the same source problem and primary target "
                    "technique, and return a complete replacement item. Return only valid JSON."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "repair_round": repair_round,
                        "source_problem": source_problem,
                        "target_technique": technique,
                        "rejected_item": rejected_item,
                        "feedback": feedback,
                        "rules": rules,
                        "output_schema": REFORMULATED_ITEM_SCHEMA,
                        "repair_requirements": [
                            "Return the full revised item, not a patch.",
                            "Do not leak the target technique name in natural_language_problem.",
                            "Do not add naive_solution or expert_solution fields.",
                            "Include natural_language_answer for the revised problem.",
                            "Include a complete top-level mathematical_model for the revised problem.",
                            "Keep at least the required number of source_trace.kept elements.",
                            "Make verification.pass true only if the answer is actually checked.",
                            "If the issue is duplicate text, change the story/numbers while preserving the same target technique.",
                        ],
                    },
                    ensure_ascii=False,
                ),
            },
        ]

    def run(
        self,
        source_problem: JsonDict,
        technique: JsonDict,
        rejected_item: JsonDict,
        rules: JsonDict,
        feedback: JsonDict,
        repair_round: int,
    ) -> JsonDict:
        response = call_openai_compatible_chat(
            self.model_cfg,
            self.build_messages(source_problem, technique, rejected_item, rules, feedback, repair_round),
            timeout_seconds=self.api_timeout,
        )
        result = extract_json(response["content"])
        if not isinstance(result, dict):
            raise FrameworkError("Repair agent did not return a JSON object.")
        result["_agent"] = self.name
        result["_repair_round"] = repair_round
        result["_llm"] = llm_metadata(self.model_cfg, response)
        return result


class LLMReferenceImplementationAgent:
    """LLM agent that creates bundle-style ordinary/technique reference files."""

    name = "LLM Reference Implementation Agent"

    def __init__(self, model_cfg: JsonDict, api_timeout: int = 180):
        self.model_cfg = model_cfg
        self.api_timeout = api_timeout

    def build_messages(
        self,
        reformulated_item: JsonDict,
        technique: JsonDict,
        rules: JsonDict,
        feedback: JsonDict | None = None,
        repair_round: int = 0,
    ) -> list[JsonDict]:
        payload: JsonDict = {
            "reformulated_item": reformulated_item,
            "target_technique": technique,
            "reference_rules": rules.get("reference_generation_rules", {}),
            "output_schema": REFERENCE_IMPLEMENTATION_SCHEMA,
            "implementation_contract": [
                "Return only valid JSON.",
                "Generate complete Python source strings, not markdown fences.",
                "ordinary_model_py and technique_model_py must expose a solve(instance_path='instance.json', params=None) function.",
                "Each solve function must return a dict containing status, objective_value, solver_name, model_build_seconds, solver_runtime_seconds, num_variables, num_constraints, num_nonzeros, work_units, mip_gap, solution_summary, and notes.",
                "Each model file must also be runnable as a script and print EXECUTION_RESULT_JSON=<json>.",
                "validate_py must run both models for two sequential rounds, compare objective values, collect speed/work/model-size metrics, and write validation.json.",
                "validation.json must contain problem_id, ok, rounds, and summary. Each round must contain ordinary, technique, objective_match, runtime_speedup_percent, and work_reduction_percent. summary must contain reference_objective_value, minimum_runtime_speedup_percent, minimum_work_reduction_percent, ordinary_median_solver_runtime_seconds, technique_median_solver_runtime_seconds, ordinary_median_code_run_time_seconds, technique_median_code_run_time_seconds, ordinary_num_variables, technique_num_variables, ordinary_num_constraints, and technique_num_constraints.",
                "Measure solver_runtime_seconds only around optimize()/solve(); measure code_run_time_seconds around the whole solve() call inside validate.py.",
                "Use gurobipy if available for comparable reference implementations. Include a safe scipy/custom fallback only when appropriate.",
                "When using gurobipy, set Threads=1, Seed=0, TimeLimit=300, MIPGap=0, FeasibilityTol=1e-9, IntFeasTol=1e-9, and OptimalityTol=1e-9 when possible.",
                "Do not fake runtime, work, objective, variable, or constraint metrics. If a metric is unavailable, use null and explain it in notes.",
                "The ordinary model should be correct but less efficient or less structured. The technique model should use the target technique structurally, not merely mention it.",
                "Do not include API keys, absolute local paths, or hidden answer leakage in problem_md.",
            ],
        }
        if feedback:
            payload["feedback"] = feedback
            payload["repair_round"] = repair_round
        return [
            {
                "role": "system",
                "content": (
                    "You are the Reference Implementation Agent in an LLM multi-agent "
                    "optimization benchmark construction framework. Your job is to turn "
                    "one accepted reformulated optimization item into a bundle-style "
                    "human_reference directory with a fixed instance, ordinary model, "
                    "target-technique model, validator, validation summary, and review notes. "
                    "This is still benchmark construction, not candidate model evaluation. "
                    "Return only valid JSON."
                ),
            },
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ]

    def run(
        self,
        reformulated_item: JsonDict,
        technique: JsonDict,
        rules: JsonDict,
        feedback: JsonDict | None = None,
        repair_round: int = 0,
    ) -> JsonDict:
        response = call_openai_compatible_chat(
            self.model_cfg,
            self.build_messages(
                reformulated_item,
                technique,
                rules,
                feedback=feedback,
                repair_round=repair_round,
            ),
            timeout_seconds=self.api_timeout,
        )
        result = extract_json(response["content"])
        if not isinstance(result, dict):
            raise FrameworkError("Reference implementation agent did not return a JSON object.")
        result["_agent"] = self.name
        result["_repair_round"] = repair_round
        result["_llm"] = llm_metadata(self.model_cfg, response)
        return result


class LLMReferenceAuditAgent:
    """LLM agent that audits generated reference implementation files."""

    name = "LLM Reference Audit Agent"

    def __init__(self, model_cfg: JsonDict, api_timeout: int = 180):
        self.model_cfg = model_cfg
        self.api_timeout = api_timeout

    def build_messages(
        self,
        reformulated_item: JsonDict,
        technique: JsonDict,
        reference_package: JsonDict,
        validation_result: JsonDict | None,
        rules: JsonDict,
    ) -> list[JsonDict]:
        return [
            {
                "role": "system",
                "content": (
                    "You are the Reference Audit Agent in an LLM multi-agent benchmark "
                    "construction framework. Audit whether generated ordinary/technique "
                    "reference implementations are schema-complete, executable in principle, "
                    "mathematically consistent with the reformulated problem, and whether the "
                    "technique implementation structurally uses the target technique. Return only valid JSON."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "reformulated_item": reformulated_item,
                        "target_technique": technique,
                        "reference_package_summary": summarize_reference_package(reference_package),
                        "validation_result": validation_result,
                        "rules": rules.get("reference_generation_rules", {}),
                        "audit_policy": {
                            "reject_if_missing_any_required_file": True,
                            "reject_if_problem_md_diverges_from_problem_statement": True,
                            "reject_if_models_do_not_expose_solve_function": True,
                            "reject_if_validation_does_not_compare_two_models": True,
                            "reject_if_validation_json_missing_two_rounds": True,
                            "reject_if_required_runtime_or_model_size_metrics_missing_without_explanation": True,
                            "reject_if_ordinary_and_technique_are_identical": True,
                            "reject_if_technique_model_does_not_use_target_technique_structurally": True,
                            "local_validation_failure_requires_repair": True,
                        },
                        "output_schema": {
                            "pass": True,
                            "issues": ["specific issue strings; empty if pass"],
                            "repair_instructions": ["concrete repair steps"],
                            "ordinary_model_check": {"score": 0.0, "reason": "correctness and ordinary baseline quality"},
                            "technique_model_check": {"score": 0.0, "reason": "target technique use and expected efficiency"},
                            "validator_check": {"score": 0.0, "reason": "validation coverage and result interpretation"},
                            "bundle_format_check": {"score": 0.0, "reason": "file/schema completeness"},
                        },
                    },
                    ensure_ascii=False,
                ),
            },
        ]

    def run(
        self,
        reformulated_item: JsonDict,
        technique: JsonDict,
        reference_package: JsonDict,
        validation_result: JsonDict | None,
        rules: JsonDict,
    ) -> JsonDict:
        response = call_openai_compatible_chat(
            self.model_cfg,
            self.build_messages(reformulated_item, technique, reference_package, validation_result, rules),
            timeout_seconds=self.api_timeout,
        )
        result = extract_json(response["content"])
        if not isinstance(result, dict):
            raise FrameworkError("Reference audit agent did not return a JSON object.")
        result["_agent"] = self.name
        result["_llm"] = llm_metadata(self.model_cfg, response)
        return result


def summarize_reference_package(reference_package: JsonDict) -> JsonDict:
    return {
        "problem_id": reference_package.get("problem_id"),
        "has_instance_json": "instance_json" in reference_package,
        "has_problem_md": bool(reference_package.get("problem_md")),
        "has_ordinary_model_py": bool(reference_package.get("ordinary_model_py")),
        "has_technique_model_py": bool(reference_package.get("technique_model_py")),
        "has_validate_py": bool(reference_package.get("validate_py")),
        "has_review_md": bool(reference_package.get("review_md")),
        "reference_metadata": reference_package.get("reference_metadata"),
        "ordinary_model_py_prefix": str(reference_package.get("ordinary_model_py") or "")[:1600],
        "technique_model_py_prefix": str(reference_package.get("technique_model_py") or "")[:1600],
        "validate_py_prefix": str(reference_package.get("validate_py") or "")[:1600],
    }
