An energy system operator must choose the capacity to build for each generation technology before the operating conditions are known. The instance names the candidate `technologies` (a one-dimensional array with one entry per technology) and lists the `scenarios` (a one-dimensional array of explicit, equally likely operating scenarios). For each technology, `investment_cost` gives the cost of one unit of built capacity and `capacity_upper_bound` the largest amount of capacity that may be built.

In every scenario the load must be covered. `demand` is a one-dimensional array with one entry per scenario. For each scenario and technology, `availability` (a two-dimensional array with one row per scenario and one column per technology) gives the fraction of built capacity that can be used, and `operating_cost` (with the same shape) gives the cost of dispatching one unit from that technology in that scenario. Load left uncovered by dispatch is shortfall, charged at the scalar rate `shortage_penalty` per unit.

The total cost equals the investment cost of all built capacity plus the equally weighted average, over all scenarios, of the dispatch cost and the shortage penalty. Choose the capacity built for every technology and the amount dispatched from every technology in every scenario to minimize this total cost. All numerical data are fixed and explicitly provided in `instance.json`.

Report the minimum total cost and the capacity built for every technology.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `technologies`: array with 40 records.
- `scenarios`: array with 10,000 records.
- `investment_cost`: array with 40 records.
- `capacity_upper_bound`: array with 40 records.
- `availability`: array with 10,000 records.
- `operating_cost`: array with 10,000 records.
- `demand`: array with 10,000 records.
- `shortage_penalty`: number scalar.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `technologies` is an array of strings; entries retain their listed order.
- `scenarios` is an array of strings; entries retain their listed order.
- `investment_cost` is an array of integer values; entries retain their listed order.
- `capacity_upper_bound` is an array of integer values; entries retain their listed order.
- `availability` is an array of positional rows; each row contains 40 entries of numeric type.
- `operating_cost` is an array of positional rows; each row contains 40 entries of numeric type.
- `demand` is an array of numeric values; entries retain their listed order.
