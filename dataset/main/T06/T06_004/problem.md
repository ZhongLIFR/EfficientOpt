An auto-parts plant plans the production of 120,000 optional part lots. For every part, the entry in `options` gives its `minimum` and `maximum` permitted production quantity, the consumption of three shared machine resources per unit in `resources`, the amounts of two output types produced per unit in `outputs`, and the contribution (`profit`) earned per unit. A part may be left out of the plan entirely, but any part that is produced must be made in a quantity at or above its setup-dependent `minimum` run and at most its `maximum`.

Each optional lot may be idle or operated at a quantity between its stated minimum and maximum. Shared resource capacities must be respected and the required output totals must be met.

Maximize total contribution using each lot's per-unit profit.

Report the maximum total contribution and the production quantity chosen for every part.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.options`: array[120000] of records with fields:
    - `minimum`: integer
    - `maximum`: integer
    - `resources`: array[3] of integer
    - `outputs`: array[2] of integer
    - `profit`: integer
  - `instance.resource_capacities`: array[3] of integer
  - `instance.requirements`: array[2] of integer
