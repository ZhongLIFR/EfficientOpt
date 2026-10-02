A production platform can enable an optional processing option and choose a base batch quantity. Only the portion of the batch produced while the option is enabled is saleable. Saleable units earn value, base units consume shared resources, and each service group has a minimum saleable amount.

Choose the enabled options and batch quantities to maximize net value. All fixed option, group, and resource data are in `instance.json`.
## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.records`: array[3000] of records with fields:
    - `group`: integer
    - `max_units`: integer
    - `fixed_cost`: integer
    - `unit_cost`: integer
    - `unit_value`: integer
    - `resource_use`: array[7] of number
  - `instance.groups`: array[30] of records with fields:
    - `group`: integer
    - `minimum_sale`: integer
  - `instance.resources`: array[7] of records with fields:
    - `resource`: integer
    - `capacity`: number
