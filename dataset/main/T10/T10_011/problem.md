A company is relocating its 48 departments, named in `departments`, to offices in the 6 cities listed in `cities`. Each department must be assigned to exactly one city, and `city_capacity` gives, for each city, the maximum number of departments it can host.

Assigning department `d` to city `c` incurs `fixed_assignment_cost[d][c]`, while `relocation_benefit[d]` offsets part of that cost. `communication_edges` lists department pairs and their communication volumes. If two departments are assigned to cities `i` and `j`, their communication cost is the listed volume times `city_pair_cost[i][j]`.

Minimize fixed assignment cost minus relocation benefit plus communication cost. Report the minimum total cost and every department's assigned city.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

- `departments`: array with 48 records.
- `cities`: array with 6 records.
- `fixed_assignment_cost`: 48 by 6 numeric array.
- `relocation_benefit`: array with 48 records.
- `city_pair_cost`: 6 by 6 numeric array.
- `communication_edges`: array with 144 fixed records. Each record contains
  `i` (integer department index), `j` (integer department index), and
  `volume` (nonnegative numeric communication volume).
- `city_capacity`: array with 6 records.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `departments` is an array of strings; entries retain their listed order.
- `cities` is an array of strings; entries retain their listed order.
- `fixed_assignment_cost` is an array of positional rows; each row contains 6 entries of numeric type.
- `relocation_benefit` is an array of integer values; entries retain their listed order.
- `city_pair_cost` is an array of positional rows; each row contains 6 entries of numeric type.
- `city_capacity` is an array of integer values; entries retain their listed order.
