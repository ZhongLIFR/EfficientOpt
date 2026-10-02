An enterprise must relocate its departments across the cities it operates in. Every department named in `departments` must be assigned to exactly one of the cities listed in `cities`, and each city can accept at most the number of departments given by its entry in `city_capacity`. Assigning department `i` to city `c` carries a fixed relocation cost `fixed_assignment_cost` for that pair, and the department earns a relocation benefit `relocation_benefit` that offsets part of that cost regardless of the city chosen.

Departments must keep working together: `communication_edges` lists every pair of departments that communicate together with the fixed volume between them. When two communicating departments are placed in cities `c` and `k`, the communication cost is the `city_pair_cost` value for that ordered pair per unit of volume, and communicating within the same city costs zero.

Minimize the total cost, which is the sum over all departments of the fixed assignment cost minus the relocation benefit, plus the communication cost over every listed edge.

Report the minimum total cost and the city assigned to every department.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `departments`: array with 25 records.
- `cities`: array with 5 records.
- `fixed_assignment_cost`: array with 25 records.
- `relocation_benefit`: array with 25 records.
- `city_pair_cost`: array with 5 records.
- `communication_edges`: array with 109 records.
- `city_capacity`: array with 5 records.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `departments` is an array of strings; entries retain their listed order.
- `cities` is an array of strings; entries retain their listed order.
- `fixed_assignment_cost` is an array of positional rows; each row contains 5 entries of numeric type.
- `relocation_benefit` is an array of integer values; entries retain their listed order.
- `city_pair_cost` is an array of positional rows; each row contains 5 entries of numeric type.
- `communication_edges` is an array of positional rows; each row contains 3 entries of numeric type.
- `city_capacity` is an array of integer values; entries retain their listed order.
