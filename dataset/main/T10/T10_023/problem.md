An airport operator must assign each of the `flight_count` flights in the fixed instance to exactly one of `cluster_count` gate clusters. Each cluster can handle at most the number of flights given by its entry in `cluster_capacity`. Assigning flight `i` to cluster `j` has a fixed ground-handling cost `fixed_assignment_cost` for that pair, offset by an on-time credit `coordination_benefit` that is independent of the cluster.

Flights listed in `data_exchange_pairs` share crews at a fixed volume; the crew-transfer cost between clusters `j` and `k` is the `network_pair_cost` value for that ordered pair per unit, and zero within the same cluster.

Minimize the total cost, which combines the ground-handling cost minus the on-time credit for every flight with the crew-transfer cost over all listed pairs.

Report the minimum total cost and the cluster assigned to every flight.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.flight_count`: integer
  - `instance.cluster_count`: integer
  - `instance.cluster_capacity`: array[4] of integer
  - `instance.fixed_assignment_cost`: array[26] of array
  - `instance.coordination_benefit`: array[26] of integer
  - `instance.network_pair_cost`: array[4] of array
  - `instance.data_exchange_pairs`: array[126] of records with fields:
    - `i`: integer
    - `j`: integer
    - `volume`: integer

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `fixed_assignment_cost` is an array of positional rows; each row contains 4 entries of numeric type.
- `network_pair_cost` is an array of positional rows; each row contains 4 entries of numeric type.
