For every operational block, choose a nonnegative whole-number quantity for each listed allocation choice. The quantities in a block must sum exactly to its listed `balance`. Every quantity must lie between its corresponding explicit `lower` and `upper` value. The cross-block quota records constrain the sum of one named-by-index allocation choice over the explicitly listed block indices. Minimize total allocation cost.

All numerical values and index lists are fixed and explicitly stored in `instance.json`; no values are generated at solve time.

## Data schema

- `variable_names`: array of unique allocation-choice names; positions define variable indices.
- `blocks`: array of operational block records.
- `blocks[].block`: unique string label.
- `blocks[].cost`: numeric array aligned with `variable_names`.
- `blocks[].balance`: integer required sum of all allocation quantities in the block.
- `blocks[].lower`: integer lower-bound array aligned with `variable_names`.
- `blocks[].upper`: integer upper-bound array aligned with `variable_names`.
- `coupling_constraints`: array of cross-block quota records.
- `coupling_constraints[].name`: unique string label.
- `coupling_constraints[].variable_index`: zero-based index into `variable_names`.
- `coupling_constraints[].block_indices`: array of zero-based block indices.
- `coupling_constraints[].sense`: string equal to `<=` or `>=`.
- `coupling_constraints[].rhs`: integer right-hand side.
