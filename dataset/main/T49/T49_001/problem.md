
An electric-vehicle operator must decide which candidate charging stations to build and assign every demand zone to exactly one built station. Zone `i` contributes `zone_demand[i]` units. Station `j` has capacity `station_capacity[j]` and opening cost `station_open_cost[j]`. `eligibility[i]` lists the stations allowed to serve zone `i`; `assignment_cost[i][j]` gives the assignment cost for an allowed pair and is `null` for a disallowed pair.

Every zone must be assigned exactly once to an eligible built station. For each station, the total assigned zone demand cannot exceed its capacity. Minimize station-opening cost plus assignment cost. Report the minimum cost, built stations, and each zone's assigned station.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated at runtime.

## Data schema

- `zone_count`: integer scalar equal to 39,600.
- `station_count`: integer scalar equal to 100.
- `zone_demand`: array with 39,600 integer entries.
- `station_capacity`: array with 100 integer entries.
- `station_open_cost`: array with 100 integer entries.
- `eligibility`: array with 39,600 variable-length arrays of integer station indices.
- `assignment_cost`: array with 39,600 rows and 100 entries per row; entries are integer or `null`.

The order of every positional array is the order stored in the fixed JSON file.
