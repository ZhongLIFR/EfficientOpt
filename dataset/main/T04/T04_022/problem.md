The fixed instance is a minimum-cost bipartite assignment network. The ordered entries of `categories` identify the candidate assignment edges. For each listed candidate edge, choose a nonnegative whole-number assignment value. In each record of `rows`, the arrays `lb`, `ub`, and `cost` are aligned positionally with `categories` and give the edge bounds and unit costs. Each entry of `rows[].groups` identifies, through `indices`, all candidate edges incident to one supply-side or demand-side node and gives the required relation (`sense`) and right-hand side (`rhs`). Satisfy every edge bound and every listed node requirement, and minimize the total assignment cost. Report the minimum total cost. All rows and coefficients are explicitly supplied in `instance.json`; do not generate additional data.

All numerical data are explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; values are explicit and are not generated at runtime. Field paths use `[]` for array records.

- `categories`: array of candidate-edge identifiers, in the common positional order used by all coefficient arrays.
- `business_units`: descriptive string.
- `constraint_semantics`: descriptive string.
- `rows`: array of coupled assignment-network records.
- `rows[].unit`: record identifier.
- `rows[].lb`: array of integer lower bounds aligned with `categories`.
- `rows[].ub`: array of integer upper bounds aligned with `categories`.
- `rows[].cost`: array of integer objective coefficients aligned with `categories`.
- `rows[].groups`: array of node-requirement records.
- `rows[].groups[].name`: node-requirement identifier.
- `rows[].groups[].indices`: array of zero-based candidate-edge positions incident to that node.
- `rows[].groups[].sense`: one of `<=`, `>=`, or `=`.
- `rows[].groups[].rhs`: integer right-hand side.
