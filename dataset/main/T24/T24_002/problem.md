A railway operator must choose a subset of pre-approved crew work packages to cover every transport task in the planning period. The instance contains 507 tasks and 63,009 candidate work packages. The `package_task` array holds 409,349 records, each pairing a `package_id` with a `task_id` that the package can cover, and the `package_difficulty` array holds 63,009 records, each pairing a `package_id` with its `difficulty` level, which is either `easy` or `hard`. An `easy` package costs 1 unit of direct operating cost, and a `hard` package costs 2 units.

Each package may be chosen at most once, and every task must be covered by at least one chosen package. To satisfy the cross-region joint-operation coverage agreement, the chosen packages must include exactly 65 `hard` packages.

Minimize the total direct operating cost of the chosen packages. All candidate packages, coverage relations, and difficulty levels are given explicitly in `instance.json`.

Report the minimum total cost and the `package_id` of every chosen package.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `package_difficulty`: array with 63,009 records.
  Record fields:
  1. `package_id` (integer)
  2. `difficulty` (string)
- `package_task`: array with 409,349 records.
  Record fields:
  1. `package_id` (integer)
  2. `task_id` (integer)
