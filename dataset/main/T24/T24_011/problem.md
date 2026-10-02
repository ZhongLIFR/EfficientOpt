The fixed instance.json contains a batch of independent department groups. For each group choose nonnegative whole-number staffing levels x1 through x4. Require x1+x2 at most cap12, x3+x4 at most cap34, x1-x3 at least d1, and x2-x4 at least d2. Minimize the stated four-category costs over all groups. Report the minimum total cost. All coefficients, bounds, and requirements are explicitly listed in instance.json; do not generate additional data.

All numerical data are explicitly provided in `instance.json`.

## Data schema
The complete fixed instance is in `instance.json`; values are explicit and are not generated at runtime.
Field paths use `[]` for array records.
- `rows`: array.
- Nested record fields:
  - `rows[].cap12`: integer.
  - `rows[].cap34`: integer.
  - `rows[].d1`: integer.
  - `rows[].d2`: integer.
  - `rows[].c1`: integer.
  - `rows[].c2`: integer.
  - `rows[].c3`: integer.
  - `rows[].c4`: integer.
