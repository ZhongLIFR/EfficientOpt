An event organizer must hire translators so that every one of 7,200 required languages is covered by at least one hired translator. Each record in `translators` gives one candidate's hiring `cost` and the zero-based language indices that candidate covers.

Choose the set of translators that covers every required language and minimizes total hiring cost. Report the minimum cost and hired translators.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

- `num_languages`: integer scalar equal to 7200.
- `translators`: array with 17280 fixed records. Each record contains a
  string `name`, numeric `cost`, and a `languages` index array.

Additional fixed fields retained for instance identity or provenance (not used by the optimization model):

- `problem_id`: fixed identifier string; auxiliary metadata not used in the optimization model.

- `_difficulty_seed`: fixed construction metadata; not used in the optimization model.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `translators[].languages` is an array of integer values; entries retain their listed order.
