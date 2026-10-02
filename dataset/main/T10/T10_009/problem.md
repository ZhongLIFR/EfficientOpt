A grid operator must assign each of the `substation_count` substations in the fixed instance to exactly one of `center_count` regional centers. Each center can manage at most the number of substations given by its entry in `center_capacity`. Assigning substation `i` to center `j` has a fixed telemetry cost `fixed_assignment_cost` for that pair, offset by a reliability credit `coordination_benefit` that is independent of the center.

Substations listed in `data_exchange_pairs` exchange synchronized measurements at a fixed volume; the data cost between centers `j` and `k` is the `network_pair_cost` value for that ordered pair per unit, and zero within the same center.

Minimize the total cost, which combines the telemetry cost minus the reliability credit for every substation with the measurement-data cost over all listed pairs.

Report the minimum total cost and the center assigned to every substation.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `substation_count`: integer scalar.
- `center_count`: integer scalar.
- `center_capacity`: array with 4 records.
- `fixed_assignment_cost`: array with 27 records.
- `coordination_benefit`: array with 27 records.
- `network_pair_cost`: array with 4 records.
- `data_exchange_pairs`: array with 126 records.
  Record fields:
  1. `i` (integer)
  2. `j` (integer)
  3. `volume` (integer)

Additional fixed fields retained for instance identity or provenance (not used by the optimization model):

- `kind`: fixed instance label string; auxiliary metadata not used in the optimization model.

- `problem_id`: fixed identifier string; auxiliary metadata not used in the optimization model.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `center_capacity` is an array of integer values; entries retain their listed order.
- `fixed_assignment_cost` is an array of positional rows; each row contains 4 entries of numeric type.
- `coordination_benefit` is an array of integer values; entries retain their listed order.
- `network_pair_cost` is an array of positional rows; each row contains 4 entries of numeric type.
