A treasury desk must move a fixed amount of funds through a network of exchange nodes. `instance.json` describes the network: each entry of `arcs` is one directed transfer link, identified by its `tail` and `head` nodes (given as zero-based indices) and by the `cost` of moving one unit of funds along that link, in monetary units per unit. `balance` gives one value per node, stating how many more units must leave the node than arrive at it — a positive value marks a source node that supplies funds, and a negative value marks a sink node that absorbs them.

Report the minimum total cost and the complete transfer plan — the amount sent along every link.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `arcs`: array with 120,000 records.
  Record fields:
  1. `tail` (integer)
  2. `head` (integer)
  3. `cost` (integer)
- `balance`: array with 8,000 records.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `balance` is an array of integer values; entries retain their listed order.
