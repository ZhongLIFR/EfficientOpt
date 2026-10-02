A conservation center assigns every artifact batch to one available work bench. A bench can receive at most one batch during the planning window, and every request-bench pair has a fixed handling cost. Minimize the total handling cost.

All fixed batch, bench, and cost data are in `instance.json`.
## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.origin_count`: integer
  - `instance.destination_count`: integer
  - `instance.costs`: array[800] of array
  - `instance.cost_unit`: string

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `costs` is an array of positional rows; each row contains 800 entries of numeric type.
