A shipping line moves containers inside each regional depot-port market listed in `blocks` in `instance.json`. Each block lists its own origins and destinations: `supplies` gives the available containers (an integer) at each of the 119 origins, `demands` gives the containers required (an integer) at each of the 119 destinations, and `costs` is a 119×119 matrix whose entry `costs[i][j]` is the per-container shipping cost between origin `i` and destination `j`.

Within every block, choose shipments only between the origins and destinations listed in that block, so that every origin ships out its full supply and every destination receives its full demand. The cost of a block is the sum over all origin-destination pairs of containers moved times the corresponding per-container cost, and the total cost is the sum of the block costs.

Choose the shipping plan of every block to minimize the total cost across all markets. All supplies, demands, and costs are explicitly listed in `instance.json`.

Report the minimum total cost and the complete shipping plan for every block.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `blocks`: array with 95 records.
  Record fields:
  1. `supplies` (array)
  2. `demands` (array)
  3. `costs` (array)

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `blocks[].costs` is an array of positional rows; each row contains 119 entries of numeric type.
- `blocks[].demands` is an array of integer values; entries retain their listed order.
- `blocks[].supplies` is an array of integer values; entries retain their listed order.
