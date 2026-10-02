A relief coordinator must place every indivisible supply lot into a labeled pallet. Each pallet has the same capacity, and a pallet is counted only when it receives at least one lot. The goal is to use as few pallets as possible while keeping every lot intact.

The complete fixed instance is stored explicitly in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `items`: array of exactly 100 records. Each record contains integer `item` and positive integer `size`.
- `container_count`: positive integer number of available pallet labels; it equals 100 in this instance.
- `container_capacity`: positive integer capacity of every pallet.
- `size_unit`: string describing the unit used by `size` and `container_capacity`.
