A sensor-calibration study contains 1,300,000 fixed observations and two recorded features per observation. Choose one real coefficient for each feature. Minimize the sum of absolute prediction errors plus one half of `quadratic_weight` times the sum of squared coefficients. Report the minimum objective value and the fitted coefficients.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `quadratic_weight`: positive numeric scalar.
- `features`: array with 1,300,000 rows and exactly two numeric entries per row; row order is aligned with `target`.
- `target`: array with 1,300,000 numeric response values.
