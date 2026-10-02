For each team, assign exactly `total_tasks` indivisible tasks among nonnegative whole-number quantities `x`, `y`, and `z`. Meet the minimum `x+y` workload and maximum `y+z` workload, and minimize total effort. Report the minimum total objective value.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `teams`: array of independent records. Each record contains a string `team`; nonnegative integers `total_tasks`, `min_x_plus_y`, and `max_y_plus_z`; and numeric effort coefficients `effort_x`, `effort_y`, and `effort_z`.
