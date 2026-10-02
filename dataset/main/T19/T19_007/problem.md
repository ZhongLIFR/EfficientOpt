An organization is selecting contracts for industrial maintenance coverage. There are 170 independently specified requirements and 580 candidate options.

Each record in `requirements` gives a required service amount. Each record in `options` gives a fixed selection cost and a sparse list of per-requirement service capacities. If an option is selected, it can provide up to the listed capacity separately to every referenced requirement. Capacities for different requirements do not consume a shared resource. An option that is not selected provides no service.

Choose options and allocate their available service so that every requirement receives at least its demand. Minimize the total fixed cost of selected options. Report the minimum cost and the selected options.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

- `problem_id`: string identifier; not used in the optimization model.
- `business_context`: descriptive string; not used in the optimization model.
- `requirements`: array with 170 records.
  - `name`: string identifier.
  - `description`: descriptive string; not used in the optimization model.
  - `demand`: positive integer required service amount.
- `options`: array with 580 records.
  - `name`: string identifier.
  - `description`: descriptive string; not used in the optimization model.
  - `fixed_cost`: positive integer selection cost.
  - `capacities`: sparse array of records with integer `requirement` index and positive integer `amount`.

Array indices in `capacities[].requirement` are zero-based indices into `requirements`. No records may be generated or inferred at solve time.
