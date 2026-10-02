The fixed instance.json contains a batch of regional production plans. For each plan choose nonnegative whole-number quantities x and y, bounded by ux and uy. Require 10x+15y at least rhs, 20x+30y at most twice rhs, and x-y at least gap. Minimize cx*x+cy*y summed over all plans. Report the minimum total cost. All coefficients, bounds, and requirements are explicitly listed in instance.json; do not generate additional data.

All numerical data are explicitly provided in `instance.json`; do not generate or infer additional rows while solving.

## Data schema
The complete fixed instance is in `instance.json`; values are explicit and are not generated at runtime.
Field paths use `[]` for array records.
- `rows`: array.
- Nested record fields:
  - `rows[].rhs`: integer.
  - `rows[].ux`: integer.
  - `rows[].uy`: integer.
  - `rows[].gap`: integer.
  - `rows[].cx`: integer.
  - `rows[].cy`: integer.
