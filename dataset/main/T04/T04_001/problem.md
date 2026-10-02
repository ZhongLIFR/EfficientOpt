A telecommunications operator must route a fixed volume of integer packet units through a communication network at minimum total link cost. The network is described in `instance.json`: `nodes` is the ordered list of 3522 network nodes, and `arcs` lists the 615035 directed links. Each link gives a `tail` node, a `head` node, an integer `capacity`, and a `cost` per packet carried. The array `balance` contains one integer per node: a positive value means the node must send that many more packets than it receives, while a negative value means it must absorb that many more packets than it sends.

Choose a nonnegative whole-number flow on every directed arc, respecting every arc capacity and the supplied node-balance requirement at every node. Minimize total cost, the sum over all arcs of `cost` times the flow carried.

Report the minimum total cost and the complete routing plan for every arc.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `nodes`: array with 3522 records.
- `arcs`: array with 615035 records. Each record contains integer fields `tail`, `head`, `capacity`, and `cost`.
- `balance`: array with 3522 integer records.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `nodes` is an array of strings; entries retain their listed order.
