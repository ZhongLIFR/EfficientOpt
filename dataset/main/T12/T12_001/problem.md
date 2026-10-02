During the harvest season, a fixed number of empty railcars must be repositioned through a network of transfer points. `instance.json` describes the network: each entry of `arcs` is one directed relocation link, identified by its `tail` and `head` transfer points (given as zero-based indices) and by the `cost` of moving one railcar along that link, in monetary units per railcar. `balance` gives one value per transfer point, stating how many more railcars must leave the point than arrive at it — a positive value means the point supplies that many railcars, and a negative value means it absorbs that many.

Report the minimum total cost and the complete transfer plan — the number of railcars sent along every link.

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
