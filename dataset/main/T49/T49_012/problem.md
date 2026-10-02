Every critical load group must have its full required power restored, and a load group may be split among the feeders listed in its `eligible_feeders`. Each record in `feeders` names the feeder `id`, its `sector`, the `voltage_classes` it serves, its `power_capacity_kw`, its `switching_capacity_points`, and its `energization_cost`. Each record in `load_groups` names the group `id`, its `voltage_class`, its `sector`, the `required_power_kw` that must be restored, the `switching_points_per_kw` each kilowatt consumes, and the `eligible_feeders` list of feeders that may serve it. The `restoration_costs` array holds one record per allowed load-group-feeder pair with columns `load_group`, `feeder`, and `restoration_cost_per_kw`.

Eligibility already enforces voltage compatibility and switching reach. A feeder that is not energized cannot serve load, and each energized feeder has both a power capacity and a switching-operation capacity: the total kilowatts restored by it cannot exceed `power_capacity_kw`, and the total switching points, computed as `switching_points_per_kw` times the restored kilowatts, cannot exceed `switching_capacity_points`.

Minimize the total cost, which is the sum of `energization_cost` over all energized feeders plus, for every kilowatt restored, the corresponding `restoration_cost_per_kw`. All data are explicitly supplied in `instance.json`.

Report the minimum total cost, the energized feeders, and all positive load-feeder allocations.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `feeders`: array with 77 records.
  Record fields:
  1. `id` (string)
  2. `sector` (integer)
  3. `voltage_classes` (array)
  4. `power_capacity_kw` (integer)
  5. `switching_capacity_points` (integer)
  6. `energization_cost` (integer)
- `load_groups`: array with 414 records.
  Record fields:
  1. `id` (string)
  2. `voltage_class` (string)
  3. `sector` (integer)
  4. `required_power_kw` (integer)
  5. `switching_points_per_kw` (number)
  6. `eligible_feeders` (array)
- `restoration_costs`: array with 9,282 records.
  Record fields:
  1. `load_group` (string)
  2. `feeder` (string)
  3. `restoration_cost_per_kw` (number)

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `feeders[].voltage_classes` is an array of strings; entries retain their listed order.
- `load_groups[].eligible_feeders` is an array of strings; entries retain their listed order.
