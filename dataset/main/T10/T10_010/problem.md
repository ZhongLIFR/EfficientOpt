An airport operator must assign each of the `flight_count` flights in the fixed instance to exactly one of `cluster_count` gate clusters. Each cluster can handle at most the number of flights given by its entry in `cluster_capacity`. Assigning flight `i` to cluster `j` has a fixed ground-handling cost `fixed_assignment_cost` for that pair, offset by an on-time credit `coordination_benefit` that is independent of the cluster.

Flights listed in `data_exchange_pairs` share crews at a fixed volume; the crew-transfer cost between clusters `j` and `k` is the `network_pair_cost` value for that ordered pair per unit, and zero within the same cluster.

Minimize the total cost, which combines the ground-handling cost minus the on-time credit for every flight with the crew-transfer cost over all listed pairs.

Report the minimum total cost and the cluster assigned to every flight.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `flight_count`: integer scalar.
- `cluster_count`: integer scalar.
- `cluster_capacity`: array with 4 records.
- `fixed_assignment_cost`: array with 26 records.
- `coordination_benefit`: array with 26 records.
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
- `cluster_capacity` is an array of integer values; entries retain their listed order.
- `fixed_assignment_cost` is an array of positional rows; each row contains 4 entries of numeric type.
- `coordination_benefit` is an array of integer values; entries retain their listed order.
- `network_pair_cost` is an array of positional rows; each row contains 4 entries of numeric type.
