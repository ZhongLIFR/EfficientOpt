An environmental monitoring service schedules optional inspection shifts for remote sensor zones. A selected shift must receive between its published minimum and maximum duration; an unselected shift receives none. Longer shifts earn service value but consume shared analyst, battery, and communications resources. Every zone must meet a minimum inspection level.

Choose the shift duration for each listed inspection option and maximize total service value. All fixed options and resource profiles are in `instance.json`.
## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.activities`: array[80000] of records with fields:
    - `zone`: integer
    - `minimum_shift`: integer
    - `maximum_shift`: integer
    - `service_value`: integer
    - `resource_demand`: array[8] of number
  - `instance.groups`: array[38] of records with fields:
    - `zone`: integer
    - `minimum_service`: number
  - `instance.resources`: array[8] of records with fields:
    - `resource`: integer
    - `capacity`: number
  - `instance.units`: object with fields:
    - `instance.units.quantity`: string
    - `instance.units.resource`: string
