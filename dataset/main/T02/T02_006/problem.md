A controller steers a one-dimensional research vehicle through exactly 12000 consecutive unit-time periods. The vehicle has given initial and final position and velocity, and the magnitude of the acceleration in every period is bounded.

Choose one continuous acceleration for each period. The discrete dynamics advance velocity using the chosen acceleration and advance position using the velocity at the start of the period. The boundary states must equal the supplied initial and final states.

Minimize the largest absolute acceleration used in any period. Report the minimum peak acceleration.

All numerical data are fixed and explicitly provided in `instance.json`; no values are generated or sampled while solving.

## Data schema

- `periods`: integer scalar equal to 12000.
- `initial_position`, `initial_velocity`, `final_position`, `final_velocity`: numeric scalars.
- `acceleration_bound`: nonnegative numeric scalar.
