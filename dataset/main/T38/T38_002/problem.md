A calibration study contains 1500000 fixed observations and 3 recorded features per observation. `features[i][j]` is feature `j` for observation `i`, `target[i]` is its response, and `quadratic_weight` is a positive coefficient-regularization weight.

Choose one real coefficient per feature. Minimize the sum of absolute prediction errors plus one half of `quadratic_weight` times the sum of squared coefficients. Report the minimum objective and fitted coefficients.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `quadratic_weight`: positive numeric scalar equal to 1.0.
- `features`: array with 1500000 rows and 3 numeric entries per row.
- `target`: array with 1500000 numeric entries.
