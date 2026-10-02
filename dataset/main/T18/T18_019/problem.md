A mobile clinic assigns every appointment request to one available service station. Each station can serve at most one request in this planning wave, and the published matrix gives the dispatch cost for every request-station pair. Minimize total dispatch cost.

The complete request count, station count, and cost matrix are fixed in `instance.json`.
## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.origin_count`: integer
  - `instance.destination_count`: integer
  - `instance.costs`: array[650] of array
  - `instance.cost_unit`: string

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `costs` is an array of positional rows; each row contains 650 entries of numeric type.
