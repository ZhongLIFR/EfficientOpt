from __future__ import annotations

import json
import shutil
from uuid import uuid4
from pathlib import Path

from evaluation.judge.core.classifier import classify_candidate
from evaluation.judge.core.loaders import _normalise_candidate, load_case_bundle
from evaluation.judge.core.llm_judge import build_judge_messages, merge_llm_judgement, split_document
from evaluation.judge.core.report import aggregate_results
from evaluation.judge.core.discovery import discover_case_keys
from evaluation.judge.core.knowledge_base import TechniqueKnowledgeBase


def _context(*, candidate: dict, technique: dict | None = None, ordinary: dict | None = None, expert: dict | None = None) -> dict:
    return {
        "problem_id": "T09_003",
        "technique": technique or {
            "tech_id": "T09",
            "name": "piecewise-linear modeling",
            "core_idea": "Represent piecewise-linear functions with epigraph cuts, incremental variables, SOS2, or native PWL.",
        },
        "candidate": candidate,
        "ordinary_baseline": ordinary or {"solver_status": "OPTIMAL", "solver_runtime_seconds": 100.0, "work_units": 100.0},
        "technique_baseline": expert or {"solver_status": "OPTIMAL", "solver_runtime_seconds": 40.0, "work_units": 40.0},
    }


def test_valid_candidate_has_no_static_technique_category():
    result = classify_candidate(_context(candidate={
        "solver_status": "OPTIMAL",
        "objective_correct": True,
        "returncode": 0,
        "solver_runtime_seconds": 130.0,
        "work_units": 120.0,
        "candidate_code": "segment = model.addVars(n, 4); model.setObjective(sum(slopes[k] * segment[i,k] for i in range(n) for k in range(4)))",
        "formulation_summary": {"strategy": "incremental piecewise-linear formulation"},
    }))
    assert result["category"] is None
    assert result["hard_category"] is None
    assert result["efficiency_verdict"] == "poor"


def test_correct_non_target_alternative_is_category_two_when_efficient():
    result = classify_candidate(_context(
        technique={"tech_id": "T16", "name": "Benders decomposition", "core_idea": "Separate master and subproblem with cuts."},
        candidate={
            "solver_status": "OPTIMAL",
            "objective_correct": True,
            "returncode": 0,
            "solver_runtime_seconds": 45.0,
            "work_units": 42.0,
            "candidate_code": "for scenario in scenarios: flow_balance[scenario] = ...; model.addConstr(flow_balance[scenario])",
            "formulation_summary": {"strategy": "network flow formulation with conservation constraints"},
        },
        ordinary={"solver_status": "OPTIMAL", "solver_runtime_seconds": 100.0, "work_units": 100.0},
        expert={"solver_status": "OPTIMAL", "solver_runtime_seconds": 40.0, "work_units": 40.0},
    ))
    assert result["category"] is None
    merged = merge_llm_judgement(result, {"category": 2, "efficiency_verdict": "good"})
    assert merged["category"] == 2


def test_correct_non_target_alternative_is_category_three_when_poor():
    result = classify_candidate(_context(
        technique={"tech_id": "T16", "name": "Benders decomposition", "core_idea": "Separate master and subproblem with cuts."},
        candidate={
            "solver_status": "OPTIMAL",
            "objective_correct": True,
            "returncode": 0,
            "solver_runtime_seconds": 250.0,
            "work_units": 300.0,
            "candidate_code": "for scenario in scenarios: flow_balance[scenario] = ...; model.addConstr(flow_balance[scenario])",
            "formulation_summary": {"strategy": "network flow formulation with conservation constraints"},
        },
    ))
    assert result["category"] is None
    assert result["efficiency_verdict"] == "poor"
    assert merge_llm_judgement(result, {"category": 3, "efficiency_verdict": "poor"})["category"] == 3


def test_correct_plain_model_without_technique_is_category_four():
    result = classify_candidate(_context(
        technique={"tech_id": "T15", "name": "block decomposition", "core_idea": "Solve independent blocks as separate models."},
        candidate={
            "solver_status": "OPTIMAL",
            "objective_correct": True,
            "returncode": 0,
            "solver_runtime_seconds": 70.0,
            "work_units": 60.0,
            "candidate_code": "x = model.addVars(options, vtype=GRB.BINARY); model.optimize()",
            "formulation_summary": {"strategy": "straightforward binary covering model"},
        },
    ))
    assert result["category"] is None
    assert merge_llm_judgement(result, {"category": 4})["category"] == 4


def test_failed_candidate_is_category_five():
    result = classify_candidate(_context(candidate={
        "solver_status": "ERROR",
        "objective_correct": False,
        "returncode": 1,
        "notes": "AttributeError: addPWLObjective",
        "candidate_code": "model.addPWLObjective(x, b, y, GRB.MINIMIZE)",
        "formulation_summary": {"strategy": "native PWL"},
    }))
    assert result["category"] == 5
    assert result["hard_failure_reason"] == "code_error"


