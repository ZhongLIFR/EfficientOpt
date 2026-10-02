An operator must send one service vehicle from its maintenance pier to visit every listed buoy service point and return to its maintenance pier.

Choose the directed travel legs. Every site, including the depot, must have exactly one selected outgoing leg and exactly one selected incoming leg. The selected legs must form one continuous circuit containing all 35 sites; disconnected cycles are not allowed. Every visit is mandatory and self-travel is forbidden.

Minimize the sum of the selected travel costs. All authoritative numerical data are fixed and explicitly stored in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `site_term`: string describing the site terminology used by this harbor buoy maintenance instance.
- `vehicle_term`: string describing the vehicle terminology.
- `depot_index`: integer index of the depot; it equals 0.
- `coordinate_unit`: string describing the coordinate unit.
- `cost_unit`: string describing the travel-cost unit.
- `sites`: array of exactly 35 records. Each record has integer `site`, display string `name`, and `coordinates`, an array of exactly two integers.
- `travel_cost`: array of exactly 35 rows, each containing exactly 35 nonnegative numeric entries in the same order as `sites`. Diagonal entries correspond to forbidden self-travel and are not selected.
