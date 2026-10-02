An industrial testing team schedules optional test campaigns. A campaign may be approved or declined, and a planned number of tests is assigned. Only approved tests count as accepted results; accepted tests earn value while planned tests consume shared laboratory resources. Every service group has a minimum accepted-test requirement.

Choose approvals and planned test quantities to maximize net value. The fixed campaign, group, and resource data are in `instance.json`.
## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.records`: array[2500] of records with fields:
    - `group`: integer
    - `max_output`: integer
    - `activation_fee`: integer
    - `effort_cost`: integer
    - `yield_value`: integer
    - `effort_use`: array[6] of number
  - `instance.groups`: array[25] of records with fields:
    - `group`: integer
    - `minimum_accepted`: integer
  - `instance.resources`: array[6] of records with fields:
    - `resource`: integer
    - `capacity`: number
