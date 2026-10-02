A marine energy team approves optional test campaigns and plans quantities for each campaign. Only approved tests count toward accepted output; accepted tests earn value while planned tests consume shared resources. Every service group has a minimum accepted-output requirement.

Choose approvals and planned quantities to maximize net value. The complete fixed campaign, group, and resource data are in `instance.json`.
## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.records`: array[5000] of records with fields:
    - `group`: integer
    - `max_output`: integer
    - `activation_fee`: integer
    - `effort_cost`: integer
    - `yield_value`: integer
    - `effort_use`: array[7] of number
  - `instance.groups`: array[35] of records with fields:
    - `group`: integer
    - `minimum_accepted`: integer
  - `instance.resources`: array[7] of records with fields:
    - `resource`: integer
    - `capacity`: number
