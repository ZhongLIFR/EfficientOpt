A delivery service must plan one closed tour through the 100 cities named in `city_names`, starting and ending at `depot_city` and visiting every city exactly once. `coordinates` records every fixed city location, and `route_cost[i][j]` gives the fixed cost of traveling from city `i` to city `j`.

Minimize the total travel cost of the single closed tour. Report the minimum cost and complete visiting order.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

- `city_names`: array with 100 unique identifiers.
- `coordinates`: array with 100 fixed coordinate records.
- `route_cost`: complete 100 by 100 fixed numeric array.
- `depot_city`: integer scalar.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `coordinates` is an array of positional rows; each row contains 2 entries of numeric type.
- `route_cost` is an array of positional rows; each row contains 100 entries of numeric type.
