A city maintenance office has several alternative repair packages for each district. At most one package can be opened in a district, and every district must receive at least one package. Each package has a fixed priority score and consumes several shared crew resources.

Choose the repair packages and maximize total priority score while respecting every district and resource requirement. The complete fixed package, district, and resource data are in `instance.json`.
## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.activities`: array[40000] of records with fields:
    - `district`: integer
    - `priority_score`: integer
    - `crew_load`: array[12] of number
  - `instance.groups`: array[800] of records with fields:
    - `district`: integer
    - `minimum_selected`: integer
  - `instance.resources`: array[12] of records with fields:
    - `resource`: integer
    - `capacity`: number
  - `instance.units`: object with fields:
    - `instance.units.decision`: string
    - `instance.units.resource`: string
