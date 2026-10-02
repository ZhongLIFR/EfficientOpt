A calibration service fits one linear predictor in each of 50 periods using 120 candidate features and 300 observations per period. `F[t][i][j]` is feature `j` for observation `i` in period `t`, and `y[t][i]` is its response.

At most `max_features` features may be enabled in a period. A coefficient must be zero unless its feature is enabled and is bounded in magnitude by `coefficient_bounds[j]`. If a feature is enabled in a later period, it must also be enabled in every earlier period; equivalently, once disabled it cannot be re-enabled. `fixed[j]` is charged for every period in which feature `j` is enabled. The `loss` field is either `cheb` (sum across periods of the maximum absolute residual in each period) or `l1` (sum of all absolute residuals).

Minimize fitting loss plus enabling costs. Report the objective, coefficients, and enabled features.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated at runtime.

## Data schema

- `periods`: integer scalar equal to 50.
- `obs_per_period`: integer scalar equal to 300.
- `features`: integer scalar equal to 120.
- `max_features`: integer scalar equal to 18.
- `y`: array shaped `[periods][obs_per_period]`.
- `F`: array shaped `[periods][obs_per_period][features]`.
- `coefficient_bounds` and `fixed`: arrays with 120 numeric entries each.
- `loss`: string equal to `cheb`.
