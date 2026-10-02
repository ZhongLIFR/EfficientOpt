A bakery cooperative plans capacity independently for 150 locations. Each location has 14 indivisible dough-tray items. Items from different locations cannot share an oven batch, and every oven batch has the same capacity.

Assign every item to exactly one oven batch at its own location without exceeding capacity. Minimize the total number of used oven batches and report the minimum total with a compact per-location summary.

## Data schema

- `container_capacity`: positive integer capacity of every oven batch.
- `regions`: array of 150 location records with zero-based integer `index`, display `code`, and an `items` array.
- Each item has zero-based integer `index`, display `code`, and positive integer `size`.

The complete fixed instance is stored explicitly in `instance.json`; no numerical values are generated or sampled at runtime.
