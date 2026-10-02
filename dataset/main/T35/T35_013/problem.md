A workshop has two robotic arms. The `arms` array stores both arms, each record giving the arm's `arm_id` and its `processing_time`, so the two records give arm 0 a processing time of 15 minutes and arm 1 a processing time of 20 minutes. Each arm follows one directed route from `SOURCE` to `SINK` through the processing slots listed in `processing_slots`, visiting at most one slot at a time, and each of the 100 slots may be visited by at most one arm. Every slot record names its `slot_id`, the `part_id` it belongs to, and its `pass_index` (the pass order among that part's slots). Both arms may also take the direct `SOURCE`-to-`SINK` arc.

Each of the 45 parts in `parts` has a `demand` (its required total processing time and also its profit), a `recovery_time`, and an availability window bounded by `start_time` and `end_time`; each record gives the part's `id` followed by these four values. A part earns its profit only when the total processing time over all of its visited slots reaches its `demand`, and the completion time of every visited slot must keep the full processing operation inside that part's availability window.

The `allowed_route_arcs` array lists all 10,028 permitted directed arcs, each with an `arc_id`, a `from_slot`, a `to_slot`, and a `setup_time`. If an arm visits slot `v` immediately after slot `u`, the completion time of `v` must be at least the completion time of `u` plus the arc's `setup_time` plus that arm's `processing_time`. When a part uses several pass slots, a later pass may be visited only after the earlier pass, its start must be no earlier than the previous pass completion and no more than 5 minutes later, and after the arm's last slot for the part the `recovery_time` must finish by time 512. The `mutex` array lists 77 mutually exclusive part pairs, each record giving the two part identifiers `id1` and `id2`; the two parts of each pair cannot both earn profit.

Maximize the total profit earned by the accepted parts. All data are embedded explicitly in `instance.json`.

Report the maximum total profit, the accepted parts, and the route each arm follows.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `allowed_route_arcs`: array with 10,028 records.
  Record fields:
  1. `arc_id` (string)
  2. `from_slot` (string)
  3. `to_slot` (string)
  4. `setup_time` (integer)
- `arms`: array with 2 records.
  Record fields:
  1. `arm_id` (integer)
  2. `processing_time` (integer)
- `mutex`: array with 77 records.
  Record fields:
  1. `id1` (integer)
  2. `id2` (integer)
- `parts`: array with 45 records.
  Record fields:
  1. `id` (integer)
  2. `demand` (integer)
  3. `recovery_time` (integer)
  4. `start_time` (integer)
  5. `end_time` (integer)
- `processing_slots`: array with 100 records.
  Record fields:
  1. `slot_id` (string)
  2. `part_id` (integer)
  3. `pass_index` (integer)
