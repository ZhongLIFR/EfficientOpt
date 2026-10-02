A cloud operator must assign each of the `workload_count` data-processing workloads in the fixed instance to exactly one of `datacenter_count` regional data centers. Each data center can host at most the number of workloads given by its entry in `datacenter_capacity`.

When two workloads exchange data, the network cost depends on which two data centers host them: exchanging between centers `c` and `k` costs the `network_pair_cost` value for that ordered pair per unit of exchange volume, and `data_exchange_pairs` lists every workload pair that exchanges data together with its fixed exchange volume. The cost table is directional, and exchanging within the same center costs zero.

Each workload `i` has a base hosting cost `fixed_assignment_cost` for every center and a coordination credit `coordination_benefit` that offsets part of the hosting cost regardless of the chosen center.

Minimize the total cost: hosting cost minus coordination credit for every workload, plus the data-exchange network cost summed over all listed pairs.

Report the minimum total cost, the center assigned to every workload, and the number of workloads hosted by each center.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.workload_count`: integer
  - `instance.datacenter_count`: integer
  - `instance.datacenter_capacity`: array[4] of integer
  - `instance.fixed_assignment_cost`: array[24] of array
  - `instance.coordination_benefit`: array[24] of integer
  - `instance.network_pair_cost`: array[4] of array
  - `instance.data_exchange_pairs`: array[115] of records with fields:
    - `i`: integer
    - `j`: integer
    - `volume`: integer

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `fixed_assignment_cost` is an array of positional rows; each row contains 4 entries of numeric type.
- `network_pair_cost` is an array of positional rows; each row contains 4 entries of numeric type.
