The fixed observation arrays `predictor_values` and `observed_values` contain 130000 entries each; entries at the same index form one observation pair.

Fit an affine line with a free intercept and slope to all observations. For each observation, measure the absolute difference between the measured response and the line's prediction, and minimize the sum of these absolute deviations.

Report the minimum sum of absolute residuals.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `predictor_values`: numerical array with 130000 records.
- `observed_values`: numerical array with 130000 records.
