A satellite operator must assign each of the `task_count` observation tasks in the fixed instance to exactly one of `station_count` ground stations. Each station can handle at most the number of tasks given by its entry in `station_capacity`. Assigning task `i` to station `j` has a fixed support cost `fixed_assignment_cost` for that pair, offset by a weather credit `coordination_benefit` that applies regardless of the chosen station.

Tasks listed in `data_exchange_pairs` exchange calibration data with a fixed volume; the relay cost of exchanging between stations `j` and `k` is the `network_pair_cost` value for that ordered pair per unit, and zero within the same station.

Minimize the total cost, which combines the support cost minus the weather credit for every task with the relay cost over all listed pairs.

Report the minimum total cost and the station assigned to every task.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `task_count`: integer scalar.
- `station_count`: integer scalar.
- `station_capacity`: array with 4 records.
- `fixed_assignment_cost`: array with 25 records.
- `coordination_benefit`: array with 25 records.
- `network_pair_cost`: array with 4 records.
- `data_exchange_pairs`: array with 120 records.
  Record fields:
  1. `i` (integer)
  2. `j` (integer)
  3. `volume` (integer)

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `station_capacity` is an array of integer values; entries retain their listed order.
- `fixed_assignment_cost` is an array of positional rows; each row contains 4 entries of numeric type.
- `coordination_benefit` is an array of integer values; entries retain their listed order.
- `network_pair_cost` is an array of positional rows; each row contains 4 entries of numeric type.
