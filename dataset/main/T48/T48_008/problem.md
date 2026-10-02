
A planner must construct one closed directed tour through all 84 locations. The tour starts at location 0, visits every other location exactly once, and returns to location 0. `cost[i][j]` is the cost of traveling directly from location `i` to location `j`; each pair in `forbidden_arcs` is a directed arc that cannot be used.

Minimize the total cost of the selected arcs. Report the minimum total cost and the complete cyclic visiting order.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated at runtime. Fields other than `node_count`, `cost`, and `forbidden_arcs` are retained source descriptors; they do not add vehicle-capacity or multi-vehicle constraints to this single-tour problem.

## Data schema

- `node_count`: integer scalar equal to 84.
- `cost`: array with 84 rows and 84 numeric entries per row.
- `forbidden_arcs`: array with 90 rows and two integer node indices per row.
- `coordinates`: auxiliary array with 84 two-number coordinate rows.
- `problem_id` and `_difficulty_seed`: auxiliary identifier/provenance scalars when present.
