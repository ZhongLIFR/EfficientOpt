The fixed instance.json contains a batch of independent transport districts. For each district choose nonnegative whole-number route allocations x1 through x4. Require x1+x2 at most cap12 and x3+x4 at most cap34; x3-x1 at least d3 and x4-x2 at least d4. Minimize the four stated route costs across all districts. Report the minimum total cost. All coefficients, bounds, and requirements are explicitly listed in instance.json; do not generate additional data.

All numerical data are explicitly provided in `instance.json`.

## Data schema
The complete fixed instance is in `instance.json`; values are explicit and are not generated at runtime.
Field paths use `[]` for array records.
- `rows`: array.
- Nested record fields:
  - `rows[].cap12`: integer.
  - `rows[].cap34`: integer.
  - `rows[].d3`: integer.
  - `rows[].d4`: integer.
  - `rows[].c1`: integer.
  - `rows[].c2`: integer.
  - `rows[].c3`: integer.
  - `rows[].c4`: integer.
