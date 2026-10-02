An organization must make a one-to-one assignment between 1,120 maintenance crew records and 1,120 aircraft inspection job records. Every maintenance crew must receive exactly one aircraft inspection job, and every aircraft inspection job must be assigned to exactly one maintenance crew. Assigning pair `(i, j)` incurs the explicitly listed penalty `assignment_cost[i][j]`.

Choose the complete assignment that minimizes total penalty. Report the minimum total penalty and the selected worker-task index pairs.

All numerical data are fixed in `instance.json`; nothing is generated at solve time.

## Data schema

- `problem_id`, `title`, `domain`: descriptive strings.
- `worker_term`, `task_term`, `cost_unit`: terminology and unit strings.
- `workers`: 1,120 records, each with zero-based `index` and display `code`.
- `tasks`: 1,120 records, each with zero-based `index` and display `code`.
- `assignment_cost`: a 1,120 by 1,120 integer matrix. Entry `[i][j]` is the penalty for assigning worker `i` to task `j`.
