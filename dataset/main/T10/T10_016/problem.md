A research institute must assign each of the `team_count` research teams in the fixed instance to exactly one of `campus_count` campuses. Each campus can host at most the number of teams given by its entry in `campus_capacity`. Assigning team `i` to campus `c` has a fixed hosting cost `fixed_assignment_cost` for that pair, offset by a coordination credit `coordination_benefit` that is independent of the campus.

Teams listed in `data_exchange_pairs` exchange data with a fixed volume; the network cost of exchanging between campuses `c` and `k` is the `network_pair_cost` value for that ordered pair per unit of volume, and exchanging within the same campus costs zero.

Minimize the total cost: hosting cost minus coordination credit for every team, plus the data-exchange network cost over all listed pairs.

Report the minimum total cost and the campus assigned to every team.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.team_count`: integer
  - `instance.campus_count`: integer
  - `instance.campus_capacity`: array[4] of integer
  - `instance.fixed_assignment_cost`: array[26] of array
  - `instance.coordination_benefit`: array[26] of integer
  - `instance.network_pair_cost`: array[4] of array
  - `instance.data_exchange_pairs`: array[125] of records with fields:
    - `i`: integer
    - `j`: integer
    - `volume`: integer

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `fixed_assignment_cost` is an array of positional rows; each row contains 4 entries of numeric type.
- `network_pair_cost` is an array of positional rows; each row contains 4 entries of numeric type.
