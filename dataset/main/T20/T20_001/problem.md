A ground control center must plan the transfer of every mission in `missions` across `time_steps` consecutive time steps, each lasting `step_duration_seconds` seconds. For every mission, the data give its `name`, the `initial_position` and `initial_velocity` at the start of the horizon, the `final_position` and `final_velocity` it must reach by the end, the largest acceleration magnitude `acceleration_bound` it may apply at any single step, and a `fuel_weight` that scales its acceleration in the objective.

At each time step the missions share one ground-controlled propulsion power source, so the sum of the absolute accelerations applied by all missions in that step may not exceed `shared_absolute_acceleration_limit`. Within a mission, the velocity at the next step equals the velocity at the current step plus the acceleration applied, and the position then advances by the velocity at the start of that step, so the full trajectory is determined by the sequence of acceleration choices.

Minimize the total weighted acceleration, which sums over every mission and every time step the mission's `fuel_weight` times the absolute acceleration applied at that step, while meeting the start and end conditions of every mission

Report the minimum total weighted acceleration and the trajectory of position and velocity for every mission at every time step.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `time_steps`: integer scalar.
- `step_duration_seconds`: number scalar.
- `shared_absolute_acceleration_limit`: number scalar.
- `missions`: array with 20 records.
  Record fields:
  1. `name` (string)
  2. `initial_position` (number)
  3. `initial_velocity` (number)
  4. `final_position` (number)
  5. `final_velocity` (number)
  6. `acceleration_bound` (number)
  7. `fuel_weight` (number)

Additional fixed fields retained for instance identity or provenance (not used by the optimization model):

- `kind`: fixed instance label string; auxiliary metadata not used in the optimization model.

- `problem_id`: fixed identifier string; auxiliary metadata not used in the optimization model.

