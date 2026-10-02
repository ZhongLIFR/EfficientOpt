The full pallet requirement of every product must be stored, and a product may be split among the warehouses listed in its `eligible_warehouses`. Each record in `warehouses` names the warehouse `id`, its `region`, the `temperature_zones` it offers, its `pallet_capacity`, its `volume_capacity_m3`, and its `lease_cost`. Each record in `products` names the product `id`, its `temperature`, its `region`, the `required_pallets` that must be stored, the `volume_per_pallet_m3` each pallet occupies, and the `eligible_warehouses` list of warehouses that may store it. The `storage_costs` array holds one record per allowed product-warehouse pair with columns `product`, `warehouse`, and `cost_per_pallet`.

Eligibility already enforces each product's temperature class and allowed region. A warehouse that is not leased cannot store pallets, and at each leased warehouse both the total pallets and the total occupied cubic metres must stay within their limits: the stored pallets cannot exceed `pallet_capacity`, and the occupied volume, computed as each product's stored pallets times its `volume_per_pallet_m3`, cannot exceed `volume_capacity_m3`.

Minimize the total cost, which is the sum of `lease_cost` over all leased warehouses plus, for every pallet stored, the corresponding `cost_per_pallet`. All data are explicitly supplied in `instance.json`.

Report the minimum total cost, the leased warehouses, and all positive product-warehouse pallet allocations.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `warehouses`: array with 76 records.
  Record fields:
  1. `id` (string)
  2. `region` (integer)
  3. `temperature_zones` (array)
  4. `pallet_capacity` (integer)
  5. `volume_capacity_m3` (integer)
  6. `lease_cost` (integer)
- `products`: array with 205 records.
  Record fields:
  1. `id` (string)
  2. `temperature` (string)
  3. `region` (integer)
  4. `required_pallets` (integer)
  5. `volume_per_pallet_m3` (number)
  6. `eligible_warehouses` (array)
- `storage_costs`: array with 4,654 records.
  Record fields:
  1. `product` (string)
  2. `warehouse` (string)
  3. `cost_per_pallet` (number)

Additional fixed fields retained for instance identity or provenance (not used by the optimization model):

- `kind`: fixed instance label string; auxiliary metadata not used in the optimization model.

- `problem_id`: fixed identifier string; auxiliary metadata not used in the optimization model.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `warehouses[].temperature_zones` is an array of strings; entries retain their listed order.
- `products[].eligible_warehouses` is an array of strings; entries retain their listed order.
