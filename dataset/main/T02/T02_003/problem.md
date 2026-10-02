An engineer calibrates the power of 60 road lamps. Every lamp power is a continuous nonnegative value no greater than `power_bounds`. Each of 900,000 distinct road segments lists the lamps that illuminate it, the contribution of each listed lamp per unit power, and its required illumination target.

Choose one power level for every lamp. A segment's achieved illumination is the sum of the listed lamp contributions multiplied by their chosen powers. Minimize the largest absolute difference between achieved and required illumination over all road segments.

Report the minimum possible maximum deviation and the chosen power of every lamp.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled while constructing or solving the optimization model.

- `num_lamps`: integer scalar equal to 60.
- `power_bounds`: positive numeric upper bound shared by all lamp powers.
- `segments`: array of 900,000 fixed records. Each record contains:
  - `lamp_contributions`: array of `[lamp_index, contribution]` pairs; lamp indices range from 0 to 59;
  - `target_illumination`: fixed numeric target for that road segment.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `segments[].lamp_contributions` is an array of positional rows; each row contains 2 entries of numeric type.
