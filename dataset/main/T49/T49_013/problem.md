A construction programme must decide which equipment pools to mobilize and allocate the required machine-hours of 480 distinct construction sites. Every site must receive all required hours and may split them among the pools listed in `eligible_pools`. Every pool record gives its region, supported equipment types, machine-hour capacity, fuel-support capacity, and fixed mobilization cost. Every site record gives its required equipment type, region, required hours, and fuel points consumed per hour. The `operating_costs` records give the fixed hourly cost for every allowed site-pool pair.

A pool that is not mobilized cannot serve any site. For each mobilized pool, total assigned hours must not exceed `machine_hour_capacity`, and total assigned fuel points must not exceed `fuel_support_points`. Minimize total fixed mobilization cost plus total operating cost.

Report the minimum total cost, mobilized pools, and positive site-pool allocations.

## Data schema

The complete fixed instance is in `instance.json`; no value is generated or sampled while constructing or solving the optimization model.

- `equipment_pools`: array with 78 distinct records containing `id`, `region`, `equipment_types`, `machine_hour_capacity`, `fuel_support_points`, and `mobilization_cost`.
- `construction_sites`: array with 480 distinct records containing `id`, `required_equipment_type`, `region`, `required_machine_hours`, `fuel_points_per_hour`, and `eligible_pools`.
- `operating_costs`: array with 11083 fixed allowed-pair records containing `site`, `equipment_pool`, and `cost_per_machine_hour`.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `equipment_pools[].equipment_types` is an array of strings; entries retain their listed order.
- `construction_sites[].eligible_pools` is an array of strings; entries retain their listed order.
