A bank must assign each of the `branch_count` branches in the fixed instance to exactly one of `center_count` regional processing centers. Each center can handle at most the number of branches given by its entry in `center_capacity`. Assigning branch `i` to center `j` has a fixed operating cost `fixed_assignment_cost` for that pair, offset by a deposit credit `coordination_benefit` that is independent of the center.

Branches listed in `data_exchange_pairs` settle transactions with each other at a fixed volume; the settlement cost between centers `j` and `k` is the `network_pair_cost` value for that ordered pair per unit, and zero within the same center.

Minimize the total cost, which combines the operating cost minus the deposit credit for every branch with the settlement cost over all listed pairs.

Report the minimum total cost and the center assigned to every branch.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.branch_count`: integer
  - `instance.center_count`: integer
  - `instance.center_capacity`: array[4] of integer
  - `instance.fixed_assignment_cost`: array[26] of array
  - `instance.coordination_benefit`: array[26] of integer
  - `instance.network_pair_cost`: array[4] of array
  - `instance.data_exchange_pairs`: array[122] of records with fields:
    - `i`: integer
    - `j`: integer
    - `volume`: integer

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `fixed_assignment_cost` is an array of positional rows; each row contains 4 entries of numeric type.
- `network_pair_cost` is an array of positional rows; each row contains 4 entries of numeric type.
