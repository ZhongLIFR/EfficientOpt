A distribution planner sends nonnegative whole units of recovered battery modules from collection hubs to refurbishment centers. Each of the 600 collection hubs has the exact supply listed in `supply`, and each of the 620 refurbishment centers must receive the exact requirement listed in `demand`. `costs[i][j]` is the unit shipment cost from origin `i` to destination `j`.

Choose shipment quantities that satisfy every supply and demand equality and minimize total shipment cost. Report the minimum cost and a compact shipment summary.

All numerical data are fixed and explicitly stored at the top level of `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `origin_count`: integer scalar equal to 600.
- `destination_count`: integer scalar equal to 620.
- `supply`: array with 600 nonnegative integer entries.
- `demand`: array with 620 nonnegative integer entries; its sum equals the sum of `supply`.
- `costs`: array with 600 rows and 620 numeric entries per row.
- `quantity_unit`: descriptive string; it is not a coefficient or constraint.
