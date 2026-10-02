An analyst must fit a quadratic model to 256,000 observations stored in `observations` in `instance.json`. Each record contains `features`, a 3-entry vector describing one observation, and `y`, the observed target value. The three entries of `features` together encode the constant term, the slope term, and the squared term of the quadratic relationship, so the fitted value of an observation is the coefficient-weighted sum of its three feature entries.

Report the minimum total absolute residual and the three fitted coefficients.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `observations`: array with 256,000 records.
  Record fields:
  1. `features` (array)
  2. `y` (number)

All observation feature vectors and response values are explicitly fixed in instance.json; no values are generated during solving.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `observations[].features` is an array of numeric values; entries retain their listed order.
