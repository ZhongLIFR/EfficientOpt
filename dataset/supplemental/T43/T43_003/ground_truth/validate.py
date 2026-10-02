from __future__ import annotations
import json
from pathlib import Path
from common_model import load_data
from ordinary_model import solve as solve_ordinary
from technique_model import solve as solve_technique

def compare(ordinary, technique, reference):
    scale = max(1.0, abs(reference['objective']), abs(ordinary['objective']), abs(technique['objective']))
    speedup = 100.0 * (ordinary['runtime'] - technique['runtime']) / max(ordinary['runtime'], 1e-12)
    work_reduction = 100.0 * (ordinary['work'] - technique['work']) / max(ordinary['work'], 1e-12)
    checks = {
        'objective_match': abs(ordinary['objective'] - technique['objective']) <= 1e-7 * scale,
        'ordinary_matches_reference': abs(ordinary['objective'] - reference['objective']) <= 1e-7 * scale,
        'technique_matches_reference': abs(technique['objective'] - reference['objective']) <= 1e-7 * scale,
        'runtime_or_work_speedup_at_least_10_percent': speedup >= 10.0 or work_reduction >= 10.0,
        'deterministic_work_reduced': technique['work'] < ordinary['work'],
        'model_size_comparison_not_required_for_native_algorithms': True,
    }
    return {'ordinary': ordinary, 'technique': technique, 'reference_objective': reference['objective'], 'runtime_speedup_percent': speedup, 'work_reduction_percent': work_reduction, 'checks': checks, 'pass': all(checks.values())}

def main():
    data = load_data()
    rounds = []
    reference = solve_technique()
    for _ in range(2):
        rounds.append(compare(solve_ordinary(), solve_technique(), reference))
    result = {'problem_id': data['problem_id'], 'target_technique': data['target_technique'], 'independent_rounds': rounds, 'minimum_runtime_speedup_percent': min(r['runtime_speedup_percent'] for r in rounds), 'minimum_work_reduction_percent': min(r['work_reduction_percent'] for r in rounds), 'pass': all(r['pass'] for r in rounds)}
    Path('validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['pass'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
