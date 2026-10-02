An organization plans the regional shipment records indexed by `blocks`. Every record uses `sources` sources, `sinks` destinations, and `periods` periods. Coefficients carrying a block index apply to that listed region.

For every region and period, choose nonnegative shipments and binary lane-use and lane-active decisions. Destination demand must be met exactly; total shipment from a source in a period may not exceed its listed supply; and a lane can carry goods only when used, up to its capacity. At most `max_open_per_period` lanes may be used in a region and period.

Every lane is available from the start of the planning horizon until a chosen permanent retirement point. After a lane becomes inactive it cannot return to service, and shipment on the lane in a period requires it to be active in that period. Minimize total variable shipment cost plus the fixed cost charged for each active lane and period. Report the minimum total cost and the complete shipment, use, and active-status plan.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

- `blocks`: integer scalar equal to 1.
- `sources`: integer scalar equal to 45.
- `sinks`: integer scalar equal to 45.
- `periods`: integer scalar equal to 10.
- `max_open_per_period`: positive integer scalar.
- `supply`: numeric array[1][45], indexed by block and source; the same source limit applies in every period.
- `demand`: numeric array[1][45][10], indexed by block, destination, and period.
- `cost`: numeric array[1][45][45], containing variable shipment costs.
- `fixed`: numeric array[1][45][45], containing positive per-period active-lane costs.
- `capacity`: numeric array[1][45][45], containing positive lane capacities.

Auxiliary identifier fields, when present, are not decision data.
