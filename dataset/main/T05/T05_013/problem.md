A spaceport authority selects which indivisible fire-suppression, propellant-handling, telemetry, access-control, and emergency-power upgrades to install from the `projects` array and assigns every selected upgrade to one of the three `funding_cycles`; an upgrade may be implemented in at most one cycle. Each upgrade record lists an upgrade id, its `operational_zone`, the `capital_cost`, and the `readiness_benefit` it delivers, and the `schema` entry documents this column layout for the `projects` and `review_standards` arrays. Each cycle record lists the cycle id, the total budget, a benefit multiplier, and a map of per-zone spending limits. Across the whole programme, at least `minimum_projects_per_group` upgrades must be selected in each operational zone. Listed pairs in `incompatible_project_pairs` cannot be installed in the same cycle.

Each review standard in `review_standards` gives a standard id, a `burden_limit`, and the covered pairs, each pair listing an `upgrade_id` with its `burden_coefficient`. A standard counts as satisfied in a cycle when the sum of the covered `burden_coefficient` values over the upgrades installed in that cycle does not exceed its `burden_limit`; a standard not counted as satisfied imposes no restriction. At least `minimum_standards_satisfied` standards must be counted as satisfied in every cycle.

Maximize the total window-adjusted readiness benefit, the sum over all selected upgrades of `readiness_benefit` times the benefit multiplier of the cycle in which they are installed. All data are fixed explicitly in `instance.json`.

Report the optimal objective, every selected upgrade with its cycle, and the standards counted as satisfied in each cycle.

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
  1. `upgrade_id` (string).
  2. `operational_zone` (string).
  3. `capital_cost` (integer).
  4. `readiness_benefit` (integer).
- `review_standards`: array with 40 records.
  Row fields, in order:
  1. `standard_id` (string).
  2. `burden_limit` (integer).
  3. covered-item pairs (array of pairs):
     1. `upgrade_id` (string).
     2. `burden_coefficient` (integer).
- `incompatible_project_pairs`: array of string pairs with shape [97, 2].
- `minimum_standards_satisfied`: integer scalar.
- `minimum_projects_per_group`: integer scalar.

Additional fixed fields retained for instance identity or provenance (not used by the optimization model):

- `kind`: fixed instance label string; auxiliary metadata not used in the optimization model.

- `problem_id`: fixed identifier string; auxiliary metadata not used in the optimization model.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `funding_cycles` is an array of positional rows; each row contains 4 entries of integer, number, object, string type.
- `incompatible_project_pairs` is an array of positional rows; each row contains 2 entries of string type.
