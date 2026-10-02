The planner schedules 75 alloy grade records over 170 consecutive furnace windows. In each item-period pair, processing may be inactive with quantity zero. If active, the quantity must lie between the published positive minimum and maximum batch sizes. Completed quantity can be carried to later periods as inventory, but unmet demand is forbidden.

Each item starts with zero inventory. In every period, previous inventory plus current processing must equal current demand plus ending inventory. Total processing cannot exceed the period's shared furnace throughput. Minimize operating cost plus ending-inventory holding cost over all periods.

Report the minimum total cost, total processed quantity, and final total inventory. All numerical data are fixed in `instance.json`; nothing is generated at solve time.

## Data schema

- `products`: 75 item records with zero-based `index` and display `code`.
- `periods`: 170 period records with zero-based `index` and display `code`.
- `minimum_batch[p][t]`, `maximum_batch[p][t]`: positive activation interval.
- `demand[p][t]`: demand that must be met by the end of the period.
- `operating_cost[p][t]`: cost per processed quantity unit.
- `holding_cost[p][t]`: cost per unit of ending inventory.
- `line_capacity[t]`: shared period capacity.
- `quantity_unit` and `cost_unit`: unit descriptions.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `minimum_batch` is an array of positional rows; each row contains 170 entries of numeric type.
- `maximum_batch` is an array of positional rows; each row contains 170 entries of numeric type.
- `demand` is an array of positional rows; each row contains 170 entries of numeric type.
- `operating_cost` is an array of positional rows; each row contains 170 entries of numeric type.
- `holding_cost` is an array of positional rows; each row contains 170 entries of numeric type.
- `line_capacity` is an array of integer values; entries retain their listed order.
