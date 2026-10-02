A grocery network fulfills orders across 30 order pools listed in `blocks` in `instance.json`. Each block lists its own fulfillment points and orders: `supplies` gives the available items (an integer) at each of the 210 fulfillment points, `demands` gives the items required (an integer) by each of the 210 orders, and `costs` is a 210×210 matrix whose entry `costs[i][j]` is the per-unit fulfillment cost between point `i` and order `j`.

Within every block, choose allocations only between the fulfillment points and orders listed in that block, so that every point ships out its full supply and every order receives its full demand. The cost of a block is the sum over all point-order pairs of allocated items times the corresponding per-unit cost, and the total cost is the sum of the block costs.

Choose the allocation plan of every block to minimize the total cost across all pools. All supplies, demands, and costs are explicitly listed in `instance.json`.

Report the minimum total cost and the complete allocation plan for every block.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `blocks`: array with 30 records.
  Record fields:
  1. `supplies` (array)
  2. `demands` (array)
  3. `costs` (array)

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `blocks[].costs` is an array of positional rows; each row contains 210 entries of numeric type.
- `blocks[].demands` is an array of integer values; entries retain their listed order.
- `blocks[].supplies` is an array of integer values; entries retain their listed order.
