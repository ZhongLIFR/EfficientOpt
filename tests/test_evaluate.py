"""Offline entry-point and dataset-layout checks; no API calls or real solves."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

import evaluate
from evaluation.judge.core.loaders import load_case_bundle
from evaluation.judge.core.classifier import classify_candidate
from evaluation.reference_runner import SolverContext

ROOT = Path(__file__).resolve().parents[1]


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.dataset = self.root / 'dataset/main'
        self.task = self.dataset / 'T01/T01_002'
        self.truth = self.task / 'ground_truth'
        self.truth.mkdir(parents=True)
        (self.task / 'problem.md').write_text('Fixture problem.')
        (self.task / 'instance.json').write_text('{"target": 10}')
        (self.truth / 'reference.json').write_text('{"objective": 10, "relative_tolerance": 1e-6, "absolute_tolerance": 1e-6}')
        (self.truth / 'metadata.json').write_text('{"primary_technique": "T01"}')
        for kind in ('ordinary', 'technique'):
            (self.truth / f'{kind}_model.py').write_text('# fixture reference')
            (self.truth / f'{kind}_result.json').write_text('{"solver_status": "OPTIMAL", "objective_value": 99, "solver_s": 1}')

    def test_saved_result_check_is_solver_free_and_writes_output(self):
        saved = self.root / 'result.json'
        saved.write_text('{"execution_result":{"solver_status":"OPTIMAL","objective_value":10}}')
        output = self.root / 'out/evaluation.json'
        with patch.object(evaluate, 'execute', side_effect=AssertionError('No execution allowed')), contextlib.redirect_stdout(io.StringIO()):
            status = evaluate.main(['--instance', 'T01_002', '--dataset-root', str(self.dataset),
                                    '--result', str(saved), '--output', str(output)])
        self.assertEqual(status, 0)
        result = json.loads(output.read_text())
        self.assertIs(result['objective_correct'], True)
        self.assertEqual(result['reference_objective'], 10)

    def test_wrong_nonfinite_unknown_and_failed_results_are_distinct(self):
        ref = {'objective': 10}
        for value in (11, float('inf'), float('nan'), None):
            result = evaluate.score_result({'solver_status': 'OPTIMAL', 'objective_value': value}, ref)
            self.assertIs(result['objective_correct'], False)
        unknown = evaluate.score_result({'objective': 10}, ref)
        self.assertEqual(unknown['solver_status'], 'UNKNOWN')
        self.assertIs(unknown['objective_matches_reference'], True)
        self.assertIsNone(unknown['objective_correct'])
        no_target = evaluate.score_result({'solver_status': 'OPTIMAL', 'objective': 10}, {})
        self.assertIsNone(no_target['objective_correct'])
        failed = evaluate.score_result({'solver_status': 'TIME_LIMIT', 'objective': 10}, ref)
        self.assertIs(failed['objective_correct'], False)
        nonzero = evaluate.score_result({'solver_status': 'OPTIMAL', 'objective': 10, 'returncode': 1}, ref)
        self.assertIs(nonzero['objective_correct'], False)

    def test_small_targets_use_absolute_tolerance(self):
        good = evaluate.score_result({'solver_status': 'OPTIMAL', 'objective_value': 5e-7}, {'objective': 0})
        self.assertIs(good['objective_correct'], True)

    def test_judge_reads_new_layout_and_verified_target_has_precedence(self):
        formal = self.root / 'formal/model/T01_002'
        formal.mkdir(parents=True)
        (formal / 'evaluation.json').write_text('{"solver_status":"OPTIMAL","objective_value":10}')
        (formal / 'candidate_model.py').write_text('# candidate')
        bundle = load_case_bundle(problem_id='T01_002', model_name='model', dataset_root=self.dataset,
                                  formal_root=self.root / 'formal')
        self.assertEqual(bundle['reference']['objective'], 10)
        self.assertEqual(bundle['ordinary_baseline']['objective_value'], 99)
        self.assertEqual(bundle['reference_source'], 'reference_json')
        self.assertEqual(bundle['ordinary_reference_code'], '# fixture reference')
        self.assertIs(classify_candidate(bundle)['objective_correct_independent'], True)

    def test_native_reference_runs_once_in_task_cwd_with_local_helper(self):
        (self.truth / 'common_model.py').write_text('from pathlib import Path\nimport json\ndef load_data():\n    return json.loads(Path("instance.json").read_text())\n')
        model = self.truth / 'ordinary_model.py'
        model.write_text('from common_model import load_data\ndef solve():\n    return {"objective":load_data()["target"], "runtime":0.01, "gurobi_mem_used_mb":0.5}\n')
        raw = evaluate.execute(model, self.task, trusted_reference=True, timeout=10)
        self.assertEqual(raw['objective'], 10)
        result = evaluate.score_result(raw, {'objective': 10})
        self.assertEqual(result['solver_runtime_seconds'], 0.01)
        self.assertEqual(result['solver_status'], 'UNKNOWN')
        self.assertIsNone(result['objective_correct'])
        self.assertEqual(result['timing_source'], 'reference_reported_wall_time')
        self.assertNotIn('gurobi_mem_used_mb', result)
        self.assertEqual(result['raw_result']['gurobi_mem_used_mb'], 0.5)

    def test_process_timeout_is_reported(self):
        model = self.truth / 'ordinary_model.py'
        model.write_text('def solve():\n    return {}\n')
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired(['python'], 1)):
            result = evaluate.execute(model, self.task, trusted_reference=True, timeout=1)
        self.assertEqual(result['solver_status'], 'TIME_LIMIT')

    def test_algorithm_context_uses_one_cumulative_runtime_budget(self):
        class Model:
            Runtime = 3.0
            Work = 2.0
            Status = 2
            def __init__(self):
                self.params = {}
                self.solves = 0
            def setParam(self, key, value):
                self.params[key] = value
            def update(self):
                pass
            def optimize(self):
                self.solves += 1
        names = ('OPTIMAL', 'INFEASIBLE', 'INF_OR_UNBD', 'UNBOUNDED', 'TIME_LIMIT',
                 'INTERRUPTED', 'NUMERIC', 'SUBOPTIMAL', 'ITERATION_LIMIT', 'NODE_LIMIT')
        gp = types.SimpleNamespace(Model=Model, GRB=types.SimpleNamespace(**{name: i + 2 for i, name in enumerate(names)}))
        model = Model()
        context = SolverContext(time_limit=5)
        with patch.dict(sys.modules, {'gurobipy': gp}):
            self.assertEqual(context.optimize(model), 'OPTIMAL')
            self.assertEqual(model.params['TimeLimit'], 5)
            self.assertEqual(context.optimize(model), 'OPTIMAL')
            self.assertEqual(model.params['TimeLimit'], 2)
            self.assertEqual(context.optimize(model), 'TIME_LIMIT')
        self.assertEqual(model.solves, 2)
        self.assertEqual(context.calls, 2)
        self.assertEqual(context.runtime, 6)

    def test_algorithm_cannot_claim_optimal_without_solving(self):
        model = self.truth / 'technique_model.py'
        model.write_text('def solve_algorithm(instance, context):\n    return {"solver_status":"OPTIMAL", "objective_value":10}\n')
        result = evaluate.execute(model, self.task, trusted_reference=True, timeout=10)
        self.assertEqual(result['solver_status'], 'ERROR')
        self.assertIn('without all Gurobi solves', result['notes'])

    def test_reference_prefers_algorithm_over_iter_models(self):
        model = self.truth / 'technique_model.py'
        model.write_text('def iter_models(instance):\n    raise AssertionError("wrong entrypoint")\n'
                         'def solve_algorithm(instance, context):\n    return {"solver_status":"TIME_LIMIT", "objective_value":None}\n')
        result = evaluate.execute(model, self.task, trusted_reference=True, timeout=10)
        self.assertEqual(result['solver_status'], 'TIME_LIMIT')
        self.assertEqual(result['optimize_calls'], 0)

    def test_cli_help_does_not_need_configuration_or_network(self):
        commands = [
            ([sys.executable, '-B', str(ROOT / 'evaluate.py'), '--help'], ROOT),
            ([sys.executable, '-B', str(ROOT / 'judge.py'), '--help'], ROOT),
            ([sys.executable, '-B', '-m', 'optdachshund.cli', '--help'], ROOT / 'construction'),
        ]
        for command, cwd in commands:
            with self.subTest(command=command):
                result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('usage:', result.stdout)


if __name__ == '__main__':
    unittest.main()
