A grid operator dispatches power within the 105 utility areas listed in `blocks`. Each area contains 230 generators and 230 load points. For every area, `supplies[i]` is the exact integer generation available at generator i, `demands[j]` is the exact integer requirement at load point j, and `costs[i][j]` is the per-unit dispatch cost for that generator-load pair. Supply and demand are balanced inside every area.

Within each area, choose a nonnegative whole-number dispatch only between the generators and load points listed in that area, so that every generator sends its full supply and every load point receives its full demand. Minimize the sum of dispatch costs across all areas and report the minimum total cost together with the complete dispatch plan.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `blocks`: array with 105 distinct area records.
  - `supplies`: array with 230 integer records.
  - `demands`: array with 230 integer records.
  - `costs`: two-dimensional array with 230 rows and 230 columns.
