An organization must make a one-to-one assignment between 1,120 resident records and 1,120 rotation slot records. Every resident must receive exactly one rotation slot, and every rotation slot must be assigned to exactly one resident. Assigning pair `(i, j)` incurs the explicitly listed penalty `assignment_cost[i][j]`.

Choose the complete assignment that minimizes total penalty. Report the minimum total penalty and the selected worker-task index pairs.

All numerical data are fixed in `instance.json`; nothing is generated at solve time.

## Data schema

- `problem_id`, `title`, `domain`: descriptive strings.
- `worker_term`, `task_term`, `cost_unit`: terminology and unit strings.
- `workers`: 1,120 records, each with zero-based `index` and display `code`.
- `tasks`: 1,120 records, each with zero-based `index` and display `code`.
- `assignment_cost`: a 1,120 by 1,120 integer matrix. Entry `[i][j]` is the penalty for assigning worker `i` to task `j`.
