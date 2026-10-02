A service team starts at site 0, visits every other listed checkpoint exactly once, and returns to site 0. Select one continuous circuit containing all 36 sites; disconnected cycles and self-travel are forbidden. Minimize total travel cost and report the circuit cost and visit order. All authoritative numerical data are fixed and explicitly stored in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `site_term`: string describing the checkpoints.
- `vehicle_term`: string describing the service vehicle.
- `depot_index`: integer equal to 0.
- `coordinate_unit`: string describing the coordinate unit.
- `cost_unit`: string describing the travel-cost unit.
- `sites`: array of exactly 36 records. Each record has integer `site`, string `name`, and `coordinates`, an array of exactly two integers. Site indices are 0 through 35 and determine matrix order.
- `travel_cost`: array of exactly 36 rows, each containing exactly 36 nonnegative numeric entries. The matrix is symmetric. Diagonal entries represent forbidden self-travel and are not selected.
