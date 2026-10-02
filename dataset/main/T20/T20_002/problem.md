A trader must purchase and store raw oil over a fixed horizon of 952320 periods so that the demand of every period is met. For each period, `demand` gives the quantity that must be available, `capacity` the maximum quantity that can be purchased, and `production_cost` the purchase cost of one unit in that period. Oil purchased but not used immediately is carried forward as inventory, and holding one unit over one period costs the fixed rate `holding_cost`.

Report the minimum total purchase and holding cost and the complete purchase and inventory plan for every period.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `demand`: array with 952320 records.
- `capacity`: array with 952320 records.
- `production_cost`: array with 952320 records.
- `holding_cost`: number scalar.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `demand` is an array of integer values; entries retain their listed order.
- `capacity` is an array of integer values; entries retain their listed order.
- `production_cost` is an array of numeric values; entries retain their listed order.
