A hospital group must assign each of the `department_count` clinical departments in the fixed instance to exactly one of `campus_count` campuses. Each campus can host at most the number of departments given by its entry in `campus_capacity`. Assigning department `i` to campus `j` has a fixed relocation cost `fixed_assignment_cost` for that pair, offset by a service credit `coordination_benefit` that is independent of the campus.

Departments listed in `data_exchange_pairs` must transfer patient records with a fixed volume; the transfer cost between campuses `j` and `k` is the `network_pair_cost` value for that ordered pair per unit, and zero within the same campus.

Minimize the total cost, which combines the relocation cost minus the service credit for every department with the record-transfer cost over all listed pairs.

Report the minimum total cost and the campus assigned to every department.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `department_count`: integer scalar.
- `campus_count`: integer scalar.
- `campus_capacity`: array with 4 records.
- `fixed_assignment_cost`: array with 26 records.
- `coordination_benefit`: array with 26 records.
- `network_pair_cost`: array with 4 records.
- `data_exchange_pairs`: array with 128 records.
  Record fields:
  1. `i` (integer)
  2. `j` (integer)
  3. `volume` (integer)

Additional fixed fields retained for instance identity or provenance (not used by the optimization model):

- `kind`: fixed instance label string; auxiliary metadata not used in the optimization model.

- `problem_id`: fixed identifier string; auxiliary metadata not used in the optimization model.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `campus_capacity` is an array of integer values; entries retain their listed order.
- `fixed_assignment_cost` is an array of positional rows; each row contains 4 entries of numeric type.
- `coordination_benefit` is an array of integer values; entries retain their listed order.
- `network_pair_cost` is an array of positional rows; each row contains 4 entries of numeric type.
