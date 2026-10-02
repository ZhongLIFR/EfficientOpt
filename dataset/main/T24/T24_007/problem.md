The fixed instance.json contains a batch of independent farms. For each farm choose nonnegative whole-number acres of corn, wheat, and soy. Require 2*corn+wheat at least food_requirement, wheat+soy at most soil_capacity, and corn-soy at least corn_over_soy. Minimize the stated crop costs across all farms. Report the minimum total cost. All coefficients, bounds, and requirements are explicitly listed in instance.json; do not generate additional data.

All numerical data are explicitly provided in `instance.json`; do not generate or infer additional rows while solving.

## Data schema
The complete fixed instance is in `instance.json`; values are explicit and are not generated at runtime.
Field paths use `[]` for array records.
- `farms`: array.
- Nested record fields:
  - `farms[].farm`: string.
  - `farms[].food_requirement`: integer.
  - `farms[].soil_capacity`: integer.
  - `farms[].corn_over_soy`: integer.
  - `farms[].corn_cost`: integer.
  - `farms[].wheat_cost`: integer.
  - `farms[].soy_cost`: integer.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `farms` is an array of records; each record has the nested fields listed below.
