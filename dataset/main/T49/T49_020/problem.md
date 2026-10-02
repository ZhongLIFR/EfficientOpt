Every evacuation zone must receive its full required provision units, and demand may be split among the shelters listed in its `eligible_shelters`. Each record in `shelters` names the shelter `id`, its `region`, the `supported_groups` it serves, its `provision_capacity_units`, its `medical_capacity_points`, and its `opening_cost`. Each record in `evacuation_zones` names the zone `id`, its `population_group`, its `region`, the `required_provision_units` it needs, the `medical_points_per_unit` each unit consumes, and the `eligible_shelters` list of shelters that may serve it. The `provision_costs` array holds one record per allowed zone-shelter pair with columns `evacuation_zone`, `shelter`, and `provision_cost_per_unit`.

Eligibility already enforces population-group support and travel range. A shelter that is not opened cannot serve a zone, and each open shelter has both a provision capacity and a medical-support capacity: the total units assigned to it cannot exceed `provision_capacity_units`, and the total medical points, computed as `medical_points_per_unit` times the assigned units, cannot exceed `medical_capacity_points`.

Minimize the total cost, which is the sum of `opening_cost` over all open shelters plus, for every unit provided, the corresponding `provision_cost_per_unit`. All data are explicitly supplied in `instance.json`.

Report the minimum total cost, the open shelters, and all positive zone-shelter allocations.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `shelters`: array with 78 records.
  Record fields:
  1. `id` (string)
  2. `region` (integer)
  3. `supported_groups` (array)
  4. `provision_capacity_units` (integer)
  5. `medical_capacity_points` (integer)
  6. `opening_cost` (integer)
- `evacuation_zones`: array with 416 records.
  Record fields:
  1. `id` (string)
  2. `population_group` (string)
  3. `region` (integer)
  4. `required_provision_units` (integer)
  5. `medical_points_per_unit` (number)
  6. `eligible_shelters` (array)
- `provision_costs`: array with 9,382 records.
  Record fields:
  1. `evacuation_zone` (string)
  2. `shelter` (string)
  3. `provision_cost_per_unit` (number)

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `shelters[].supported_groups` is an array of strings; entries retain their listed order.
- `evacuation_zones[].eligible_shelters` is an array of strings; entries retain their listed order.
