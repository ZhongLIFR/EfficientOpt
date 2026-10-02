A calibration service fits one linear predictor in each period. For period `t`, `F[t][i][j]` is the value of feature `j` in observation `i`, and `y[t][i]` is the observed response. The coefficient of feature `j` in period `t` is a real number.

At most `max_features` features may be enabled in any period. A feature may be disabled after an earlier period, but once disabled it cannot be enabled again in a later period. A coefficient must be zero whenever its feature is disabled. For feature `j`, `coefficient_bounds[j]` is the absolute bound on its coefficient and `fixed[j]` is the cost paid in every period in which it is enabled.

The `loss` field specifies the fitting loss. If it is `cheb`, the loss of a period is the largest absolute residual among that period's observations. If it is `l1`, the loss is the sum of absolute residuals. Minimize the total fitting loss over all periods plus all feature-enabling costs. Report the minimum objective, coefficients, and enabled features.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

- `periods`: positive integer; number of periods.
- `obs_per_period`: positive integer; observations in every period.
- `features`: positive integer; number of candidate features.
- `max_features`: integer in `[0, features]`.
- `y`: array of shape `[periods][obs_per_period]` containing numeric observed responses.
- `F`: array of shape `[periods][obs_per_period][features]` containing numeric feature values.
- `coefficient_bounds`: array of `features` nonnegative numeric absolute coefficient bounds.
- `fixed`: array of `features` nonnegative numeric per-period enabling costs.
- `loss`: string, either `cheb` or `l1`.
