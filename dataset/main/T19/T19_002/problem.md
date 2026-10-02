The organizing committee of the Games must hire a team of translators so that every one of the `num_languages` required languages is covered by enough staff for shift rotation and absence backup. Each candidate in `translators` is described by a hiring `cost` and the list of `languages` the candidate can interpret; a language counts as covered when at least `minimum_interpreters_per_language` hired translators can interpret it. The total number of hired translators must stay between `team_size_minimum` and `team_size_maximum`.

Minimize the total hiring cost, which is the sum of `cost` over all hired translators

Report the minimum total hiring cost and the set of translators selected.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `num_languages`: integer scalar.
- `translators`: array with 316 records.
  Record fields:
  1. `cost` (integer)
  2. `languages` (array)
- `minimum_interpreters_per_language`: integer scalar.
- `team_size_minimum`: integer scalar.
- `team_size_maximum`: integer scalar.
- `agency_groups`: array with 16 records.
  Record fields:
  1. `name` (string)
  2. `translators` (array)
  3. `maximum_hires` (integer)
- `incompatible_pairs`: array with 47 records.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `translators[].languages` is an array of integer values; entries retain their listed order.
- `incompatible_pairs` is an array of positional rows; each row contains 2 entries of numeric type.
