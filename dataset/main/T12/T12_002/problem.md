A city must calibrate 45 response coefficients so that the illumination predicted for every road segment matches the measured illumination as closely as possible. Each record in `observations` represents one distinct road segment and contains `features`, a 45-entry numeric vector describing that segment and its lamp configuration, and `y`, the measured illumination.

Choose all 45 response coefficients. Minimize the largest absolute difference, over all 215000 road segments, between the linear prediction from `features` and the corresponding measured value `y`.

Report the minimized maximum absolute deviation and the chosen response coefficients.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `observations`: array with 215000 distinct records.
  Record fields:
  1. `features` (array of 45 numbers)
  2. `y` (number)

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `observations[].features` is an array of integer values; entries retain their listed order.