def test_loader_reads_reference_directory_layout():
    tmp_path = Path(__import__("tempfile").gettempdir()) / f".test_tmp_{uuid4().hex}"
    tmp_path.mkdir(parents=True)
    try:
        _test_loader_reads_reference_directory_layout(tmp_path)
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_llm_judgement_cannot_override_hard_solve_error():
    hard = {"category": 5, "hard_category": 5, "hard_failure_reason": "code_error"}
    merged = merge_llm_judgement(hard, {"category": 1, "brief_reason": "looks like target technique"})
    assert merged["category"] == 5
    assert merged["hard_gate_applied"] is True


def test_llm_judgement_is_used_for_valid_candidate():
    hard = {"category": None, "hard_category": None, "hard_failure_reason": None, "efficiency_verdict": "good"}
    merged = merge_llm_judgement(hard, {"category": 2, "technique_match": "alternative", "brief_reason": "network flow alternative"})
    assert merged["category"] == 2
    assert merged["hard_gate_applied"] is False


def test_prompt_exposes_user_approved_semantic_equivalences():
    messages = build_judge_messages({
        "problem_id": "T09_003",
        "problem_statement": "piecewise linear cost",
        "technique": {
            "tech_id": "T09",
            "name": "piecewise-linear modeling",
            "core_idea": "epigraph cuts",
            "semantic_equivalents": ["native PWL", "SOS2/lambda", "incremental segments"],
        },
        "candidate": {"candidate_code": "model.setPWLObj(x, b, y)"},
        "ordinary_baseline": {},
        "technique_baseline": {},
        "reference_formulation": "epigraph formulation",
        "technique_catalog": [{"tech_id": "T50", "name": "tensor low-rank modeling"}],
    }, {"category": None, "hard_category": None})
    assert "semantic_equivalents" in messages[1]["content"]
    assert "incremental segments" in messages[1]["content"]
    assert "technique_catalog" in messages[1]["content"]
    assert "static_precheck" not in messages[1]["content"]


def test_report_counts_five_categories_and_runtime_fields():
    summary = aggregate_results([
        {"model_name": "m", "problem_id": "T09_003", "category": 1, "candidate_solver_runtime_seconds": 2.0},
        {"model_name": "m", "problem_id": "T09_004", "category": 4, "candidate_solver_runtime_seconds": 3.0},
        {"model_name": "n", "problem_id": "T10_001", "category": 5, "candidate_solver_runtime_seconds": None},
    ])
    by_model = {row["model_name"]: row for row in summary}
    assert by_model["m"]["category_counts"]["1"] == 1
    assert by_model["m"]["category_counts"]["4"] == 1
    assert by_model["m"]["mean_model_runtime_seconds"] == 2.5
    assert by_model["n"]["category_counts"]["5"] == 1


def test_flat_metrics_survive_null_nested_execution_result():
    normalized = _normalise_candidate(
        {
            "solver_runtime_seconds": 12.5,
            "num_variables": 100,
            "num_constraints": 50,
            "num_nonzeros": 300,
            "execution_result": {
                "solver_runtime_seconds": None,
                "num_variables": None,
                "num_constraints": None,
                "num_nonzeros": None,
            },
        },
        {"formulation_summary": {}},
        "code",
    )
    assert normalized["solver_runtime_seconds"] == 12.5
    assert normalized["num_variables"] == 100
    assert normalized["num_constraints"] == 50
    assert normalized["num_nonzeros"] == 300


def test_memory_metrics_are_normalized_to_mb_and_gb():
    normalized = _normalise_candidate(
        {"execution_result": {"gurobi_max_mem_used_mb": 2048.0}},
        {"formulation_summary": {}},
        "code",
    )
    assert normalized["memory_peak_mb"] == 2048.0
    assert normalized["memory_peak_gb"] == 2.0


def test_reference_objective_is_checked_independently():
    result = classify_candidate({
        "technique": {"tech_id": "T09"},
        "reference": {"objective": 100.0, "relative_tolerance": 1e-6},
        "candidate": {
            "solver_status": "OPTIMAL",
            "objective_value": 100.00000001,
            "objective_correct": False,
            "returncode": 0,
            "candidate_code": "model.optimize()",
        },
    })
    assert result["objective_correct_independent"] is True
    assert result["objective_validation_source"] == "reference_json"
    assert result["category"] is None
    assert merge_llm_judgement(result, {"category": 4})["category"] == 4


