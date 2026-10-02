A distribution network has 60 sources and 60 sinks over 8 periods. For every source-destination lane and period, choose a nonnegative shipment and binary `use` and `open` decisions. Source shipments cannot exceed the listed per-period supply; every destination demand must be met exactly; shipment is bounded by lane capacity when used; and no more than `max_open_per_period` lanes may be used in a block and period.

If a lane is used in period `t`, it must be open in period `t` and every earlier period. Opening costs are charged separately for each lane and period. Minimize variable shipment costs plus all period-specific opening costs. Report the minimum cost and a compact shipment/lane-status summary.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated at runtime.

## Data schema

- `sources`: integer scalar equal to 60.
- `sinks`: integer scalar equal to 60.
- `periods`: integer scalar equal to 8.
- `supply`: array with 60 numeric entries; it is the per-period upper bound for each source.
- `demand`: array shaped `[sinks][periods]`.
- `cost`, `fixed`, and `capacity`: arrays shaped `[sources][sinks]`.
- `tight`: auxiliary numeric construction descriptor.
- `max_open_per_period`: integer scalar.
- `problem_id` and `_difficulty_seed`: auxiliary identifier/provenance scalars.
