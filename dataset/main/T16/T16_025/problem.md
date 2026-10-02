A relief-logistics agency is preparing its network for the coming season. It may lease any subset of
20 candidate warehouses listed in `warehouses`; leasing warehouse `j` costs `lease_cost` and gives a
daily storage throughput of `storage_capacity`. Nothing can be stored in a warehouse that is not leased.

The agency serves 60 districts listed in `districts`. Districts differ in how costly it is to leave
demand unmet, given by `shortage_penalty` per unit. Moving one unit from warehouse `j` to district `i`
costs `transport_cost[i][j]`.

Demand is uncertain. `demand_by_scenario` holds 650 equally likely demand scenarios: its entry
`[i][s]` is the demand of district `i` in scenario `s`. In every scenario the agency decides how much
to ship from each leased warehouse to each district, and how much demand to leave unmet; shipments out
of a warehouse cannot exceed its throughput in any scenario, and every district's demand must be either
shipped or recorded as unmet.

Choose which warehouses to lease and the shipping plan for every scenario so that the expected total
cost - leasing plus transportation plus shortage penalty - is as small as possible.

Report the minimum expected cost, the leased warehouses, and the shipping plan per scenario.

All numerical data are fixed and provided in the instance file.

## Data schema

The complete fixed instance is in the instance file; no values are generated or sampled during execution.

- `warehouses`: array with 20 records; fields `lease_cost` (integer), `storage_capacity` (integer).
- `districts`: array with 60 records; field `shortage_penalty` (integer).
- `transport_cost`: 60 x 20 matrix of integers; `transport_cost[i][j]` is the unit cost from
  warehouse `j` to district `i`.
- `demand_by_scenario`: 60 x 650 matrix of integers; `demand_by_scenario[i][s]` is district `i`'s
  demand in scenario `s`.
- `scenario_count`: integer, the number of equally likely scenarios.
