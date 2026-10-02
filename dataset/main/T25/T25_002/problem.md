A regional warehouse must pack a fixed set of indivisible product crates onto identical standard pallets. Empty candidate pallets may remain unused. Every crate must be assigned to exactly one pallet, no crate may be split, and the sum of crate volumes on a pallet may not exceed its capacity.

Minimize the number of pallets that carry at least one crate. Report the minimum pallet count and a compact assignment summary.

## Data schema

- `item_count`: number of crates.
- `pallet_capacity`: capacity of each pallet.
- `candidate_pallet_count`: number of available candidate pallets.
- `item_volumes`: ordered array of positive integer crate volumes, with length `item_count`.

The complete fixed instance is stored explicitly in `instance.json`; no numerical values are generated or sampled at runtime.
