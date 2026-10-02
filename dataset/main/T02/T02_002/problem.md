A spacecraft controller steers one one-dimensional rocket through 27,000 consecutive unit-time periods. The initial and final position and velocity and the common acceleration bound are fixed in `instance.json`.

Choose one continuous acceleration for every period. Velocity advances by the selected acceleration and position advances using the velocity at the start of the period. The supplied initial and final boundary states must be met exactly. Minimize the largest absolute acceleration used over the complete horizon.

Report the minimum peak acceleration and the complete acceleration plan.

## Data schema

The complete fixed instance is in `instance.json`; no value is generated or sampled while constructing or solving the optimization model.

- `periods`: integer scalar equal to 27,000.
- `initial_position`: number scalar.
- `initial_velocity`: number scalar.
- `final_position`: number scalar.
- `final_velocity`: number scalar.
- `acceleration_bound`: number scalar.
- `problem_id`: fixed identifier string.
- `kind`: fixed instance label string.
