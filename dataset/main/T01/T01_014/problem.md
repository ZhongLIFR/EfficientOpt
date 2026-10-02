The planning instance contains independent client funds. For each row, choose nonnegative whole-number allocations for `fund_x` and `fund_y`. The linear combination `eq_coeff` dot the allocation vector must meet `minimum_required` and cannot exceed `maximum_available`; these two supplied values are equal for every row. Every listed side constraint must also hold.

In addition, 60 explicitly listed coordination tasks must each be assigned to exactly one of 13 interchangeable operating windows. Pairs in `conflict_edges` share a scarce resource and cannot use the same window. Activating a window incurs `window_activation_cost`.

Minimize the sum of all category allocation costs and all activated-window costs. Report the minimum total cost.

## Data schema
The complete fixed instance is in `instance.json`; values are explicit and are not generated at runtime.
Field paths use `[]` for array records.
- `categories`: array.
- `business_units`: string.
- `equality_semantics`: string.
- `rows`: array.
- `coordination`: object.
- `coordination.num_tasks`: integer.
- `coordination.num_windows`: integer.
- `coordination.conflict_edges`: array.
- `coordination.window_activation_cost`: integer.
- Nested record fields:
  - `rows[].unit`: string.
  - `rows[].minimum_required`: integer.
  - `rows[].maximum_available`: integer.
  - `rows[].eq_coeff`: array.
  - `rows[].eq_rhs`: integer.
  - `rows[].cost`: array.
  - `rows[].side`: array.
  - `rows[].side[].coeff`: array.
  - `rows[].side[].sense`: string.
  - `rows[].side[].rhs`: integer.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `categories` is an array of strings; entries retain their listed order.
- `rows[].cost` is an array of integer values; entries retain their listed order.
- `rows[].eq_coeff` is an array of integer values; entries retain their listed order.
- `rows[].side[].coeff` is an array of integer values; entries retain their listed order.
- `coordination.conflict_edges` is an array of positional rows; each row contains 2 entries of numeric type.
