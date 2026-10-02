"""Subprocess adapter for bundled solve() and solve_algorithm(instance, context)."""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path
import sys
import time


class SolverContext:
    """Apply the fixed solver settings when a bundled algorithm requests a solve."""
    def __init__(self, time_limit=5400.0):
        self.time_limit = float(time_limit)
        self.runtime = 0.0
        self.work = 0.0
        self.calls = 0
        self.statuses = []

    def optimize(self, model, callback=None):
        import gurobipy as gp
        if not isinstance(model, gp.Model):
            raise TypeError('context.optimize expects gurobipy.Model')
        remaining = self.time_limit - self.runtime
        if remaining <= 0:
            self.statuses.append('TIME_LIMIT')
            return 'TIME_LIMIT'
        for key, value in {'OutputFlag': 0, 'Threads': 1, 'Seed': 0, 'MIPGap': 0, 'TimeLimit': max(0.001, remaining)}.items():
            model.setParam(key, value)
        model.update()
        model.optimize() if callback is None else model.optimize(callback)
        runtime = float(model.Runtime)
        if not math.isfinite(runtime):
            raise RuntimeError('Model did not report finite Gurobi Runtime')
        self.runtime += runtime
        self.work += float(model.Work)
        self.calls += 1
        names = {getattr(gp.GRB, name): name for name in (
            'OPTIMAL', 'INFEASIBLE', 'INF_OR_UNBD', 'UNBOUNDED', 'TIME_LIMIT',
            'INTERRUPTED', 'NUMERIC', 'SUBOPTIMAL', 'ITERATION_LIMIT', 'NODE_LIMIT')}
        status = names.get(model.Status, f'UNKNOWN({model.Status})')
        self.statuses.append(status)
        return status


def run(model_path: Path, instance_path: Path, entrypoint: str) -> dict:
    start = time.perf_counter()
    sys.path.insert(0, str(model_path.parent.resolve()))
    try:
        spec = importlib.util.spec_from_file_location('efficientopt_reference', model_path)
        if spec is None or spec.loader is None:
            raise ImportError(f'Cannot load {model_path}')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        method = getattr(module, entrypoint, None)
        if not callable(method):
            raise TypeError(f'Reference must define {entrypoint}().')
        if entrypoint == 'solve_algorithm':
            context = SolverContext()
            instance = json.loads(instance_path.read_text(encoding='utf-8-sig'))
            result = method(instance, context)
            if not isinstance(result, dict):
                raise TypeError('Reference algorithm must return a dictionary.')
            status = result.get('solver_status')
            if status == 'OPTIMAL' and (not context.statuses or any(value != 'OPTIMAL' for value in context.statuses)):
                raise RuntimeError('Algorithm claimed OPTIMAL without all Gurobi solves being OPTIMAL')
            if status != 'OPTIMAL':
                result['objective_value'] = None
            result['solver_runtime_seconds'] = context.runtime
            result['work_units'] = context.work
            result['optimize_calls'] = context.calls
        else:
            result = method()
        if not isinstance(result, dict):
            raise TypeError('Reference solve() must return a dictionary.')
        if entrypoint == 'solve':
            raw = dict(result)
            result = dict(raw)
            result['raw_result'] = raw
            # Historical solve() references use inconsistent units for these names.
            # Keep them in raw_result only; do not present them as normalized MB.
            for key in ('gurobi_mem_used_mb', 'gurobi_max_mem_used_mb', 'max_mem_used_mb'):
                result.pop(key, None)
            result['timing_source'] = ('reference_reported_runtime_s' if 'runtime_s' in raw
                                       else 'reference_reported_wall_time')
        else:
            result['timing_source'] = 'sum_of_gurobi_model_runtime'
        result.setdefault('solver_status', result.get('status') or 'UNKNOWN')
    except Exception as error:
        result = {'solver_status': 'ERROR', 'notes': f'{type(error).__name__}: {error}'}
    result['total_process_s'] = time.perf_counter() - start
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--instance', type=Path, required=True)
    parser.add_argument('--entrypoint', choices=('solve', 'solve_algorithm'), required=True)
    parser.add_argument('--result', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.model, args.instance, args.entrypoint)
    args.result.parent.mkdir(parents=True, exist_ok=True)
    args.result.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return 1 if result.get('solver_status') == 'ERROR' else 0


if __name__ == '__main__':
    raise SystemExit(main())
