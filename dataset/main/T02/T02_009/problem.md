A calibration service fits one linear predictor for each period. For period `t`, `F[t][i][j]` is the value of candidate feature `j` in observation `i`, and `y[t][i]` is the observed response. The coefficient of feature `j` in period `t` is a real number.

At most `max_features` features may be enabled in a period. An enabled feature remains enabled in all later periods, and a coefficient is zero unless its feature is enabled; `coefficient_bounds` gives the coefficient bounds and `fixed` gives the enabling cost. The `loss` field selects the prescribed per-period fitting loss: worst-observation absolute deviation (`cheb`) or the sum of absolute deviations (`l1`; when omitted, use the default specified by the instance and model).

Minimize the total fitting loss plus feature-enabling costs. Report the minimum objective, the coefficients, and the enabled features for every period.

All numerical data are fixed and provided in the instance file.

## Data schema

- `periods`: integer scalar.
- `obs_per_period`: integer scalar.
- `features`: integer scalar.
- `max_features`: integer scalar.
- `y`: array with 50 rows; each row is an array with 300 values.
- `F`: array with 50 rows; each row is an array with 300 rows; each row is an array with 120 values.
- `coefficient_bounds`: array with 120 values.
- `fixed`: array with 120 values.
- `loss`: string scalar.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `coefficient_bounds` is an array of numeric values; entries retain their listed order.
- `fixed` is an array of integer values; entries retain their listed order.
