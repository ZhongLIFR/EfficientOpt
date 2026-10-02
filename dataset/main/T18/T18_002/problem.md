An operator must plan a closed business tour through 100 cities. The tour must start at the city identified by `start_city`, visit every city exactly once, and return to the starting city. The travel distance from each city to every other city is given by `distances`.

Minimize the total travel distance of the complete tour.

Report the minimum tour distance and the sequence of cities visited from `start_city` back to `start_city`.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `city_count`: integer scalar equal to 100.
- `start_city`: integer scalar identifying the tour's starting city.
- `distances`: 100 by 100 numeric array; entry `[i][j]` is the distance from city `i` to city `j`.
- `objective`: string describing the requested objective.

Additional fixed fields retained for instance identity or provenance (not used by the optimization model):

- `_difficulty_seed`: fixed construction metadata; not used in the optimization model.

- `case_id`: fixed case identifier; auxiliary metadata not used in the optimization model.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `distances` is an array of positional rows; each row contains 100 entries of numeric type.
