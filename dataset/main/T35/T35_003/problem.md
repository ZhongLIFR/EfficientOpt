For every operational allocation block, choose a nonnegative whole-number quantity for each option listed in `variables`. Minimize the sum of the option-specific costs. In each block, satisfy the supplied exact linear balance and every supplied linear lower or upper limit. Report the minimum total objective value.

All coefficients, right-hand sides, and costs are fixed and explicitly stored in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `variables`: ordered array of unique option-name strings.
- `blocks`: array of independent records. Each record contains:
  - `block`: nonempty identifier string;
  - `costs`: object with one numeric cost for every name in `variables`;
  - `equality`: object with `coefficients` (one numeric coefficient for every name in `variables`) and numeric `rhs`;
  - `constraints`: array of objects, each containing `coefficients`, `sense`, and `rhs`. `coefficients` may omit zero coefficients and may use only names from `variables`; `sense` is either `<=` or `>=`; `rhs` is numeric.
