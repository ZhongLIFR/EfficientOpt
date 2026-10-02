A resource planner must choose a nonnegative whole-number allocation for each listed resource option. Every policy row must be satisfied in its stated direction. Minimize total allocation cost. All authoritative names, costs, coefficients, directions, and right-hand sides are fixed and explicitly stored in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `business_context`: display string describing the planning setting.
- `resource_types`: array of exactly 146 strings; array position is the resource index.
- `cost`: array of exactly 146 nonnegative integers; `cost[j]` is the unit cost of resource `j`.
- `policy_rows`: array of exactly 256 records.
- `policy_rows[].policy`: display string unique within the instance.
- `policy_rows[].indices`: array of distinct integer resource indices in the range 0 through 145.
- `policy_rows[].coefficients`: array of integers of the same length and order as `indices`.
- `policy_rows[].sense`: string equal to `<=` or `>=`.
- `policy_rows[].rhs`: integer right-hand side.
