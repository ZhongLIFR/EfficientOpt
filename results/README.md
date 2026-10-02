# Paper Results

These CSV files contain the frozen results used in the
[EfficientOpt paper](https://arxiv.org/abs/2609.38884). They were not rerun for this
release. Complete LLM generation trajectories are not bundled.

The main analysis concerns **computational efficiency on correctly solved tasks**.
Numerical accuracy establishes which programs qualify for cost comparisons.

| File | Contents |
| --- | --- |
| [cost_ratios.csv](cost_ratios.csv) | Paper's paired solver-time, solver-work, and preparation-plus-solving cost ratios |
| [model_sizes.csv](model_sizes.csv) | Ordinary/expert reference model dimensions |
| [accuracy.csv](accuracy.csv) | Supplementary overall numerical accuracy for 11 models |
| [accuracy_by_technique.csv](accuracy_by_technique.csv) | Accuracy pooled by target technique |
| [accuracy_by_model_technique.csv](accuracy_by_model_technique.csv) | Accuracy by model and technique |
| [accuracy_records.csv](accuracy_records.csv) | Task-level outcomes and reference objectives |

## Computational costs

`cost_ratios.csv` reproduces the four cost columns from the paper's main results
table. Values are **LLM/reference shifted geometric ratios**, rounded to two
decimal places as in the paper. The shift is one second for time and one solver
work unit for `Work`. Below 1 means lower LLM cost under this aggregation; the
values are not ratios of summed costs or unshifted speedups.

- `runtime_vs_ordinary` and `runtime_vs_expert`: Gurobi `Runtime` relative to each reference.
- `work_vs_expert`: Gurobi `Work` relative to the expert reference.
- `build_opt_vs_expert`: recorded preparation plus separately timed solver calls, relative to the expert reference. This subtotal does not cover all program or request costs.

Paired cost comparisons use **543 tasks** with comparable ordinary and expert
reference executions, further restricted by numerical correctness and available
measurements. The four ratios in each row use the same complete measurements:
**4,148 model–task pairs** overall. Task sets differ between models. The paper's
solver-runtime analysis requires fewer measurements and includes **4,202 correct
runs**; see the paper for comparisons on shared task sets.

## Supplementary numerical outcomes

Accuracy uses **561 main tasks per model**, including generation and execution
failures: **6,171 retained outcomes** across 11 models. A numerically correct
outcome requires an optimal solver status and a finite objective matching the
verified reference within the paper's tolerances.

Tasks outside the reference-cost subset still contribute to accuracy.
Supplemental tasks are outside these statistics.

Empty cells mean unavailable, not zero. Source hashes identify the frozen analysis;
input hashes and identity checks cover only the records where that evidence was
available. Model-size counts do not establish faster solving. See Appendix D for
measurement scopes and aggregation rules.
