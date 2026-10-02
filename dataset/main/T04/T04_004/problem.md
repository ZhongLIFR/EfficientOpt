A clinical distribution system ships indivisible sample units from 2300 collection sites to 2300 processing laboratories. `supplies[i]` gives the exact number of samples available at collection site `i`, `demands[j]` gives the exact number required by laboratory `j`, and `costs[i][j]` is the per-sample transport cost. Total supply equals total demand.

Choose a nonnegative whole-number shipment for every site-laboratory pair. Every collection site must send its complete supply and every laboratory must receive its complete demand. Minimize total transport cost and report the minimum cost and shipment plan.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `supplies`: array with 2300 positive integers.
- `demands`: array with 2300 positive integers whose total equals total supply.
- `costs`: 2300 by 2300 array of fixed positive integer costs.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `costs` is an array of positional rows; each row contains 2300 entries of numeric type.
