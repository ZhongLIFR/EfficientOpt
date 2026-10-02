A distribution planner sends nonnegative whole units of vaccine units from regional depots to clinics. Each of the 500 regional depots has the exact supply listed in `supply`, and each of the 520 clinics must receive the exact requirement listed in `demand`. `costs[i][j]` is the unit shipment cost from origin `i` to destination `j`.

Choose shipment quantities that satisfy every supply and demand equality and minimize total shipment cost. Report the minimum cost and a compact shipment summary.

All numerical data are fixed and explicitly stored at the top level of `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `origin_count`: integer scalar equal to 500.
- `destination_count`: integer scalar equal to 520.
- `supply`: array with 500 nonnegative integer entries.
- `demand`: array with 520 nonnegative integer entries; its sum equals the sum of `supply`.
- `costs`: array with 500 rows and 520 numeric entries per row.
- `quantity_unit`: descriptive string; it is not a coefficient or constraint.
