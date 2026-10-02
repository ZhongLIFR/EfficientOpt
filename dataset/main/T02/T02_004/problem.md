An analyst fits a straight-line relationship to 300,000 fixed observations. Each record in `observations` contains a predictor and a measured response. The line has a free intercept and a free slope; each prediction is the line's response at the observation's predictor.

Choose the intercept and slope to minimize the largest absolute prediction error over all observations. Report the minimum possible maximum error and the fitted intercept and slope.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `observations`: array with 300,000 records.
  Record fields:
  1. `predictor` (number)
  2. `observed_value` (number)
