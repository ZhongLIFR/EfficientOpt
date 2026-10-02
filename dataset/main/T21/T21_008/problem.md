A routing operator must dispatch two vehicles from the central depot for every independent location group. The two vehicles together must visit each of the ten non-depot locations exactly once, with five locations assigned to each vehicle, and every vehicle returns to the depot at the end of its tour. The goal is to minimize total travel cost.

All data are fixed in `instance.json`. The top-level `blocks` field is an array of 2,560 independent location groups. For each group, `cost` is the 11 by 11 travel-cost matrix between all locations: location 0 is the depot and locations 1 through 10 are the locations to be visited. Entry `cost[i][j]` is the travel cost from location `i` to location `j`.

For every group, construct two depot-to-depot tours. Each tour must visit exactly five distinct non-depot locations, and together the two tours must visit every non-depot location exactly once. Minimize the total travel cost over all groups.

Report the minimum total travel cost.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `blocks`: array of objects with fields:
  - `cost`: square numeric travel-cost matrix.
