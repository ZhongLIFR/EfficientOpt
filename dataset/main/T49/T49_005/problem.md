A platform must place the full compute demand of every service across eligible edge sites. Each record in `sites` names the site `id`, its `compute_capacity`, the `activation_cost` of activating it, and its `zone`. Each record in `services` names the service `id`, its `compute_demand`, its `home_zone`, and the `eligible_sites` list of sites that may process it. The `assignment_costs` array holds one record per allowed service-site pair with columns `service`, `site`, and `unit_cost`.

Demand is divisible among the sites listed in a service's `eligible_sites`, a list that already enforces site `zone` availability relative to the service `home_zone`. An inactive site cannot process any workload, and the total workload placed at an active site cannot exceed its `compute_capacity`.

Minimize the total cost, which is the sum of `activation_cost` over all active sites plus, for every unit of workload placed, the corresponding `unit_cost`. All data are explicitly supplied in `instance.json`.

Report the minimum total cost, the activated sites, and all positive workload allocations.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `sites`: array with 74 records.
  Record fields:
  1. `id` (string)
  2. `compute_capacity` (integer)
  3. `activation_cost` (integer)
  4. `zone` (integer)
- `services`: array with 230 records.
  Record fields:
  1. `id` (string)
  2. `compute_demand` (integer)
  3. `home_zone` (integer)
  4. `eligible_sites` (array)
- `assignment_costs`: array with 5,340 records.
  Record fields:
  1. `service` (string)
  2. `site` (string)
  3. `unit_cost` (number)

Additional fixed fields retained for instance identity or provenance (not used by the optimization model):

- `kind`: fixed instance label string; auxiliary metadata not used in the optimization model.

- `problem_id`: fixed identifier string; auxiliary metadata not used in the optimization model.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `services[].eligible_sites` is an array of strings; entries retain their listed order.
