A national emergency service operates the regional depots listed in `depots`. Each depot is identified by its `name` and must pack every indivisible bundle in its `bundle_sizes` array into pallets registered to that same depot. Every pallet has capacity `pallet_capacity`, and the total size of the bundles assigned to a pallet may not exceed that capacity.

Assign each bundle to exactly one pallet at its listed depot. Minimize the total number of pallets used over all depots. Report the minimum total and one pallet assignment for every bundle.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `pallet_capacity`: positive integer.
- `depots`: array[20] of records.
- `depots[].name`: distinct string identifier.
- `depots[].bundle_sizes`: array[34] of positive integers.
