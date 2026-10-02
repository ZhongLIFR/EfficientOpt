
A planner must construct one closed directed tour through all 105 locations. The tour starts at location 0, visits every other location exactly once, and returns to location 0. `cost[i][j]` is the cost of traveling directly from location `i` to location `j`; each pair in `forbidden_arcs` is a directed arc that cannot be used.

Minimize the total cost of the selected arcs. Report the minimum total cost and the complete cyclic visiting order.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated at runtime.

## Data schema

- `node_count`: integer scalar equal to 105.
- `cost`: array with 105 rows and 105 numeric entries per row.
- `forbidden_arcs`: array with 576 rows and two integer node indices per row.
