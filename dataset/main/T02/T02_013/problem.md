A controller steers a one-dimensional research vehicle through exactly 16000 consecutive unit-time periods. The vehicle has given initial and final position and velocity, and the magnitude of the acceleration in every period is bounded.

Choose one continuous acceleration for each period. The discrete dynamics advance velocity using the chosen acceleration and advance position using the velocity at the start of the period. The boundary states must equal the supplied initial and final states.

Minimize the largest absolute acceleration used in any period. Report the minimum peak acceleration.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `periods`: integer scalar equal to 16000.
- `initial_position`: numeric scalar.
- `initial_velocity`: numeric scalar.
- `final_position`: numeric scalar.
- `final_velocity`: numeric scalar.
- `acceleration_bound`: nonnegative numeric scalar.
