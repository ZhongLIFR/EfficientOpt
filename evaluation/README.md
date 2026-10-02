# Local evaluation

Run commands from the repository root with Python 3.10 or newer.
Before executing a reference or candidate, download and extract the numerical
instances as described in [dataset/README.md](../dataset/README.md).

```bash
python -m pip install -r requirements.txt
python evaluate.py --instance T01_002 --candidate path/to/candidate.py
python evaluate.py --instance T01_002 --reference expert
python evaluate.py --instance T01_002 --result path/to/execution.json
```

Candidates define `build_model(instance)` returning a Gurobi model, or
`iter_models(instance)` yielding Gurobi models whose objectives are summed.
The runner sets Threads=1, Seed=0, MIPGap=0, and TimeLimit=5400 seconds per model.
Gurobi execution requires a suitable license. Code runs in a subprocess; it is
not a security sandbox. `--timeout` bounds the entire process (default 6000 s).

`--result` uses only the standard library and does not execute code. It accepts
`objective_value` and `solver_status`, or the same fields inside
`execution_result`. Results are compared with each task's
`ground_truth/reference.json`; numerical agreement is not a proof of feasibility
or modeling correctness. Unknown targets/statuses remain unconfirmed.
`--output` defaults to `output/<instance>/evaluation.json`.

Bundled references also support their existing `solve()` / `solve_algorithm()`
interfaces, in a separate process with the task directory as its working
directory. Their reported status is preserved; missing status is `UNKNOWN`.
`solve_algorithm` shares a cumulative 5400-second Gurobi Runtime budget across
its solves and reports the sum of their Runtime and Work measurements.
For native references, `timing_source` distinguishes their reported wall time
from Gurobi Runtime. Their original dictionary is retained in `raw_result`;
historical Gurobi memory fields with inconsistent units are not exposed as
normalized top-level MB measurements.
Use `--dataset-root dataset/supplemental` for supplemental tasks. These tasks
do not have the main benchmark's verified objective targets.

For LLM-based technique attribution, see [judge/README.md](judge/README.md).

```bash
python -m unittest discover -s tests -v
```
