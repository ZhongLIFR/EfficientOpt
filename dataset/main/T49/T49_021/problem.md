Every customer district must receive its full required heat units, and demand may be split among the heat plants listed in its `eligible_heat_plants`. Each record in `heat_plants` names the plant `id`, its `region`, the `heat_grades` it can supply, its `heat_capacity_units`, its `pumping_capacity_points`, and its `startup_cost`. Each record in `customer_districts` names the district `id`, its `required_heat_grade`, its `region`, the `required_heat_units` it needs, the `pumping_points_per_unit` each unit consumes, and the `eligible_heat_plants` list of plants that may supply it. The `supply_costs` array holds one record per allowed district-plant pair with columns `customer_district`, `heat_plant`, and `supply_cost_per_unit`.

Eligibility already enforces heat grade and network range. A plant that is not started cannot supply heat, and each started plant has both a heat-output capacity and a pumping capacity: the total units supplied by it cannot exceed `heat_capacity_units`, and the total pumping points, computed as `pumping_points_per_unit` times the supplied units, cannot exceed `pumping_capacity_points`.

Minimize the total cost, which is the sum of `startup_cost` over all started plants plus, for every unit supplied, the corresponding `supply_cost_per_unit`. All data are explicitly supplied in `instance.json`.

Report the minimum total cost, the started plants, and all positive district-plant heat supplies.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `heat_plants`: array with 78 records.
  Record fields:
  1. `id` (string)
  2. `region` (integer)
  3. `heat_grades` (array)
  4. `heat_capacity_units` (integer)
  5. `pumping_capacity_points` (integer)
  6. `startup_cost` (integer)
- `customer_districts`: array with 832 records.
  Record fields:
  1. `id` (string)
  2. `required_heat_grade` (string)
  3. `region` (integer)
  4. `required_heat_units` (integer)
  5. `pumping_points_per_unit` (number)
  6. `eligible_heat_plants` (array)
- `supply_costs`: array with 18,844 records.
  Record fields:
  1. `customer_district` (string)
  2. `heat_plant` (string)
  3. `supply_cost_per_unit` (number)

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `heat_plants[].heat_grades` is an array of strings; entries retain their listed order.
- `customer_districts[].eligible_heat_plants` is an array of strings; entries retain their listed order.
