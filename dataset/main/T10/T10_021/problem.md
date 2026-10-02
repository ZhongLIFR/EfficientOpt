A cloud provider must assign each of the `instance_count` service instances in the fixed instance to exactly one of `zone_count` availability zones. Each zone can host at most the number of instances given by its entry in `zone_capacity`. Assigning instance `i` to zone `j` has a fixed tenancy cost `fixed_assignment_cost` for that pair, offset by a latency credit `coordination_benefit` that is independent of the zone.

Instances listed in `data_exchange_pairs` exchange traffic at a fixed volume; the peering cost between zones `j` and `k` is the `network_pair_cost` value for that ordered pair per unit, and zero within the same zone.

Minimize the total cost, which combines the tenancy cost minus the latency credit for every instance with the peering cost over all listed pairs.

Report the minimum total cost and the zone assigned to every instance.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.instance_count`: integer
  - `instance.zone_count`: integer
  - `instance.zone_capacity`: array[4] of integer
  - `instance.fixed_assignment_cost`: array[28] of array
  - `instance.coordination_benefit`: array[28] of integer
  - `instance.network_pair_cost`: array[4] of array
  - `instance.data_exchange_pairs`: array[135] of records with fields:
    - `i`: integer
    - `j`: integer
    - `volume`: integer

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `fixed_assignment_cost` is an array of positional rows; each row contains 4 entries of numeric type.
- `network_pair_cost` is an array of positional rows; each row contains 4 entries of numeric type.