def test_failure_taxonomy_distinguishes_timeout_infeasible_and_code_error():
    base = {"objective_correct": False, "returncode": 1, "candidate_code": ""}
    timeout = classify_candidate({"technique": {"tech_id": "T09"}, "candidate": {**base, "solver_status": "TIME_LIMIT"}})
    infeasible = classify_candidate({"technique": {"tech_id": "T09"}, "candidate": {**base, "solver_status": "INFEASIBLE"}})
    code_error = classify_candidate({"technique": {"tech_id": "T09"}, "candidate": {**base, "solver_status": "ERROR", "notes": "AttributeError"}})
    assert timeout["hard_failure_reason"] == "time_limit"
    assert infeasible["hard_failure_reason"] == "infeasible_model"
    assert code_error["hard_failure_reason"] == "code_error"
    assert "wrong_objective_or_feasibility" in timeout["failure_reasons"]


def test_merge_propagates_llm_efficiency_and_separates_review_sources():
    merged = merge_llm_judgement(
        {"category": None, "hard_category": None, "efficiency_verdict": "good"},
        {"category": 2, "technique_match": "alternative", "efficiency_verdict": "good", "recommended_manual_review": False},
    )
    assert merged["category"] == 2
    assert merged["efficiency_verdict"] == "good"
    assert merged["llm_manual_review"] is False
    assert merged["manual_review"] is False


def test_alternative_categories_use_explicit_runtime_rule():
    good = merge_llm_judgement(
        {"category": None, "hard_category": None, "efficiency_verdict": "good"},
        {"category": 3, "technique_match": "alternative"},
    )
    poor = merge_llm_judgement(
        {"category": None, "hard_category": None, "efficiency_verdict": "poor"},
        {"category": 2, "technique_match": "alternative"},
    )
    unavailable = merge_llm_judgement(
        {"category": None, "hard_category": None, "efficiency_verdict": "unavailable"},
        {"category": 2, "technique_match": "alternative"},
    )
    assert good["category"] == 2
    assert poor["category"] == 3
    assert unavailable["category"] is None
    assert unavailable["manual_review"] is True


def test_runtime_rule_has_no_boundary_overlap_at_two_times_expert():
    result = classify_candidate(_context(
        technique={"tech_id": "T16", "name": "Benders decomposition"},
        candidate={
            "solver_status": "OPTIMAL",
            "objective_correct": True,
            "returncode": 0,
            "solver_runtime_seconds": 80.0,
            "work_units": 80.0,
            "candidate_code": "model.optimize()",
        },
        ordinary={"solver_status": "OPTIMAL", "solver_runtime_seconds": 160.0, "work_units": 160.0},
        expert={"solver_status": "OPTIMAL", "solver_runtime_seconds": 40.0, "work_units": 40.0},
    ))
    assert result["efficiency_verdict"] == "poor"


def test_full_code_and_reference_implementations_are_kept_in_prompt():
    code = "head\n" + ("x = 1\n" * 4000) + "TAIL_MARKER"
    messages = build_judge_messages({
        "problem_id": "T09_003",
        "problem_statement": "problem",
        "technique": {"tech_id": "T09", "name": "PWL", "semantic_equivalents": ["native PWL"]},
        "technique_catalog": [],
        "candidate": {"candidate_code": code, "formulation_summary": {}},
        "ordinary_baseline": {},
        "technique_baseline": {},
        "ordinary_reference_code": "ordinary_reference_marker",
        "technique_reference_code": "technique_reference_marker",
        "reference_formulation": "reference",
    }, {"category": None, "hard_category": None})
    content = messages[1]["content"]
    assert "TAIL_MARKER" in content
    assert "ordinary_reference_marker" in content
    assert "technique_reference_marker" in content
    assert "code_truncated_in_prompt" not in content or "false" in content


def test_document_chunking_covers_every_character():
    document = "0123456789" * 100
    chunks = split_document(document, 37)
    assert "".join(chunks) == document
    assert len(chunks) > 1


def test_discovery_is_path_driven_and_deduplicates_case_keys():
    tmp_path = Path(__import__("tempfile").gettempdir()) / f".test_discovery_{uuid4().hex}"
    tmp_path.mkdir(parents=True)
    try:
        _test_discovery_is_path_driven_and_deduplicates_case_keys(tmp_path)
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_knowledge_base_loads_all_techniques_without_hardcoded_range():
    tmp_path = Path(__import__("tempfile").gettempdir()) / f".test_kb_{uuid4().hex}"
    tmp_path.mkdir(parents=True)
    try:
        _test_knowledge_base_loads_all_techniques_without_hardcoded_range(tmp_path)
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def _test_knowledge_base_loads_all_techniques_without_hardcoded_range(tmp_path: Path):
    kb_path = tmp_path / "techniques.json"
    kb_path.write_text(json.dumps({"techniques": [
        {"tech_id": "T01", "name": "equivalent transformation", "core_idea": "preserve feasible set"},
        {"tech_id": "T50", "name": "tensor low-rank modeling", "core_idea": "preserve tensor modes"},
    ]}), encoding="utf-8")
    kb = TechniqueKnowledgeBase.from_json(kb_path)
    assert kb.ids() == ["T01", "T50"]
    assert kb.get("T50")["core_idea"] == "preserve tensor modes"


