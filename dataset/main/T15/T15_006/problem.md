An economy is organized into 90 production-economy blocks listed in `blocks` in `instance.json`. Each block lists its own sources and destinations: `supplies` gives the available quantity (an integer) at each of the 122 sources, `demands` gives the required quantity (an integer) at each of the 122 destinations, and `costs` is a 122×122 matrix whose entry `costs[i][j]` is the per-unit allocation cost between source `i` and destination `j`.

Within every block, choose shipments only between the sources and destinations listed in that block, so that every source ships out its full supply and every destination receives its full demand. The cost of a block is the sum over all source-destination pairs of shipped quantity times the corresponding per-unit cost, and the total cost is the sum of the block costs.

Choose the shipment plan of every block to minimize the total cost across all blocks. All supplies, demands, and costs are explicitly listed in `instance.json`.

Report the minimum total cost and the complete shipment plan for every block.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `blocks`: array with 90 records.
  Record fields:
  1. `supplies` (array)
  2. `demands` (array)
  3. `costs` (array)

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `blocks[].costs` is an array of positional rows; each row contains 122 entries of numeric type.
- `blocks[].demands` is an array of integer values; entries retain their listed order.
- `blocks[].supplies` is an array of integer values; entries retain their listed order.
