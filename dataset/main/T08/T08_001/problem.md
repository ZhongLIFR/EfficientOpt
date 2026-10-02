A software platform decides which optional feature A and feature B to make available for each customer segment. Activating either feature consumes engineering capacity; activating both for the same segment creates an additional launch value. Regional launch limits and shared engineering capacities are published in `instance.json`.

Choose the feature decisions and maximize total launch value after all limits are respected.
## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.records`: array[1000] of records with fields:
    - `group`: integer
    - `joint_value`: integer
    - `cost_a`: integer
    - `cost_b`: integer
    - `load_a`: array[6] of number
    - `load_b`: array[6] of number
  - `instance.groups`: array[12] of records with fields:
    - `group`: integer
    - `max_a`: integer
    - `max_b`: integer
  - `instance.resources`: array[6] of records with fields:
    - `resource`: integer
    - `capacity`: number
