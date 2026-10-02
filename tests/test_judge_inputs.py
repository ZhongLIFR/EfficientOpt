"""Offline checks for the public configuration and packaged reference layout."""
from __future__ import annotations

import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from evaluation.judge.core.classifier import classify_candidate
from evaluation.judge.core.llm_judge import call_judge_api, merge_llm_judgement
from evaluation.judge.core.loaders import load_case_bundle
from evaluation.judge.core.report import aggregate_results
from evaluation.judge.core.runner import _result_row


class PublicConfigTests(unittest.TestCase):
    def test_example_config_uses_environment_endpoint_and_credentials(self) -> None:
        config_path = Path(__file__).resolve().parents[1] / "evaluation/judge/configs" / "judge_model.example.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        response = io.BytesIO(json.dumps({"choices": [{"message": {"content": '{"category": 1}'}}]}).encode())
        with patch.dict(os.environ, {
            "EFFICIENTOPT_JUDGE_BASE_URL": " https://judge.invalid/v1/ ",
            "EFFICIENTOPT_JUDGE_API_KEY": "offline-test-key",
        }), patch("urllib.request.urlopen", return_value=response) as request:
            result = call_judge_api(config, [{"role": "user", "content": "test"}])
        self.assertEqual(request.call_args.args[0].full_url, "https://judge.invalid/v1/chat/completions")
        self.assertEqual(result["parsed"], {"category": 1})

    def test_explicit_endpoint_takes_precedence_over_environment(self) -> None:
        config = {"model": "offline", "api_key": "offline-test-key", "base_url": "https://explicit.invalid/v1", "base_url_env": "JUDGE_TEST_ENDPOINT"}
        response = io.BytesIO(b'{"choices":[{"message":{"content":"{}"}}]}')
        with patch.dict(os.environ, {"JUDGE_TEST_ENDPOINT": "https://unused.invalid/v1"}), patch("urllib.request.urlopen", return_value=response) as request:
            call_judge_api(config, [])
        self.assertEqual(request.call_args.args[0].full_url, "https://explicit.invalid/v1/chat/completions")


class PackagedReferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.private = self.root / "private" / "T01" / "T01_001"
        self.private.mkdir(parents=True)
        public = self.root / "public" / "T01" / "T01_001"
        public.mkdir(parents=True)
        (public / "problem.md").write_text("Minimize cost.", encoding="utf-8")
        self.write_result("ordinary", objective=10, runtime=2)
        self.write_result("technique", objective=10, runtime=1)

    def write_result(self, name: str, *, objective: float, runtime: float, status: str = "OPTIMAL") -> None:
        (self.private / f"{name}_result.json").write_text(json.dumps({"solver_status": status, "objective_value": objective, "solver_s": runtime}), encoding="utf-8")

    def load(self, **kwargs):
        return load_case_bundle(problem_id="T01_001", model_name="offline", public_root=self.root / "public", private_root=self.root / "private", formal_root=self.root / "formal", **kwargs)

    def test_packaged_results_supply_metrics_and_agreeing_objective(self) -> None:
        bundle = self.load()
        self.assertEqual(bundle["ordinary_baseline"]["solver_runtime_seconds"], 2)
        self.assertEqual(bundle["technique_baseline"]["solver_runtime_seconds"], 1)
        self.assertEqual(bundle["reference"]["objective_value"], 10)
        self.assertEqual(bundle["reference_source"], "paired_baseline_results")
        bundle["candidate"] = {"solver_status": "OPTIMAL", "objective_value": 10}
        self.assertTrue(classify_candidate(bundle)["objective_correct_independent"])
        self.assertEqual(classify_candidate(bundle)["objective_validation_source"], "paired_baseline_results")

    def test_conflicting_or_unsolved_pairs_do_not_supply_objective(self) -> None:
        for objective, status in [(11, "OPTIMAL"), (10, "TIME_LIMIT"), (float("inf"), "OPTIMAL")]:
            with self.subTest(objective=objective, status=status):
                self.write_result("technique", objective=objective, runtime=1, status=status)
                bundle = self.load()
                self.assertEqual(bundle["reference"], {})
                self.assertEqual(bundle["reference_source"], "unavailable")
                self.assertTrue(bundle["reference_note"])
                self.assertIn("reference", bundle["missing_context"])

    def test_explicit_reference_and_external_metrics_retain_precedence(self) -> None:
        (self.private / "reference.json").write_text('{"objective": 99}', encoding="utf-8")
        baseline = self.root / "baselines" / "ordinary" / "T01_001"
        baseline.mkdir(parents=True)
        (baseline / "runner_result.json").write_text('{"solver_status": "OPTIMAL", "objective_value": 10, "solver_runtime_seconds": 7}', encoding="utf-8")
        bundle = self.load(baseline_root=self.root / "baselines")
        self.assertEqual(bundle["reference"], {"objective": 99})
        self.assertEqual(bundle["reference_source"], "reference_json")
        self.assertEqual(bundle["ordinary_baseline"]["solver_runtime_seconds"], 7)
        self.assertEqual(bundle["technique_baseline"]["solver_runtime_seconds"], 1)


