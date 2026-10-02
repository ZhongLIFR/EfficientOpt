A mobile health network schedules optional refrigerated service blocks across several depots. Each block can be unused, or it can receive a positive number of service-hours between its published minimum and maximum. Service-hours earn value, while refrigeration, vehicle, and staffing resources have shared limits. Every depot must receive its published minimum service level.

Choose the service-hours for the listed blocks and maximize total service value. The fixed data are in `instance.json`; all quantities are measured in service-hours and all resource entries use the units stated in that file.
## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.activities`: array[50000] of records with fields:
    - `group`: integer
    - `min_hours`: integer
    - `max_hours`: integer
    - `value_per_hour`: integer
    - `resource_use`: array[6] of number
  - `instance.groups`: array[30] of records with fields:
    - `group`: integer
    - `minimum_hours`: number
  - `instance.resources`: array[6] of records with fields:
    - `resource`: integer
    - `capacity`: number
  - `instance.units`: object with fields:
    - `instance.units.quantity`: string
    - `instance.units.resource`: string
