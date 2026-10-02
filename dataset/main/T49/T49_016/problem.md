Every crop zone must assign its full required hectares to compatible technology packages, and area may be divided among the packages listed in its `eligible_technology_packages`. Each record in `technology_packages` names the package `id`, its `region`, the `supported_crops` it serves, its `area_capacity_hectares`, its `support_capacity_points`, and its `adoption_cost`. Each record in `crop_zones` names the zone `id`, its `crop`, its `region`, the `required_hectares` that must be covered, the `support_points_per_hectare` each hectare consumes, and the `eligible_technology_packages` list of packages that may serve it. The `operating_costs` array holds one record per allowed crop-zone-package pair with columns `crop_zone`, `technology_package`, and `operating_cost_per_hectare`.

Eligibility already enforces crop support and service range. A package that is not adopted cannot serve area, and each adopted package has both an acreage capacity and a technical-support capacity: the total hectares assigned to it cannot exceed `area_capacity_hectares`, and the total support points, computed as `support_points_per_hectare` times the assigned hectares, cannot exceed `support_capacity_points`.

Minimize the total cost, which is the sum of `adoption_cost` over all adopted packages plus, for every hectare covered, the corresponding `operating_cost_per_hectare`. All data are explicitly supplied in `instance.json`.

Report the minimum total cost, the adopted packages, and all positive crop-zone allocations.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `technology_packages`: array with 78 records.
  Record fields:
  1. `id` (string)
  2. `region` (integer)
  3. `supported_crops` (array)
  4. `area_capacity_hectares` (integer)
  5. `support_capacity_points` (integer)
  6. `adoption_cost` (integer)
- `crop_zones`: array with 416 records.
  Record fields:
  1. `id` (string)
  2. `crop` (string)
  3. `region` (integer)
  4. `required_hectares` (integer)
  5. `support_points_per_hectare` (number)
  6. `eligible_technology_packages` (array)
- `operating_costs`: array with 9,410 records.
  Record fields:
  1. `crop_zone` (string)
  2. `technology_package` (string)
  3. `operating_cost_per_hectare` (number)

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `technology_packages[].supported_crops` is an array of strings; entries retain their listed order.
- `crop_zones[].eligible_technology_packages` is an array of strings; entries retain their listed order.
