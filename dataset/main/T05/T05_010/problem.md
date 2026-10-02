A conservation authority selects which indivisible habitat-restoration projects to undertake from the `projects` array and assigns every selected project to one of the three `funding_cycles`; a project may be undertaken in at most one cycle. Each project record lists a project id, its `catchment`, the `capital_cost`, and the `expected_ecological_benefit` it delivers, and the `schema` entry documents this column layout for the `projects` and `review_standards` arrays. Each cycle record lists the cycle id, the total capital budget, a benefit multiplier, and a map of per-catchment spending limits. Listed pairs in `incompatible_project_pairs` cannot be undertaken in the same cycle.

Each review standard in `review_standards` gives a standard id, an `impact_limit`, and the covered pairs, each pair listing a `project_id` with its `impact_coefficient`. A standard counts as satisfied in a cycle when the sum of the covered `impact_coefficient` values over the projects undertaken in that cycle does not exceed its `impact_limit`; a standard not counted as satisfied imposes no restriction. At least `minimum_standards_satisfied` standards must be counted as satisfied in every cycle.

Maximize the total season-adjusted ecological benefit, the sum over all selected projects of `expected_ecological_benefit` times the benefit multiplier of the cycle in which they are undertaken. All data are fixed explicitly in `instance.json`.

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
  2. `catchment` (string).
  3. `capital_cost` (integer).
  4. `expected_ecological_benefit` (integer).
- `review_standards`: array with 40 records.
  Row fields, in order:
  1. `standard_id` (string).
  2. `impact_limit` (integer).
  3. covered-item pairs (array of pairs):
     1. `project_id` (string).
     2. `impact_coefficient` (integer).
- `incompatible_project_pairs`: array of string pairs with shape [99, 2].
- `minimum_standards_satisfied`: integer scalar.

Additional fixed fields retained for instance identity or provenance (not used by the optimization model):

- `kind`: fixed instance label string; auxiliary metadata not used in the optimization model.

- `problem_id`: fixed identifier string; auxiliary metadata not used in the optimization model.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `funding_cycles` is an array of positional rows; each row contains 4 entries of integer, number, object, string type.
- `incompatible_project_pairs` is an array of positional rows; each row contains 2 entries of string type.
