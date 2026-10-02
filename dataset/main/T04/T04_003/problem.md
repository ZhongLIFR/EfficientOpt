An electricity operator must move indivisible power blocks from 2450 plants to 2450 cities at minimum total cost. `supplies[i]` is the exact number of units available at plant `i`, `demands[j]` is the exact number required by city `j`, and `costs[i][j]` is the fixed cost of sending one unit on that route. Total supply equals total demand.

Choose a nonnegative whole-number shipment for every plant-city pair. Every plant must ship its full supply and every city must receive its full demand. Minimize total transmission cost and report the minimum cost and complete shipment plan.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `supplies`: array with 2450 positive integers.
- `demands`: array with 2450 positive integers whose total equals total supply.
- `costs`: 2450 by 2450 array of fixed positive integer costs.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `costs` is an array of positional rows; each row contains 2450 entries of numeric type.
