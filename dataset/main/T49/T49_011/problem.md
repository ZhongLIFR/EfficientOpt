Every cargo lot must be loaded in full and may be divided among the holds listed in its `eligible_holds`. Each record in `holds` names the hold `id`, its `deck`, the `cargo_classes` it accepts, its `weight_capacity_tonnes`, its `volume_capacity_m3`, and its `preparation_cost`. Each record in `cargo_lots` names the lot `id`, its `cargo_class`, its `preferred_deck`, the `required_tonnes` that must be loaded, the `volume_per_tonne_m3` each tonne occupies, and the `eligible_holds` list of holds that may take it. The `handling_costs` array holds one record per allowed lot-hold pair with columns `cargo_lot`, `hold`, and `handling_cost_per_tonne`.

Eligibility already enforces cargo-class compatibility and the permitted deck range. A hold that is not prepared cannot receive cargo, and each prepared hold has both a weight capacity and a cubic-volume capacity: the total tonnes loaded into it cannot exceed `weight_capacity_tonnes`, and the total volume, computed as `volume_per_tonne_m3` times the loaded tonnes, cannot exceed `volume_capacity_m3`.

Minimize the total cost, which is the sum of `preparation_cost` over all prepared holds plus, for every tonne loaded, the corresponding `handling_cost_per_tonne`. All data are explicitly supplied in `instance.json`.

Report the minimum total cost, the prepared holds, and all positive lot-hold loading quantities.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `holds`: array with 75 records.
  Record fields:
  1. `id` (string)
  2. `deck` (integer)
  3. `cargo_classes` (array)
  4. `weight_capacity_tonnes` (integer)
  5. `volume_capacity_m3` (integer)
  6. `preparation_cost` (integer)
- `cargo_lots`: array with 816 records.
  Record fields:
  1. `id` (string)
  2. `cargo_class` (string)
  3. `preferred_deck` (integer)
  4. `required_tonnes` (integer)
  5. `volume_per_tonne_m3` (number)
  6. `eligible_holds` (array)
- `handling_costs`: array with 18,648 records.
  Record fields:
  1. `cargo_lot` (string)
  2. `hold` (string)
  3. `handling_cost_per_tonne` (number)

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `holds[].cargo_classes` is an array of strings; entries retain their listed order.
- `cargo_lots[].eligible_holds` is an array of strings; entries retain their listed order.