class UnknownCorrectnessTests(unittest.TestCase):
    def context(self, **candidate):
        return {"candidate": {"solver_status": "OPTIMAL", "objective_value": 10, **candidate}}

    def test_unknown_reference_is_not_failure_or_success_after_llm_merge(self):
        hard = classify_candidate(self.context())
        self.assertIsNone(hard["category"])
        self.assertIsNone(hard["hard_category"])
        self.assertEqual(hard["failure_reasons"], [])
        self.assertEqual(hard["objective_validation_status"], "unknown")
        for category, match in [(1, "target"), (2, "alternative"), (4, "none"), (5, "not_applicable")]:
            with self.subTest(category=category):
                merged = merge_llm_judgement(hard, {"category": category, "technique_match": match})
                row = _result_row(self.context(), merged, "offline")
                self.assertIsNone(row["category"])
                self.assertEqual(row["category_label"], "needs_manual_review")
                self.assertTrue(row["manual_review"])

    def test_explicit_correctness_flags_and_actual_solver_failure_keep_precedence(self):
        good = classify_candidate(self.context(objective_correct=True))
        self.assertEqual(merge_llm_judgement(good, {"category": 1, "technique_match": "target"})["category"], 1)
        bad = classify_candidate(self.context(objective_correct=False))
        self.assertEqual(bad["category"], 5)
        self.assertIn("wrong_objective_or_feasibility", bad["failure_reasons"])
        failed = classify_candidate(self.context(solver_status="TIME_LIMIT"))
        self.assertEqual(failed["category"], 5)
        self.assertEqual(failed["hard_failure_reason"], "time_limit")
        self.assertNotIn("wrong_objective_or_feasibility", failed["failure_reasons"])

    def test_verified_reference_still_overrides_supplied_flag(self):
        for objective, flag, expected in [(10, False, True), (11, True, False)]:
            with self.subTest(objective=objective):
                context = self.context(objective_correct=flag)
                context["reference"] = {"objective": objective}
                result = classify_candidate(context)
                self.assertIs(result["objective_correct_independent"], expected)
                self.assertEqual(result["category"], None if expected else 5)

    def test_nonfinite_or_invalid_candidate_is_failure_even_with_true_flag(self):
        for value in (float("inf"), -float("inf"), float("nan"), "invalid"):
            with self.subTest(value=value):
                context = self.context(objective_value=value, objective_correct=True)
                context["reference"] = {"objective": float("inf")}
                result = classify_candidate(context)
                self.assertEqual(result["category"], 5)
                self.assertIs(result["objective_correct_independent"], False)

    def test_invalid_reference_or_tolerance_leaves_correctness_unknown(self):
        references = [{"objective": value} for value in (float("inf"), float("nan"), "invalid")]
        references.extend({"objective": 10, "relative_tolerance": value}
                          for value in (float("inf"), float("nan"), -1, "invalid"))
        for reference in references:
            with self.subTest(reference=reference):
                context = self.context()
                context["reference"] = reference
                result = classify_candidate(context)
                self.assertIsNone(result["objective_correct_independent"])
                self.assertEqual(result["objective_validation_status"], "unknown")
                self.assertIsNone(result["category"])
                self.assertTrue(result["manual_review"])

    def test_reports_exclude_unknown_from_category_counts_and_proportions(self):
        unknown = {**classify_candidate(self.context()), "model_name": "m"}
        success = {**merge_llm_judgement(classify_candidate(self.context(objective_correct=True)),
                                        {"category": 1, "technique_match": "target"}), "model_name": "m"}
        failure = {**classify_candidate(self.context(objective_correct=False)), "model_name": "m"}
        summary = aggregate_results([unknown, success, failure])[0]
        self.assertEqual(summary["n"], 3)
        self.assertEqual(summary["classified_n"], 2)
        self.assertEqual(summary["unjudged_count"], 1)
        self.assertEqual(summary["objective_unknown_count"], 1)
        self.assertEqual(summary["category_counts"], {"1": 1, "2": 0, "3": 0, "4": 0, "5": 1})
        self.assertEqual(summary["category_proportions"]["1"], 0.5)
        self.assertEqual(summary["category_proportions"]["5"], 0.5)
        empty = aggregate_results([unknown])[0]
        self.assertEqual(empty["classified_n"], 0)
        self.assertTrue(all(value is None for value in empty["category_proportions"].values()))


if __name__ == "__main__":
    unittest.main()
