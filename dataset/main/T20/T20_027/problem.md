A network operator plans material flow over a fixed horizon on the explicitly listed directed network. In each period, net inflow minus net outflow at every node must equal its listed `balance` entry. For every arc and period choose nonnegative flow and binary used/open states. Flow is limited by arc capacity when used; a used arc must be open; and at most `max_open_per_period` arcs may be used in one period. An arc may be retired but cannot reopen: being open in a later period requires it to have been open in all earlier periods. Minimize variable flow cost plus per-period fixed cost for open arcs.

All data are fixed and explicitly provided in `instance.json`; no arcs or values are generated at solve time.

## Data schema

- `nodes`: integer number of nodes.
- `periods`: integer number of periods.
- `max_open_per_period`: integer limit on used arcs per period.
- `arcs`: array of directed `[tail, head]` node-index pairs.
- `capacity`, `cost`, `fixed`: numeric arrays aligned with `arcs`.
- `balance`: `nodes` by `periods` numeric array.
