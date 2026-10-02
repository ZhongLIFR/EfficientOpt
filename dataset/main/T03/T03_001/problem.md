The instance contains independent regional energy plans and a shared operating-window schedule.

For each row `r`, choose nonnegative whole-number quantities `x[r]`, `y[r]`, and `z[r]` for primary, secondary, and reserve energy. They may not exceed the corresponding limits `ub_x`, `ub_y`, and `ub_z`. Their sum may not exceed `capacity`; `x[r]` must exceed `y[r]` by at least `x_over_y`, and `y[r]` must exceed `z[r]` by at least `y_over_z`. The row cost is the stated linear cost of these quantities.

In addition, each coordination task must be assigned to exactly one operating window. Tasks joined by an edge in `conflict_edges` cannot share a window. A window is open if any task is assigned to it, and each open window incurs `window_activation_cost`. Minimize the sum of all row costs and all open-window costs.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

- `categories`: array of three descriptive category names corresponding to `x`, `y`, and `z`.
- `business_units`: string describing the row collection.
- `rows`: array of regional-plan records.
- `rows[].unit`: string identifier.
- `rows[].capacity`: nonnegative integer.
- `rows[].x_over_y`, `rows[].y_over_z`: nonnegative integer separation requirements.
- `rows[].ub_x`, `rows[].ub_y`, `rows[].ub_z`: nonnegative integer upper bounds.
- `rows[].cost_x`, `rows[].cost_y`, `rows[].cost_z`: numeric unit costs.
- `coordination`: object describing the shared schedule.
- `coordination.num_tasks`: positive integer.
- `coordination.num_windows`: positive integer.
- `coordination.conflict_edges`: array of two-integer task-index pairs; task indices are zero-based.
- `coordination.window_activation_cost`: nonnegative numeric cost per open window.
