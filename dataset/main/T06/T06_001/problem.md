A mining company plans the production of 600,000 optional mining lots. For every lot, the entry in `options` gives its `minimum` and `maximum` permitted production level, the consumption of three shared resources per production unit in `resources`, the amounts of two ore-quality outputs produced per unit in `outputs`, and the `profit` earned per production unit. A lot may be left idle, but a lot that operates must produce within its `minimum`–`maximum` interval.

Each optional lot may be idle or operated at a quantity between its stated minimum and maximum. Shared resource capacities must be respected and the required output totals must be met.

Maximize total contribution using each lot's per-unit profit.

Report the maximum total value and the production level chosen for every lot.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `options`: array with 600,000 records.
  Record fields:
  1. `minimum` (integer)
  2. `maximum` (integer)
  3. `resources` (array)
  4. `outputs` (array)
  5. `profit` (integer)
- `resource_capacities`: array with 3 records.
- `requirements`: array with 2 records.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `options[].outputs` is an array of integer values; entries retain their listed order.
- `options[].resources` is an array of integer values; entries retain their listed order.
- `resource_capacities` is an array of integer values; entries retain their listed order.
- `requirements` is an array of integer values; entries retain their listed order.
