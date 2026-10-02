The operator allocates a nonnegative continuous quantity to each of 305,000 units. Every unit belongs to one service group, has a published upper bound, and incurs a convex four-segment piecewise-linear cost described by five breakpoints and four increasing marginal slopes. Each group must receive at least its published total quantity. In addition, every allocated unit consumes each of 49 shared resources according to its published per-quantity coefficients, and the corresponding system capacity cannot be exceeded.

Minimize total piecewise-linear cost while satisfying all group minima and resource capacities. All fixed data are in `instance.json`: `group_count`, `group_minimum_quantity`, `resource_capacities`, and `units`. Each unit record gives `unit`, `group`, `breakpoints`, `slopes`, and `resource_use_per_quantity` parallel to the capacity array. Report the proven minimum and compact allocation totals.

## Data schema
The complete fixed instance is in `instance.json`; values are explicit and are not generated at runtime.
Field paths use `[]` for array records.
- `group_count`: integer.
- `group_minimum_quantity`: array.
- `resource_capacities`: array.
- `units`: array.
- Nested record fields:
  - `units[].unit`: integer.
  - `units[].group`: integer.
  - `units[].breakpoints`: array.
  - `units[].slopes`: array.
  - `units[].resource_use_per_quantity`: array.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `group_minimum_quantity` is an array of numeric values; entries may be integers or decimal numbers.
- `resource_capacities` is an array of numeric values; entries retain their listed order.
- `units` is an array of records; each record has the nested fields listed below.
- `units[].resource_use_per_quantity` is an array of numeric values; entries retain their listed order.
- `units[].slopes` is an array of numeric values; entries retain their listed order.
