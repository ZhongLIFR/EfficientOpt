The organizing committee of the Games must hire a team of translators so that every one of the `num_languages` required languages is covered by enough staff for shift rotation and absence backup. Each candidate in `translators` is described by a hiring `cost` and the list of `languages` the candidate can interpret; a language counts as covered when at least `minimum_interpreters_per_language` hired translators can interpret it. The total number of hired translators must stay between `team_size_minimum` and `team_size_maximum`.

Minimize the total hiring cost, which is the sum of `cost` over all hired translators

Report the minimum total hiring cost and the set of translators selected.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.num_languages`: integer
  - `instance.translators`: array[316] of records with fields:
    - `name`: string
    - `cost`: integer
    - `languages`: array[7] of integer
  - `instance.minimum_interpreters_per_language`: integer
  - `instance.team_size_minimum`: integer
  - `instance.team_size_maximum`: integer
  - `instance.agency_groups`: array[16] of records with fields:
    - `name`: string
    - `translators`: array[20] of integer
    - `maximum_hires`: integer
  - `instance.incompatible_pairs`: array[47] of array

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `incompatible_pairs` is an array of positional rows; each row contains 2 entries of numeric type.
