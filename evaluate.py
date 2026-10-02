"""Run one candidate/reference or check a saved result against a verified objective."""
from __future__ import annotations

import argparse
import ast
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def task_directory(dataset_root: Path, instance_id: str) -> Path:
    if not re.fullmatch(r'T\d{2}_\d{3}', instance_id):
        raise ValueError('Use an instance ID such as T01_002.')
    task = dataset_root / instance_id.split('_', 1)[0] / instance_id
    if not (task / 'problem.md').is_file():
        raise FileNotFoundError(f'Task not found: {task}')
    return task.resolve()


def normalize_result(raw: dict) -> dict:
    result = dict(raw)
    if isinstance(raw.get('execution_result'), dict):
        result.update({key: value for key, value in raw['execution_result'].items() if value is not None})
    aliases = {
        'objective_value': ('objective',),
        'solver_runtime_seconds': ('solver_s', 'runtime_s', 'runtime', 'wall_seconds'),
        'build_s': ('build_time_s',), 'work_units': ('work',),
        'num_variables': ('variables',), 'num_constraints': ('constraints',),
        'num_nonzeros': ('nonzeros',),
    }
    for key, alternatives in aliases.items():
        if result.get(key) is None:
            result[key] = next((result[name] for name in alternatives if result.get(name) is not None), None)
    result['solver_status'] = str(result.get('solver_status') or result.get('status') or 'UNKNOWN').upper()
    return result


def score_result(raw: dict, reference: dict) -> dict:
    result = normalize_result(raw)
    target = reference.get('objective', reference.get('objective_value'))
    value = result.get('objective_value')
    relative = reference.get('relative_tolerance', 1e-6)
    absolute = reference.get('absolute_tolerance', 1e-6)
    match = None
    note = 'No verified reference objective is available.'
    try:
        target = float(target)
        relative, absolute = float(relative), float(absolute)
        valid_reference = all(math.isfinite(v) for v in (target, relative, absolute)) and min(relative, absolute) >= 0
    except (TypeError, ValueError):
        valid_reference = False
    if valid_reference:
        try:
            value = float(value)
            match = math.isfinite(value) and math.isclose(value, target, rel_tol=relative, abs_tol=absolute)
        except (TypeError, ValueError):
            match = False
        note = 'Numerical objective comparison; this does not independently certify the formulation or feasibility.'
    else:
        target = None
    status = result['solver_status']
    success = status in {'OPTIMAL', 'SOLVED', 'VALIDATED_NATIVE_PYTHON'}
    failure = (status in {'ERROR', 'INFEASIBLE', 'INF_OR_UNBD', 'UNBOUNDED', 'TIME_LIMIT', 'INTERRUPTED', 'NUMERIC'}
               or result.get('returncode') not in (None, 0))
    correct = False if failure or match is False else (True if success and match is True else None)
    if status == 'UNKNOWN' and match is True:
        note += ' The reported objective matches, but solver status is unknown.'
    result.update(objective_matches_reference=match, objective_correct=correct,
                  reference_objective=target, correctness_note=note)
    return result


def execute(model: Path, task: Path, *, trusted_reference: bool, timeout: float) -> dict:
    if not (task / 'instance.json').is_file():
        raise FileNotFoundError(f'Missing instance data: {task / "instance.json"}')
    model = model.resolve()
    if not model.is_file():
        raise FileNotFoundError(model)
    mode = 'builder'
    if trusted_reference:
        tree = ast.parse(model.read_text(encoding='utf-8-sig'))
        functions = {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        if 'solve_algorithm' in functions:
            mode = 'solve_algorithm'
        elif not functions.intersection({'build_model', 'iter_models'}):
            mode = 'solve'
    with tempfile.TemporaryDirectory(prefix='efficientopt-') as directory:
        output = Path(directory) / 'execution.json'
        if mode == 'builder':
            command = [sys.executable, '-B', str(ROOT / 'evaluation/runner.py'), '--candidate', str(model),
                       '--instance', str(task / 'instance.json'), '--result', str(output)]
        else:
            command = [sys.executable, '-B', str(ROOT / 'evaluation/reference_runner.py'), '--model', str(model),
                       '--instance', str(task / 'instance.json'), '--entrypoint', mode, '--result', str(output)]
        try:
            process = subprocess.run(command, cwd=task, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {'solver_status': 'TIME_LIMIT', 'notes': f'Process exceeded {timeout:g} seconds.'}
        if output.is_file():
            result = json.loads(output.read_text(encoding='utf-8'))
        else:
            result = {'solver_status': 'ERROR', 'notes': (process.stderr or process.stdout)[-4000:]}
        result['returncode'] = process.returncode
        return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--instance', required=True, metavar='T01_002')
    parser.add_argument('--dataset-root', type=Path, default=ROOT / 'dataset/main')
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--candidate', type=Path, help='Python defining build_model(instance) or iter_models(instance).')
    source.add_argument('--reference', choices=('ordinary', 'expert'), help='Execute a bundled reference implementation.')
    source.add_argument('--result', type=Path, help='Check saved result JSON without importing Gurobi or executing code.')
    parser.add_argument('--output', type=Path, help='Default: output/<instance>/evaluation.json')
    parser.add_argument('--timeout', type=float, default=6000, help='Maximum execution-process wall time in seconds.')
    args = parser.parse_args(argv)
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error('--timeout must be finite and positive')
    task = task_directory(args.dataset_root, args.instance)
    reference_path = task / 'ground_truth/reference.json'
    reference = json.loads(reference_path.read_text(encoding='utf-8')) if reference_path.is_file() else {}
    if args.result:
        raw = json.loads(args.result.read_text(encoding='utf-8'))
    else:
        model = args.candidate or task / 'ground_truth' / ('ordinary_model.py' if args.reference == 'ordinary' else 'technique_model.py')
        raw = execute(model, task, trusted_reference=args.reference is not None, timeout=args.timeout)
    if not isinstance(raw, dict):
        raise ValueError('Execution result must be a JSON object.')
    result = score_result(raw, reference)
    result['problem_id'] = args.instance
    output = args.output or Path('output') / args.instance / 'evaluation.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({key: result.get(key) for key in ('problem_id', 'solver_status', 'objective_value',
                     'reference_objective', 'objective_matches_reference', 'objective_correct')}, indent=2))
    print(f'Saved: {output}')
    return 1 if result['solver_status'] == 'ERROR' else 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr)
        raise SystemExit(1)
