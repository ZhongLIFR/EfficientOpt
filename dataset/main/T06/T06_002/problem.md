An auto-parts plant plans the production of 120,000 optional part lots. For every part, the entry in `options` gives its `minimum` and `maximum` permitted production quantity, the consumption of three shared machine resources per unit in `resources`, the amounts of two output types produced per unit in `outputs`, and the contribution (`profit`) earned per unit. A part may be left out of the plan entirely, but any part that is produced must be made in a quantity at or above its setup-dependent `minimum` run and at most its `maximum`.

Each optional lot may be idle or operated at a quantity between its stated minimum and maximum. Shared resource capacities must be respected and the required output totals must be met.

Maximize total contribution using each lot's per-unit profit.

Report the maximum total contribution and the production quantity chosen for every part.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `options`: array with 120,000 records.
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
