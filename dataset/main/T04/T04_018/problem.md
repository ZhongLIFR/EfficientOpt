A fixed allocation network contains a set of candidate assignments. Each candidate has a lower bound, an upper bound, and a per-unit cost. The candidates are divided into named requirement groups; a candidate may belong to more than one group. For every group, the sum of its listed candidate assignments must satisfy the stated `<=`, `>=`, or `=` requirement.

Choose a nonnegative whole-number quantity for every candidate assignment. Respect every candidate bound and every group requirement, and minimize the total assignment cost. Report the minimum total cost and a compact description of the selected assignments.

All numerical data are explicitly stored in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `categories`: array of 2,310,000 candidate-assignment names. Its position is the candidate index used by all other arrays.
- `rows`: array containing one fixed allocation record.
- `rows[].unit`: descriptive string for the allocation record.
- `rows[].lb`: array of 2,310,000 integer lower bounds, aligned with `categories`.
- `rows[].ub`: array of 2,310,000 integer upper bounds, aligned with `categories`.
- `rows[].cost`: array of 2,310,000 integer unit costs, aligned with `categories`.
- `rows[].groups`: array of 140,000 requirement-group records.
- `rows[].groups[].name`: descriptive group name.
- `rows[].groups[].indices`: array of zero-based candidate indices included in the group.
- `rows[].groups[].sense`: one of `<=`, `>=`, or `=`.
- `rows[].groups[].rhs`: integer right-hand side.
- `business_units`: auxiliary descriptive string; it is not numerical decision data.
- `constraint_semantics`: auxiliary descriptive string; the operative requirements are the explicit `sense` and `rhs` values in `rows[].groups`.
