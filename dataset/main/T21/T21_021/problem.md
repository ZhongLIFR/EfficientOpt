A routing operation must visit 90 fixed cities. `coordinates[i]` gives the two-dimensional location of city `i`. Travel is directed and asymmetric: `cost[i][j]` is the fixed cost of travelling from city `i` to city `j` and may differ from `cost[j][i]`.

Choose one closed tour that starts at city 0, visits every city exactly once, and returns to city 0. Minimize the total travel cost. Report the minimum cost and the complete tour.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `node_count`: integer scalar equal to 90.
- `coordinates`: array of exactly 90 rows; every row contains exactly two numeric coordinates.
- `cost`: array of exactly 90 rows; every row contains exactly 90 nonnegative numeric entries. Diagonal entries represent forbidden self-travel and are not decision arcs.
