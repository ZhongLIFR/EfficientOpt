A delivery service must plan one closed tour through the 25 cities named in `city_names`, starting and ending at the depot and visiting every city exactly once. The two-dimensional table `coordinates` records the grid position of every city (one `x`-`y` pair per city), and the complete fixed table `route_cost` gives the cost of traveling directly between each pair of cities. The integer `depot_city` identifies the city where the tour must start and end.

Choose the visiting order of the cities so that the tour is a single closed route covering all 25 cities exactly once and returning to `depot_city`. All costs are fixed in the supplied matrix in the instance file.

Minimize the total travel cost, the sum of `route_cost` over every consecutive leg of the tour.

Report the minimum total travel cost and the complete visiting order of the tour.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.city_names`: array[100] of string
  - `instance.coordinates`: array[100] of array
  - `instance.route_cost`: array[100] of array
  - `instance.depot_city`: integer

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `coordinates` is an array of positional rows; each row contains 2 entries of numeric type.
- `route_cost` is an array of positional rows; each row contains 100 entries of numeric type.
