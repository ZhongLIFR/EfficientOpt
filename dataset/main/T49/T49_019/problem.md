Every industrial buyer must receive its full required hydrogen units, and demand may be split among the electrolyser parks listed in its `eligible_parks`. Each record in `electrolyser_parks` names the park `id`, its `region`, the `hydrogen_grades` it produces, its `production_capacity_units`, its `electricity_capacity_points`, and its `startup_cost`. Each record in `industrial_buyers` names the buyer `id`, its `required_grade`, its `region`, the `required_hydrogen_units` it needs, the `electricity_points_per_unit` each unit consumes, and the `eligible_parks` list of parks that may supply it. The `production_costs` array holds one record per allowed buyer-park pair with columns `industrial_buyer`, `electrolyser_park`, and `production_cost_per_unit`.

Eligibility already enforces hydrogen grade and delivery range. A park that is not started cannot supply hydrogen, and each started park has both a production capacity and an electricity-use capacity: the total units produced by it cannot exceed `production_capacity_units`, and the total electricity points, computed as `electricity_points_per_unit` times the produced units, cannot exceed `electricity_capacity_points`.

Minimize the total cost, which is the sum of `startup_cost` over all started parks plus, for every unit produced, the corresponding `production_cost_per_unit`. All data are explicitly supplied in `instance.json`.

Report the minimum total cost, the started parks, and all positive buyer-park supplies.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `electrolyser_parks`: array with 78 records.
  Record fields:
  1. `id` (string)
  2. `region` (integer)
  3. `hydrogen_grades` (array)
  4. `production_capacity_units` (integer)
  5. `electricity_capacity_points` (integer)
  6. `startup_cost` (integer)
- `industrial_buyers`: array with 208 records.
  Record fields:
  1. `id` (string)
  2. `required_grade` (string)
  3. `region` (integer)
  4. `required_hydrogen_units` (integer)
  5. `electricity_points_per_unit` (number)
  6. `eligible_parks` (array)
- `production_costs`: array with 4,633 records.
  Record fields:
  1. `industrial_buyer` (string)
  2. `electrolyser_park` (string)
  3. `production_cost_per_unit` (number)

Additional fixed fields retained for instance identity or provenance (not used by the optimization model):

- `kind`: fixed instance label string; auxiliary metadata not used in the optimization model.

- `problem_id`: fixed identifier string; auxiliary metadata not used in the optimization model.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `electrolyser_parks[].hydrogen_grades` is an array of strings; entries retain their listed order.
- `industrial_buyers[].eligible_parks` is an array of strings; entries retain their listed order.
