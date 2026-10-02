A delivery vehicle must start at depot 0, visit each of 64 distinct customers exactly once, and return to the depot. The `coordinates` array explicitly lists all 65 fixed locations, and `distance` gives the fixed travel cost between every ordered pair of locations.

Choose a single minimum-cost tour. Report its total cost and the complete ordered node sequence.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `customer_count`: integer scalar equal to 64.
- `coordinates`: array with 65 positional rows, each containing two numeric coordinates.
- `distance`: array with 65 rows and 65 numeric entries per row; diagonal entries are zero.
