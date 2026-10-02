
A network operator plans material flows over a fixed horizon on a directed network. `arcs[a]` gives the tail and head of link `a`; `capacity[a]`, `cost[a]`, and `fixed[a]` give its flow capacity, variable cost, and per-period open cost. At every period, net inflow minus net outflow at node `i` must equal `balance[i][t]`.

For every link and period choose a nonnegative flow and binary `use` and `open` decisions. Flow is at most link capacity when used, and a used link must be open. At most `max_open_per_period` links may be used in a period. If a link is used in period `t`, it must be open in period `t` and every earlier period. Minimize total variable flow cost plus all per-period open costs.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated at runtime.

## Data schema

- `nodes`: integer scalar equal to 36.
- `periods`: integer scalar equal to 8.
- `max_open_per_period`: integer scalar.
- `arcs`: array with 152 rows and two integer node indices per row.
- `capacity`, `cost`, and `fixed`: arrays with 152 numeric entries each.
- `balance`: array with 36 rows and 8 numeric entries per row.
- Auxiliary identifier or provenance fields are not decision data.
