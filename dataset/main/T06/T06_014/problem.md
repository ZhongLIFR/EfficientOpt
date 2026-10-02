A manufacturer plans four regional plants, 100 biologic product families, and 160 consecutive shifts. Each plant-product-shift operation may be inactive with quantity zero. If active, output must lie between the published positive minimum and maximum batch sizes. Output may be carried as inventory, but all demand must be met without backlog.

Each plant and product starts with zero inventory. At each plant, previous inventory plus current output equals demand plus ending inventory. Total output at a plant cannot exceed its shift-specific line capacity. Minimize operating and inventory-holding cost across the entire network.

Report the minimum total cost, total processed quantity, and final total inventory. All numerical data are explicit in `instance.json`; nothing is generated at solve time.

## Data schema

- `sites`, `products`, `periods`: indexed records.
- `site_data[f]`: all data for site `f`.
- `minimum_batch[p][t]`, `maximum_batch[p][t]`: positive operating interval.
- `demand[p][t]`, `operating_cost[p][t]`, `holding_cost[p][t]`: item-period data.
- `line_capacity[t]`: site and shift capacity.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `site_data` is an array of records; each record has the nested fields listed below.
- `site_data[].demand` is an array of positional rows; each row contains 160 entries of numeric type.
- `site_data[].holding_cost` is an array of positional rows; each row contains 160 entries of numeric type.
- `site_data[].line_capacity` is an array of integer values; entries retain their listed order.
- `site_data[].maximum_batch` is an array of positional rows; each row contains 160 entries of numeric type.
- `site_data[].minimum_batch` is an array of positional rows; each row contains 160 entries of numeric type.
- `site_data[].operating_cost` is an array of positional rows; each row contains 160 entries of numeric type.
- `sites`, `products`, and `periods` are arrays of records; each record has an integer `index` and a string `code`.
- Each `site_data` record has an integer `site_index`; its batch, demand, operating-cost, and holding-cost fields are product-by-period positional rows, and `line_capacity` is a period-indexed numeric vector.
