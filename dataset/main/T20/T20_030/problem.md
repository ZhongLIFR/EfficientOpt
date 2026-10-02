A calibration service fits one linear predictor for each period. For period `t`, `F[t][i][j]` is the value of candidate feature `j` in observation `i`, and `y[t][i]` is the observed response. The coefficient of feature `j` in period `t` is a real number.

At most `max_features` features may be enabled in a period. Feature availability may be retired over time but cannot be re-enabled: if a feature is enabled in a later period, it must also be enabled in every earlier period. A coefficient is zero unless its feature is enabled; `coefficient_bounds` gives the coefficient bounds and `fixed` gives the per-period enabling cost. The `loss` field selects the prescribed per-period fitting loss: worst-observation absolute deviation (`cheb`) or the sum of absolute deviations (`l1`).

Minimize the total fitting loss plus feature-enabling costs. Report the minimum objective, the coefficients, and the enabled features for every period.

All numerical data are fixed and provided in the instance file.

## Data schema

- `periods`: integer scalar.
- `obs_per_period`: integer scalar.
- `features`: integer scalar.
- `max_features`: integer scalar.
- `y`: array with 42 rows; each row is an array with 240 numeric values.
- `F`: array with 42 rows; each row is an array with 240 rows; each row is an array with 100 numeric values.
- `coefficient_bounds`: array with 100 positive numeric values.
- `fixed`: array with 100 nonnegative numeric values.
- `loss`: string scalar equal to `cheb` or `l1`.
