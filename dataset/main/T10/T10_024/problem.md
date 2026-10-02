A company is relocating its 48 departments, named in `departments`, to offices in the six cities listed in `cities`. Each department must be assigned to exactly one city, and `city_capacity` gives, for each city, the maximum number of departments it can host.

Assigning department `d` to city `c` incurs the fixed cost `fixed_assignment_cost[d][c]` (a 48-by-6 table, in monetary units) and, because the department leaves its current location, yields a relocation benefit `relocation_benefit[d]` that offsets part of that cost. Departments exchange information with each other: `communication_edges` lists the department pairs that communicate, together with the communication volume of each pair, and `city_pair_cost` gives the cost of communicating between any two cities (a 6-by-6 table, in monetary units). The communication cost of a listed pair is its volume times the pair cost of the two cities to which its departments are assigned.

Minimize the total cost, that is, the sum of the fixed assignment costs of all departments, minus the sum of all relocation benefits, plus the communication costs of all listed pairs. All data are fixed and explicitly provided in the instance file.

Report the minimum total cost and the city assigned to every department.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.departments`: array[48] of string
  - `instance.cities`: array[6] of string
  - `instance.fixed_assignment_cost`: array[48] of array
  - `instance.relocation_benefit`: array[48] of integer
  - `instance.city_pair_cost`: array[6] of array
  - `instance.communication_edges`: array[144] of records with fields:
    - `i`: integer
    - `j`: integer
    - `volume`: integer
  - `instance.city_capacity`: array[6] of integer

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `fixed_assignment_cost` is an array of positional rows; each row contains 6 entries of numeric type.
- `city_pair_cost` is an array of positional rows; each row contains 6 entries of numeric type.