def test_prompt_can_judge_a_technique_outside_the_old_regex_set():
    messages = build_judge_messages({
        "problem_id": "T50_001",
        "problem_statement": "recover a low-rank tensor",
        "technique": {
            "tech_id": "T50",
            "name": "tensor low-rank modeling",
            "core_idea": "preserve tensor modes and use CP/Tucker",
            "semantic_equivalents": ["CP decomposition", "Tucker decomposition"],
        },
        "technique_catalog": [{"tech_id": "T50", "name": "tensor low-rank modeling"}],
        "candidate": {"candidate_code": "X = cp_decomposition(data, rank=3)"},
        "ordinary_baseline": {},
        "technique_baseline": {},
        "reference_formulation": "CP/Tucker model",
    }, {"category": None, "hard_category": None})
    assert "tensor low-rank modeling" in messages[1]["content"]
    assert "CP decomposition" in messages[1]["content"]


def _test_discovery_is_path_driven_and_deduplicates_case_keys(tmp_path: Path):
    formal = tmp_path / "formal"
    for model, problem in (("model_a", "T01_001"), ("model_a", "T01_002"), ("model_b", "T01_001")):
        folder = formal / model / problem
        folder.mkdir(parents=True)
        (folder / "evaluation.json").write_text("{}", encoding="utf-8")
    keys = discover_case_keys(formal)
    assert keys == [("model_a", "T01_001"), ("model_a", "T01_002"), ("model_b", "T01_001")]


def _test_loader_reads_reference_directory_layout(tmp_path: Path):
    public = tmp_path / "public" / "T09" / "T09_003"
    private = tmp_path / "private" / "T09" / "T09_003"
    llm = tmp_path / "llm" / "gpt55" / "T09_003"
    baseline_o = tmp_path / "baselines" / "ordinary" / "T09_003"
    baseline_t = tmp_path / "baselines" / "technique" / "T09_003"
    for path in (public, private, llm, baseline_o, baseline_t):
        path.mkdir(parents=True)
    (public / "problem.md").write_text("minimize cost", encoding="utf-8")
    (public / "instance.json").write_text("{}", encoding="utf-8")
    (private / "metadata.json").write_text(json.dumps({"primary_technique": "T09", "technique_name": "PWL"}), encoding="utf-8")
    (private / "formulation.md").write_text("use epigraph cuts", encoding="utf-8")
    (private / "reference.json").write_text(json.dumps({"objective": 10.0}), encoding="utf-8")
    (llm / "evaluation.json").write_text(json.dumps({"id": "T09_003", "objective_correct": True, "execution_result": {"solver_status": "OPTIMAL"}}), encoding="utf-8")
    (llm / "parsed.json").write_text(json.dumps({"formulation_summary": {}, "code": "model.setPWLObj(x, b, y)"}), encoding="utf-8")
    (llm / "candidate_model.py").write_text("model.setPWLObj(x, b, y)", encoding="utf-8")
    (baseline_o / "runner_result.json").write_text(json.dumps({"solver_status": "OPTIMAL", "solver_runtime_seconds": 20}), encoding="utf-8")
    (baseline_t / "runner_result.json").write_text(json.dumps({"solver_status": "OPTIMAL", "solver_runtime_seconds": 10}), encoding="utf-8")
    kb_path = tmp_path / "custom_kb.json"
    kb_path.write_text(json.dumps({"techniques": [{"tech_id": "T09", "name": "custom PWL", "semantic_equivalents": ["custom PWL"]}]}), encoding="utf-8")

    bundle = load_case_bundle(
        problem_id="T09_003",
        model_name="gpt55",
        public_root=tmp_path / "public",
        private_root=tmp_path / "private",
        formal_root=tmp_path / "llm",
        baseline_root=tmp_path / "baselines",
        knowledge_base_path=kb_path,
    )
    assert bundle["candidate"]["solver_status"] == "OPTIMAL"
    assert bundle["technique"]["tech_id"] == "T09"
    assert bundle["technique_baseline"]["solver_runtime_seconds"] == 10
    assert "use epigraph cuts" in bundle["reference_formulation"]
    assert "custom PWL" in bundle["technique"]["semantic_equivalents"]
    assert bundle["missing_context"] == []


def load_tests(loader, tests, pattern):
    """Run the existing function tests with Python's built-in unittest runner."""
    import unittest
    tests.addTests(unittest.FunctionTestCase(value) for name, value in sorted(globals().items())
                   if name.startswith("test_") and callable(value))
    return tests
