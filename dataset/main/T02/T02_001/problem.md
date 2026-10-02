A controller steers a one-dimensional rocket through 27,000 consecutive unit-time periods. The initial and final position and velocity and the common acceleration bound are fixed in `instance.json`.

Choose one continuous acceleration for every period. Velocity advances by the selected acceleration, and position advances by the velocity at the start of the period. The initial and final boundary states must be met exactly. Minimize the largest absolute acceleration used in any period.

Report the minimum peak acceleration and the complete acceleration plan.

## Data schema

The complete fixed instance is in `instance.json`; no value is generated or sampled while constructing or solving the optimization model.

- `periods`: integer scalar equal to 27,000.
- `initial_position`: number scalar.
- `initial_velocity`: number scalar.
- `final_position`: number scalar.
- `final_velocity`: number scalar.
- `acceleration_bound`: positive number scalar giving the common magnitude bound on every acceleration.
