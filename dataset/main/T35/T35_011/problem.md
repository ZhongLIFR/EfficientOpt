For each school district, choose nonnegative whole-number allocations `x`, `y`, `z`, and `w`. Meet the two stated pairwise minimum staffing requirements and the two stated maximum allocation-difference requirements while minimizing total allocation cost. Report the minimum total objective value.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `districts`: array of independent records. Each record contains a string `district`; integer requirements `minimum_xy`, `minimum_yz`, `maximum_z_minus_w`, and `maximum_x_minus_w`; and numeric costs `cost_x`, `cost_y`, `cost_z`, and `cost_w`.
