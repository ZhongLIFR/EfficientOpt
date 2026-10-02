Assign every listed task to exactly one operating window. Tasks joined by a pair in `conflict_edges` cannot use the same window. A window is used if any task is assigned to it, and every used window incurs `window_cost`. Minimize total used-window cost.

All task counts and conflict pairs are fixed and explicitly stored in `instance.json`; no graph data are generated at solve time.

## Data schema

- `num_tasks`: integer number of tasks, indexed from zero.
- `num_windows`: integer number of available windows, indexed from zero.
- `conflict_edges`: array of distinct two-integer task-index pairs.
- `window_cost`: nonnegative numeric cost per used window.
