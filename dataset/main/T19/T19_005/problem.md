An organization is selecting contracts for industrial maintenance coverage. There are 105 independently specified requirements and 330 candidate options.

Each requirement needs the listed number of distinct service assignments. Each selected option may supply at most one indivisible assignment to each requirement named in its sparse `capacities` list; an unselected option supplies none. Assignments for different requirements do not share capacity.

Choose options and service assignments so that every requirement receives exactly its listed demand from distinct selected options. Minimize the total fixed cost of selected options. Report the minimum cost and selected options.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

- `problem_id`: string identifier; not used in the optimization model.
- `business_context`: descriptive string; not used in the optimization model.
- `requirements`: array with 105 records.
  - `name`: string identifier.
  - `description`: descriptive string; not used in the optimization model.
  - `demand`: positive integer number of distinct assignments required.
- `options`: array with 330 records.
  - `name`: string identifier.
  - `description`: descriptive string; not used in the optimization model.
  - `fixed_cost`: positive integer selection cost.
  - `capacities`: sparse array containing `requirement` (zero-based index) and `amount` (equal to 1).

No records may be generated or inferred at solve time.
