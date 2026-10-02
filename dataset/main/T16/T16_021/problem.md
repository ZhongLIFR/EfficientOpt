A supply-network planner must decide, before any operating scenario is known, which of 52 candidate distribution centers to open. The instance lists 2850 explicit operating scenarios, all equally likely. Opening center `j` is a binary decision with fixed cost `hire_cost[j]`; `capacity[j]` is its nominal capacity.

In scenario `s`, `demand[s]` must be covered by divisible product flow or recorded as shortfall. `availability[s][j]` is the usable fraction of center `j`'s capacity, `service_cost[s][j]` is its unit service cost, and `shortage_penalty` is the unit cost of shortfall. A closed center cannot serve flow, and an open center may serve at most its scenario-dependent available capacity.

Minimize opening cost plus the equally weighted average, over all scenarios, of service cost and shortfall penalty. Report the minimum total cost and the complete list of centers opened.

All numerical data are fixed and explicitly provided in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `facility_count`: integer scalar equal to 52.
- `scenario_count`: integer scalar equal to 2850.
- `hire_cost`: array[52] of numbers.
- `capacity`: array[52] of numbers.
- `demand`: array[2850] of numbers.
- `availability`: array[2850] of array[52] of numbers.
- `service_cost`: array[2850] of array[52] of numbers.
- `shortage_penalty`: numeric scalar.
