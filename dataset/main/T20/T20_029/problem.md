A network operator plans material flows over a fixed horizon of periods on a directed network. Each entry of `arcs` gives the tail and head node of one link. The link data in `capacity`, `cost`, and `fixed` give its maximum flow, per-unit flow cost, and per-period activation cost.

At every period, the net inflow minus net outflow at each node must equal the corresponding entry of `balance`. For each link and period choose a nonnegative flow and whether the link is used and open. Flow cannot exceed the link capacity when the link is used, a used link must be open, and no more than `max_open_per_period` links may be used in one period. If a link is used in period `t`, it must be open in period `t` and every earlier period.

Minimize the total variable flow cost plus the fixed cost of opened links. Report the minimum total cost and the flow, use, and open decisions for every link and period.

All numerical data are fixed and provided in the instance file.

## Data schema

- `nodes`: integer scalar.
- `periods`: integer scalar.
- `max_open_per_period`: integer scalar.
- `arcs`: array with 152 rows; each row is an array with 2 values.
- `capacity`: array with 152 values.
- `cost`: array with 152 values.
- `fixed`: array with 152 values.
- `balance`: array with 36 rows; each row is an array with 8 values.

The instance may contain auxiliary identifier or provenance fields; these are not decision data.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `capacity` is an array of integer values; entries retain their listed order.
- `cost` is an array of integer values; entries retain their listed order.
- `fixed` is an array of integer values; entries retain their listed order.
