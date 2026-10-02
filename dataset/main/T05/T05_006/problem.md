A city chooses which indivisible district-heating retrofit projects to carry out from the `projects` array and assigns every selected project to one of the three `funding_cycles`; a project may be carried out in at most one cycle. Each project record lists a project id, its `district`, the `capital_required`, and the `annual_fuel_saving` it delivers, and the `schema` entry documents this column layout for the `projects` and `review_standards` arrays. Each cycle record lists the cycle id, the total capital available, a benefit multiplier, and a map of per-district capital caps. Listed pairs in `incompatible_project_pairs` cannot be carried out in the same cycle.

Each review standard in `review_standards` gives a standard id, an `impact_limit`, and the covered pairs, each pair listing a `project_id` with its `impact_coefficient`. A standard counts as satisfied in a cycle when the sum of the covered `impact_coefficient` values over the projects carried out in that cycle does not exceed its `impact_limit`; a standard not counted as satisfied imposes no restriction. At least `minimum_standards_satisfied` standards must be counted as satisfied in every cycle.

Maximize the total phase-adjusted annual fuel savings, the sum over all selected projects of `annual_fuel_saving` times the benefit multiplier of the cycle in which they are carried out. All data are fixed explicitly in `instance.json`.

Report the optimal objective, every selected project with its cycle, and the standards counted as satisfied in each cycle.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

The arrays below use positional rows; the listed order is part of the data contract.
- `funding_cycles`: array with 3 records.
  Row fields, in order:
  1. cycle identifier (string).
  2. total cycle budget (integer).
  3. cycle benefit multiplier (number).
  4. per-location cap map (object map from string keys to integer values).
- `schema`: object with fields:
  - `projects`: string scalar describing the positional project-row fields.
  - `review_standards`: string scalar describing the positional standard-row and covered-item fields.
- `projects`: array with 64 records.
  Row fields, in order:
  1. `project_id` (string).
  2. `district` (string).
  3. `capital_required` (integer).
  4. `annual_fuel_saving` (integer).
- `review_standards`: array with 40 records.
  Row fields, in order:
  1. `standard_id` (string).
  2. `impact_limit` (integer).
  3. covered-item pairs (array of pairs):
     1. `project_id` (string).
     2. `impact_coefficient` (integer).
- `incompatible_project_pairs`: array of string pairs with shape [102, 2].
- `minimum_standards_satisfied`: integer scalar.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `funding_cycles` is an array of positional rows; each row contains 4 entries of integer, number, object, string type.
- `incompatible_project_pairs` is an array of positional rows; each row contains 2 entries of string type.
