A spare-parts network must decide which depots to open and replenish 480 distinct maintenance bases. Every base must receive all required part units and may split demand among the depots listed in `eligible_depots`. Every depot record gives its region, stocked part families, unit-throughput capacity, handling capacity, and fixed opening cost. Every base record gives its part family, region, required units, and handling points consumed per unit. The `replenishment_costs` records give the fixed unit cost for every allowed base-depot pair.

A depot that is not open cannot serve any base. For each open depot, shipped units must not exceed `throughput_capacity_units`, and total handling points must not exceed `handling_capacity_points`. Minimize total fixed opening cost plus total replenishment cost.

Report the minimum total cost, open depots, and positive base-depot shipments.

## Data schema

The complete fixed instance is in `instance.json`; no value is generated or sampled while constructing or solving the optimization model.

- `depots`: array with 78 distinct records containing `id`, `region`, `part_families`, `throughput_capacity_units`, `handling_capacity_points`, and `opening_cost`.
- `maintenance_bases`: array with 480 distinct records containing `id`, `part_family`, `region`, `required_part_units`, `handling_points_per_unit`, and `eligible_depots`.
- `replenishment_costs`: array with 11087 fixed allowed-pair records containing `maintenance_base`, `depot`, and `replenishment_cost_per_unit`.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `depots[].part_families` is an array of strings; entries retain their listed order.
- `maintenance_bases[].eligible_depots` is an array of strings; entries retain their listed order.
