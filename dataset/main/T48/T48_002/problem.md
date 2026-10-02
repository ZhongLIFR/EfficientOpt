A delivery vehicle must start at depot 0, visit each of 79 distinct customers exactly once, and return to the depot. The `coordinates` array explicitly lists all 80 fixed locations, and `distance` gives the fixed travel cost between every ordered pair of locations.

Choose a single minimum-cost tour. Report its total cost and the complete ordered node sequence.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `customer_count`: integer scalar equal to 79.
- `coordinates`: array with 80 positional rows, each containing two numeric coordinates.
- `distance`: array with 80 rows and 80 numeric entries per row; diagonal entries are zero.
