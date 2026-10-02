Every route programme must receive its full required flight-hours, and hours may be split among the fleet groups listed in its `eligible_fleet_groups`. Each record in `fleet_groups` names the group `id`, its `base`, the `route_types` it can operate, its `flight_hour_capacity`, its `maintenance_point_capacity`, and its `readiness_cost`. Each record in `route_programmes` names the programme `id`, its `route_type`, its `preferred_base`, the `required_flight_hours` it needs, the `maintenance_points_per_hour` each hour consumes, and the `eligible_fleet_groups` list of groups that may operate it. The `operating_costs` array holds one record per allowed route-fleet-group pair with columns `route`, `fleet_group`, and `operating_cost_per_hour`.

Eligibility already enforces route type and positioning range. A fleet group that is not made ready cannot operate routes, and each ready group has both a flight-hour capacity and a maintenance capacity: the total hours assigned to it cannot exceed `flight_hour_capacity`, and the total maintenance points, computed as `maintenance_points_per_hour` times the assigned hours, cannot exceed `maintenance_point_capacity`.

Minimize the total cost, which is the sum of `readiness_cost` over all ready fleet groups plus, for every flight-hour operated, the corresponding `operating_cost_per_hour`. All data are explicitly supplied in `instance.json`.

Report the minimum total cost, the ready fleet groups, and all positive route-fleet hour allocations.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `fleet_groups`: array with 79 records.
  Record fields:
  1. `id` (string)
  2. `base` (integer)
  3. `route_types` (array)
  4. `flight_hour_capacity` (integer)
  5. `maintenance_point_capacity` (integer)
  6. `readiness_cost` (integer)
- `route_programmes`: array with 836 records.
  Record fields:
  1. `id` (string)
  2. `route_type` (string)
  3. `preferred_base` (integer)
  4. `required_flight_hours` (integer)
  5. `maintenance_points_per_hour` (number)
  6. `eligible_fleet_groups` (array)
- `operating_costs`: array with 18,608 records.
  Record fields:
  1. `route` (string)
  2. `fleet_group` (string)
  3. `operating_cost_per_hour` (number)

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `fleet_groups[].route_types` is an array of strings; entries retain their listed order.
- `route_programmes[].eligible_fleet_groups` is an array of strings; entries retain their listed order.
