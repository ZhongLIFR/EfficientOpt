The organizing committee of an Olympic event must hire a team of translators so that every language required at the event is covered by at least one hired translator. The instance records the number of required languages in `num_languages`, and lists the candidate translators in `translators`. Each entry of `translators` gives the hiring `cost` of that translator and the `languages` they speak, expressed as the indices of the required languages; a single translator may cover several languages.

Report the minimum total hiring cost and the complete set of translators to hire.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.problem_id`: string
  - `instance.num_languages`: integer
  - `instance.translators`: array[17280] of records with fields:
    - `name`: string
    - `cost`: integer
    - `languages`: array[8] of integer
  - `instance._difficulty_seed`: integer
