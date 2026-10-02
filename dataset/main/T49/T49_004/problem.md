
A public-health agency must decide which candidate cold-chain hubs to open and assign every clinic to exactly one opened hub. Clinic `i` requires `clinic_demand[i]` units. Hub `j` has capacity `hub_capacity[j]` and opening cost `hub_open_cost[j]`. `eligibility[i]` lists the hubs allowed to serve clinic `i`; `assignment_cost[i][j]` gives the assignment cost for an allowed pair and is `null` for a disallowed pair.

Every clinic must be assigned exactly once to an eligible open hub. For each hub, the total assigned clinic demand cannot exceed its capacity. Minimize hub-opening cost plus assignment cost. Report the minimum cost, opened hubs, and each clinic's assigned hub.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated at runtime.

## Data schema

- `clinic_count`: integer scalar equal to 1,600.
- `hub_count`: integer scalar equal to 90.
- `clinic_demand`: array with 1,600 integer entries.
- `hub_capacity`: array with 90 integer entries.
- `hub_open_cost`: array with 90 integer entries.
- `eligibility`: array with 1,600 variable-length arrays of integer hub indices.
- `assignment_cost`: array with 1,600 rows and 90 entries per row; entries are integer or `null`.

The order of every positional array is the order stored in the fixed JSON file.
