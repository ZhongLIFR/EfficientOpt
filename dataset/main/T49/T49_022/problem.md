A logistics operator may open directed transportation corridors between 500 regional nodes. The `network_nodes` array lists every node as a record with its `node_id`. Each record in `network_arcs` names a candidate corridor by `id`, its `source` and `target` nodes, the `fixed_cost` of opening it, and the `var_cost` of moving one unit of any commodity along it. Every opened corridor has a shared capacity of 1,500 units across all commodities, and a corridor that is not opened cannot carry any flow.

The operator must fulfil 80 shipment contracts, each described by a record in `commodities` with the `commodity_id`, its `origin` node, its `destination` node, and the `demand` that must be delivered in full. Flow of a commodity may be split across multiple directed paths. For every commodity, the net outflow at its origin must equal its demand, the net inflow at its destination must equal that demand, and every other node must satisfy flow conservation; all flows are nonnegative, and the sum of all commodity flows on an opened corridor cannot exceed 1,500.

Minimize the total cost, which is the sum of `fixed_cost` over all opened corridors plus, for every corridor, `var_cost` times the total commodity flow it carries. All data are explicitly supplied in `instance.json`.

Report the minimum total cost, the set of opened corridors, and the flow of every commodity on every corridor.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `commodities`: array with 80 records.
  Record fields:
  1. `commodity_id` (integer)
  2. `origin` (integer)
  3. `destination` (integer)
  4. `demand` (integer)
- `network_arcs`: array with 2,986 records.
  Record fields:
  1. `id` (integer)
  2. `source` (integer)
  3. `target` (integer)
  4. `fixed_cost` (integer)
  5. `var_cost` (integer)
- `network_nodes`: array with 500 records.
  Record fields:
  1. `node_id` (integer)
