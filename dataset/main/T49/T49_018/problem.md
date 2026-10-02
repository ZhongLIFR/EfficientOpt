Every demand sector must receive its full required water units, and demand may be split among the treatment modules listed in its `eligible_modules`. Each record in `treatment_modules` names the module `id`, its `region`, the `water_qualities` it can produce, its `treatment_capacity_units`, its `chemical_capacity_points`, and its `commissioning_cost`. Each record in `demand_sectors` names the sector `id`, its `required_quality`, its `region`, the `required_water_units` it needs, the `chemical_points_per_unit` each unit consumes, and the `eligible_modules` list of modules that may supply it. The `treatment_costs` array holds one record per allowed sector-module pair with columns `demand_sector`, `treatment_module`, and `treatment_cost_per_unit`.

Eligibility already enforces the required water quality and delivery range. A module that is not commissioned cannot supply water, and each commissioned module has both a treatment-volume capacity and a chemical-use capacity: the total units supplied by it cannot exceed `treatment_capacity_units`, and the total chemical points, computed as `chemical_points_per_unit` times the supplied units, cannot exceed `chemical_capacity_points`. Two modules in a listed `incompatible_module_pairs` pair require the same intake works, so at most one of them may be commissioned.

Minimize the total cost, which is the sum of `commissioning_cost` over all commissioned modules plus, for every unit supplied, the corresponding `treatment_cost_per_unit`. All data are explicitly supplied in `instance.json`.

Report the minimum total cost, the commissioned modules, and all positive sector-module allocations.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `incompatible_module_pairs`: array with 36 records.
- `treatment_modules`: array with 78 records.
  Record fields:
  1. `id` (string)
  2. `region` (integer)
  3. `water_qualities` (array)
  4. `treatment_capacity_units` (integer)
  5. `chemical_capacity_points` (integer)
  6. `commissioning_cost` (integer)
- `demand_sectors`: array with 416 records.
  Record fields:
  1. `id` (string)
  2. `required_quality` (string)
  3. `region` (integer)
  4. `required_water_units` (integer)
  5. `chemical_points_per_unit` (number)
  6. `eligible_modules` (array)
- `treatment_costs`: array with 9,418 records.
  Record fields:
  1. `demand_sector` (string)
  2. `treatment_module` (string)
  3. `treatment_cost_per_unit` (number)

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `incompatible_module_pairs` is an array of positional rows; each row contains 2 entries of string type.
- `treatment_modules[].water_qualities` is an array of strings; entries retain their listed order.
- `demand_sectors[].eligible_modules` is an array of strings; entries retain their listed order.
