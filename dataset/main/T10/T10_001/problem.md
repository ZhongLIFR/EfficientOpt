A cloud operator must assign each of the `workload_count` data-processing workloads in the fixed instance to exactly one of `datacenter_count` regional data centers. Each data center can host at most the number of workloads given by its entry in `datacenter_capacity`.

When two workloads exchange data, the network cost depends on which two data centers host them: exchanging between centers `c` and `k` costs the `network_pair_cost` value for that ordered pair per unit of exchange volume, and `data_exchange_pairs` lists every workload pair that exchanges data together with its fixed exchange volume. The cost table is directional, and exchanging within the same center costs zero.

Each workload `i` has a base hosting cost `fixed_assignment_cost` for every center and a coordination credit `coordination_benefit` that offsets part of the hosting cost regardless of the chosen center.

Minimize the total cost: hosting cost minus coordination credit for every workload, plus the data-exchange network cost summed over all listed pairs.

Report the minimum total cost, the center assigned to every workload, and the number of workloads hosted by each center.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `workload_count`: integer scalar.
- `datacenter_count`: integer scalar.
- `datacenter_capacity`: array with 4 records.
- `fixed_assignment_cost`: array with 24 records.
- `coordination_benefit`: array with 24 records.
- `network_pair_cost`: array with 4 records.
- `data_exchange_pairs`: array with 90 records.
  Record fields:
  1. `i` (integer)
  2. `j` (integer)
  3. `volume` (integer)

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `datacenter_capacity` is an array of integer values; entries retain their listed order.
- `fixed_assignment_cost` is an array of positional rows; each row contains 4 entries of numeric type.
- `coordination_benefit` is an array of integer values; entries retain their listed order.
- `network_pair_cost` is an array of positional rows; each row contains 4 entries of numeric type.
