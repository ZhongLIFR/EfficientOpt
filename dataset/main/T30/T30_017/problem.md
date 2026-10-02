Several service regions each operate one vehicle from their own depot at site 0. Within every region, the vehicle must visit every other listed checkpoint exactly once and return to site 0. Each region must form one continuous circuit; disconnected cycles and self-travel are forbidden. Minimize the sum of travel costs across all regions and report each region's circuit cost and visit order. All authoritative numerical data are fixed and explicitly stored in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `coordinate_unit`: string describing the coordinate unit.
- `cost_unit`: string describing the travel-cost unit.
- `regions`: array of exactly 2 records, whose site counts are [34, 35] in listed order.
- `regions[].region_id`: string label unique within the instance.
- `regions[].name`: display string.
- `regions[].depot_index`: integer equal to 0.
- `regions[].sites`: array of site records. Each record has integer `site`, string `name`, and `coordinates`, an array of exactly two integers. Indices are consecutive from 0 and determine matrix order.
- `regions[].travel_cost`: square array with one row and column per listed site; entries are nonnegative numeric travel costs. Each regional matrix is symmetric. Diagonal entries represent forbidden self-travel and are not selected.
