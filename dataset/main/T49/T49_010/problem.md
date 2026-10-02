A research organization must decide which of 79 programmes to launch and assign staff hours for 650 distinct work packages. Each work package has a field, home campus, required staff hours, laboratory workload per hour, and an explicit set of eligible programmes. Each programme has supported fields, staff-hour capacity, laboratory capacity, and a fixed launch cost. `staffing_costs` gives the fixed hourly cost for every allowed work-package/programme pair.

Every work package's full staffing requirement must be assigned. A programme can receive work only if launched, and its staff-hour and laboratory capacities cannot be exceeded. Minimize total launch and staffing cost. Report the minimum cost, launched programmes, and positive assignments.

## Data schema

The complete fixed instance is in `instance.json`; no value is generated or sampled during model construction or solving.

- `programmes`: 79 records with `id`, `campus`, `fields`, `staff_hour_capacity`, `lab_point_capacity`, and `launch_cost`.
- `work_packages`: 650 records with `id`, `field`, `home_campus`, `required_staff_hours`, `lab_points_per_hour`, and `eligible_programmes`.
- `staffing_costs`: 15298 allowed-pair records with `work_package`, `programme`, and `cost_per_staff_hour`.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `programmes[].fields` is an array of strings; entries retain their listed order.
- `work_packages[].eligible_programmes` is an array of strings; entries retain their listed order.
