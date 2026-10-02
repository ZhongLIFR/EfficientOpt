A control center plans security patrol-robot transfers for 16 assets over `time_steps` consecutive steps of length `step_duration`. For each asset, `missions` gives its initial and required final position and velocity, its acceleration bound, and its fuel weight.

At every step, velocity changes by the chosen acceleration times `step_duration`, and position changes by the velocity at the beginning of the step times `step_duration`. The assets share one control resource, so the sum of their absolute accelerations in every step may not exceed `shared_absolute_acceleration_limit`.

Choose every acceleration and trajectory so that all final states are reached. Minimize the sum of each asset's `fuel_weight` times its absolute acceleration over all steps. Report the minimum weighted acceleration and the trajectories.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

- `problem_id`: string identifier; not used in the optimization model.
- `business_context`: descriptive string; not used in the optimization model.
- `time_steps`: positive integer number of steps.
- `step_duration`: positive numeric step length.
- `shared_absolute_acceleration_limit`: nonnegative numeric per-step shared bound.
- `missions`: array with 16 records.
  - `name`: string identifier.
  - `initial_position`, `initial_velocity`: numeric initial state.
  - `final_position`, `final_velocity`: numeric required terminal state.
  - `acceleration_bound`: nonnegative numeric per-step magnitude bound.
  - `fuel_weight`: positive numeric objective weight.

No values, records, or trajectories may be generated at solve time.
