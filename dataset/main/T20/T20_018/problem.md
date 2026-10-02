The fixed instance is a manufacturing sequence problem with ordered tasks cut, machine, assemble, inspect. For every task, select exactly one allowed start period from its inclusive release/latest window. Consecutive starts must differ by at least the listed lag. Minimize the weighted sum of start times over all chains and report it. All instance rows are explicitly supplied in instance.json.

All numerical data are explicitly provided in `instance.json`; do not generate or infer additional rows while solving.

## Data schema
The complete fixed instance is in `instance.json`; values are explicit and are not generated at runtime.
Field paths use `[]` for array records.
- `business_context`: string.
- `tasks`: array.
- `chains`: array.
- Nested record fields:
  - `chains[].chain`: string.
  - `chains[].horizon`: integer.
  - `chains[].release`: array.
  - `chains[].latest`: array.
  - `chains[].lags`: array.
  - `chains[].weights`: array.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `tasks` is an array of strings; entries retain their listed order.
- `chains` is an array of records; each record has the nested fields listed below.
- `chains[].lags` is an array of integer values; entries retain their listed order.
- `chains[].latest` is an array of integer values; entries retain their listed order.
- `chains[].release` is an array of integer values; entries retain their listed order.
- `chains[].weights` is an array of integer values; entries retain their listed order.
