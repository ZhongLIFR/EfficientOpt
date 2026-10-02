A hospital group must assign each of the `department_count` clinical departments in the fixed instance to exactly one of `campus_count` campuses. Each campus can host at most the number of departments given by its entry in `campus_capacity`. Assigning department `i` to campus `j` has a fixed relocation cost `fixed_assignment_cost` for that pair, offset by a service credit `coordination_benefit` that is independent of the campus.

Departments listed in `data_exchange_pairs` must transfer patient records with a fixed volume; the transfer cost between campuses `j` and `k` is the `network_pair_cost` value for that ordered pair per unit, and zero within the same campus.

Minimize the total cost, which combines the relocation cost minus the service credit for every department with the record-transfer cost over all listed pairs.

Report the minimum total cost and the campus assigned to every department.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.department_count`: integer
  - `instance.campus_count`: integer
  - `instance.campus_capacity`: array[4] of integer
  - `instance.fixed_assignment_cost`: array[26] of array
  - `instance.coordination_benefit`: array[26] of integer
  - `instance.network_pair_cost`: array[4] of array
  - `instance.data_exchange_pairs`: array[128] of records with fields:
    - `i`: integer
    - `j`: integer
    - `volume`: integer

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `fixed_assignment_cost` is an array of positional rows; each row contains 4 entries of numeric type.
- `network_pair_cost` is an array of positional rows; each row contains 4 entries of numeric type.
