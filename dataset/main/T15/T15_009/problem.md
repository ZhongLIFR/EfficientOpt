A power utility plans allocation across 110 regions listed in `blocks` in `instance.json`. Every region lists its own generators, demand centers, available generation, required demand, and per-unit allocation costs. The regions contain between 215 and 225 generators and between 217 and 227 demand centers.

Within each region, choose the nonnegative whole-number amount allocated only between the generators and demand centers listed in that region. Every generator must allocate its complete supply and every demand center must receive its exact demand. Minimize the total allocation cost across all regions.

Report the minimum total cost and the complete allocation plan for every region.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled while constructing or solving the optimization model.

- `blocks`: array of 110 distinct region records. Each record contains:
  - `supplies`: positive integer array, one entry per generator;
  - `demands`: positive integer array, one entry per demand center, with the same total as `supplies`;
  - `costs`: rectangular array whose row count equals `supplies` length and whose column count equals `demands` length; each entry is a fixed integer per-unit allocation cost.
