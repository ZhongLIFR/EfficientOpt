A farm manager must choose activity levels for each independent planning group. The land-and-labor use of the chosen plan must remain feasible under the budgeted yield and labor deviations, even when a limited number of the listed coefficients simultaneously reach their full adverse deviation; only the combinations explicitly listed as extreme scenarios need to be safeguarded. The goal is to maximize the total payoff.

All data are fixed in `instance.json`. The top-level `groups` field is an array of 14,080 independent planning groups. For every group, `profit` lists the per-unit payoff of each of the 28 farm activities, `nominal` their nominal per-unit land-and-labor requirement, `deviation` the maximum adverse per-unit increase of that requirement, and `upper_bounds` the maximum level permitted for each activity. `gamma` is the number of coefficients that may deviate at once, `capacity` is the available land-and-labor capacity, and `scenarios` enumerates the extreme cases, each entry being a pair of coefficient indices that may both reach their full deviation.

Choose a real-valued level for every activity, between zero and its upper bound, so that for every extreme scenario the total requirement stays within capacity, and maximize the total payoff over all groups.

Report the maximum total payoff.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `groups`: array with 14080 records.
  Record fields:
  1. `profit` (array)
  2. `nominal` (array)
  3. `deviation` (array)
  4. `upper_bounds` (array)
  5. `gamma` (integer)
  6. `capacity` (number)
  7. `scenarios` (array)

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `groups[].deviation` is an array of numeric values; entries retain their listed order.
- `groups[].nominal` is an array of integer values; entries retain their listed order.
- `groups[].profit` is an array of integer values; entries retain their listed order.
- `groups[].scenarios` is an array of positional rows; each row contains 2 entries of numeric type.
- `groups[].upper_bounds` is an array of integer values; entries retain their listed order.
