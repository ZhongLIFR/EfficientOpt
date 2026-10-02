A settlement house clears funds across 28 regions listed in `blocks` in `instance.json`. Each block lists its own participants: `supplies` gives the funds offered (an integer) by each of the 220 source members, `demands` gives the funds required (an integer) by each of the 220 destination members, and `costs` is a 220×220 matrix whose entry `costs[i][j]` is the per-unit clearing cost from source member `i` to destination member `j`.

Within every block, choose transfers only between the source and destination members listed in that block, so that every source member's full supply is cleared out and every destination member's full demand is received. The cost of a block is the sum over all listed source-destination pairs of cleared amount times the corresponding per-unit cost, and the total cost is the sum of the block costs.

Choose the clearing plan of every block to minimize the total cost across all regions. All supplies, demands, and costs are explicitly listed in `instance.json`.

Report the minimum total cost and the complete clearing plan for every block.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `blocks`: array with 28 records.
  Record fields:
  1. `supplies` (array)
  2. `demands` (array)
  3. `costs` (array)

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `blocks[].costs` is an array of positional rows; each row contains 220 entries of numeric type.
- `blocks[].demands` is an array of integer values; entries retain their listed order.
- `blocks[].supplies` is an array of integer values; entries retain their listed order.
