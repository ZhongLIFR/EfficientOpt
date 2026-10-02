A health authority chooses which indivisible equipment-upgrade projects to fund from the `projects` array and assigns every selected project to one of the three `funding_cycles`; a project may be implemented in at most one cycle. Each project record lists a project id, its `region`, the `funding_required`, and the `public_health_value` it delivers, and the `schema` entry documents this column layout for the `projects` and `review_standards` arrays. Each cycle record lists the cycle id, the total capital available, a value multiplier, and a map of per-region capital caps. Explicitly listed pairs in `incompatible_project_pairs` cannot be implemented in the same cycle.

Each review standard in `review_standards` gives a standard id, a `risk_limit`, and the covered pairs, each pair listing a `project_id` with its `risk_coefficient`. A standard counts as satisfied in a cycle when the sum of the covered `risk_coefficient` values over the projects implemented in that cycle does not exceed its `risk_limit`; a standard not counted as satisfied imposes no restriction. At least `minimum_standards_satisfied` standards must be counted as satisfied in every cycle.

Maximize the total cycle-adjusted public-health value, the sum over all selected projects of `public_health_value` times the value multiplier of the cycle in which they are implemented. All data are fixed explicitly in the instance file.

Report the optimal objective, every implemented project with its cycle, and the standards counted as satisfied in each cycle.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.funding_cycles`: array[3] of array
  - `instance.schema`: object with fields:
    - `instance.schema.projects`: string
    - `instance.schema.review_standards`: string
  - `instance.projects`: array[64] of array
  - `instance.review_standards`: array[40] of array
  - `instance.incompatible_project_pairs`: array[102] of array
  - `instance.minimum_standards_satisfied`: integer

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `funding_cycles` is an array of positional rows; each row contains 4 entries of integer, number, object, string type.
- `projects` is an array of positional rows; each row contains 4 entries of integer, string type.
- `review_standards` is an array of positional rows; each row contains 3 entries of array, integer, string type.
- `incompatible_project_pairs` is an array of positional rows; each row contains 2 entries of string type.
