A grid operator must assign each of the `substation_count` substations in the fixed instance to exactly one of `center_count` regional centers. Each center can manage at most the number of substations given by its entry in `center_capacity`. Assigning substation `i` to center `j` has a fixed telemetry cost `fixed_assignment_cost` for that pair, offset by a reliability credit `coordination_benefit` that is independent of the center.

Substations listed in `data_exchange_pairs` exchange synchronized measurements at a fixed volume; the data cost between centers `j` and `k` is the `network_pair_cost` value for that ordered pair per unit, and zero within the same center.

Minimize the total cost, which combines the telemetry cost minus the reliability credit for every substation with the measurement-data cost over all listed pairs.

Report the minimum total cost and the center assigned to every substation.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.substation_count`: integer
  - `instance.center_count`: integer
  - `instance.center_capacity`: array[4] of integer
  - `instance.fixed_assignment_cost`: array[27] of array
  - `instance.coordination_benefit`: array[27] of integer
  - `instance.network_pair_cost`: array[4] of array
  - `instance.data_exchange_pairs`: array[126] of records with fields:
    - `i`: integer
    - `j`: integer
    - `volume`: integer

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `fixed_assignment_cost` is an array of positional rows; each row contains 4 entries of numeric type.
- `network_pair_cost` is an array of positional rows; each row contains 4 entries of numeric type.
