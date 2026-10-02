A district energy plant plans 110 heat-delivery products over 160 consecutive production shifts. For every product and shift, charging may be inactive with quantity zero. If it is active, its charging quantity must lie between the listed positive minimum and maximum batch sizes. Thermal units can be stored for later shifts, but backorders are forbidden.

Each product starts with zero inventory. In every shift, previous inventory plus current charging must equal current demand plus ending inventory. The sum charged across products cannot exceed that shift's shared line capacity. Minimize charging cost plus ending-inventory holding cost over all shifts.

Report the minimum total cost, total charging quantity, and final total inventory. All numerical data are fixed in `instance.json`; nothing is generated at solve time.

## Data schema

- `products`: 110 records with zero-based `index` and display `code`.
- `periods`: 160 records with zero-based `index` and display `code`.
- `minimum_batch[p][t]`, `maximum_batch[p][t]`: positive activation interval for product `p` in shift `t`.
- `demand[p][t]`: demand that must be met by the end of shift `t`.
- `charging_cost[p][t]`: cost per charging quantity unit.
- `holding_cost[p][t]`: cost per unit of ending inventory.
- `line_capacity[t]`: shared charging capacity in shift `t`.
- `quantity_unit` and `cost_unit`: unit descriptions.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `minimum_batch` is an array of positional rows; each row contains 160 entries of numeric type.
- `maximum_batch` is an array of positional rows; each row contains 160 entries of numeric type.
- `demand` is an array of positional rows; each row contains 160 entries of numeric type.
- `charging_cost` is an array of positional rows; each row contains 160 entries of numeric type.
- `holding_cost` is an array of positional rows; each row contains 160 entries of numeric type.
- `line_capacity` is an array of integer values; entries retain their listed order.
