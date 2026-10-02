The fixed instance.json contains a batch of independent staffing units. For each staffing unit choose bounded nonnegative whole-number senior, intermediate, and junior staffing levels x, y, z. Total staff cannot exceed cap; x-y must be at least dxy and y-z at least dyz. Minimize cx*x+cy*y+cz*z summed over all units. Report the minimum total staffing cost. All coefficients, bounds, and requirements are explicitly listed in instance.json; do not generate additional data.

All numerical data are explicitly provided in `instance.json`; do not generate or infer additional rows while solving.

## Data schema
The complete fixed instance is in `instance.json`; values are explicit and are not generated at runtime.
Field paths use `[]` for array records.
- `rows`: array.
- Nested record fields:
  - `rows[].cap`: integer.
  - `rows[].cx`: integer.
  - `rows[].cy`: integer.
  - `rows[].cz`: integer.
  - `rows[].dxy`: integer.
  - `rows[].dyz`: integer.
  - `rows[].ux`: integer.
  - `rows[].uy`: integer.
  - `rows[].uz`: integer.
