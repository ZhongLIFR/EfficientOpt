A controller steers a one-dimensional rocket through a fixed number of unit-time periods. The rocket has given initial and final position and velocity, and the magnitude of the acceleration in every period is bounded.

Choose one continuous acceleration for each period. The discrete dynamics advance velocity using the chosen acceleration and advance position using the velocity at the start of the period. The boundary states must equal the supplied initial and final states.

Minimize the largest absolute acceleration used in any period. Report the minimum peak acceleration and the complete acceleration plan.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `periods`: integer scalar.
- `initial_position`: numeric scalar.
- `initial_velocity`: numeric scalar.
- `final_position`: numeric scalar.
- `final_velocity`: numeric scalar.
- `acceleration_bound`: nonnegative numeric scalar.
