A distribution operator ships indivisible units from 2300 origins to 2700 destinations. `supplies[i]` is the exact number of units available at origin `i`, `demands[j]` is the exact number required at destination `j`, and `costs[i][j]` is the unit shipment cost from origin `i` to destination `j`.

Choose a nonnegative whole-number shipment for every origin-destination pair. Every origin must ship its full supply and every destination must receive its full demand. Minimize total shipment cost and report the minimum cost with a compact shipment summary.

All numerical data are fixed and explicitly stored at the top level of `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `supplies`: array with 2300 positive integer entries.
- `demands`: array with 2700 positive integer entries; its sum equals the sum of `supplies`.
- `costs`: array with 2300 rows and 2700 nonnegative integer entries per row.
- `indivisible_units`: boolean scalar equal to `true`.
