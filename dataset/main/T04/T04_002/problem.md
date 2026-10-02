A regional electricity operator must move indivisible power blocks from 800 distinct plants to 800 distinct cities at minimum total cost. `supplies[i]` is the exact number of blocks available at plant `i`, `demands[j]` is the exact number required by city `j`, and `costs[i][j]` is the fixed cost of sending one block on that route. Total supply equals total demand.

Choose a nonnegative whole-number shipment for every plant-city pair. Every plant must ship its full supply and every city must receive its full demand. Minimize total transmission cost and report the minimum objective value.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `supplies`: array of 800 positive integers.
- `demands`: array of 800 positive integers whose total equals total supply.
- `costs`: 800 by 800 array of fixed positive integer route costs.
