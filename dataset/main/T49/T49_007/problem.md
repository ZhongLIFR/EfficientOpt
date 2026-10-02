An emergency response network must decide which of 82 relief hubs to open and how to deliver supplies to 480 distinct affected zones. Every zone must receive all required units of its supply type and may split demand among `eligible_hubs`. Hub records give sector, stocked supply types, daily throughput, and opening cost. Zone records give supply type, sector, required units, and eligibility. `delivery_costs` gives the fixed unit cost for every allowed zone-hub pair.

A closed hub cannot ship supplies, and total units shipped by an open hub cannot exceed its throughput. Minimize total hub opening and delivery cost. Report the minimum cost, open hubs, and positive shipments.

## Data schema

The complete fixed instance is in `instance.json`; no value is generated or sampled while constructing or solving the optimization model.

- `hubs`: array with 82 distinct records containing `id`, `sector`, `stock_types`, `daily_throughput_units`, and `opening_cost`.
- `zones`: array with 480 distinct records containing `id`, `supply_type`, `sector`, `required_units`, and `eligible_hubs`.
- `delivery_costs`: array with 11257 fixed allowed-pair records containing `zone`, `hub`, and `cost_per_unit`.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `hubs[].stock_types` is an array of strings; entries retain their listed order.
- `zones[].eligible_hubs` is an array of strings; entries retain their listed order.
