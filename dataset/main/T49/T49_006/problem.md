A municipal waste network must decide which of 84 treatment plants to commission and how to treat the annual waste from 480 distinct districts. Every district's waste must be treated in full and may be split among the plants listed in its `eligible_plants`. Plant records give region, licensed waste types, annual capacity, and fixed commissioning cost. District records give waste type, region, annual tonnes, and eligibility. The `treatment_costs` array gives the fixed unit treatment cost for every allowed district-plant pair.

A plant that is not commissioned cannot treat waste, and the total assigned tonnes at each commissioned plant cannot exceed its annual capacity. Minimize commissioning cost plus treatment cost. Report the minimum total cost, commissioned plants, and positive district-plant treatment quantities.

## Data schema

The complete fixed instance is in `instance.json`; no value is generated or sampled while constructing or solving the optimization model.

- `plants`: array with 84 distinct records containing `id`, `region`, `licensed_waste_types`, `annual_capacity_tonnes`, and `commissioning_cost`.
- `districts`: array with 480 distinct records containing `id`, `waste_type`, `region`, `annual_tonnes`, and `eligible_plants`.
- `treatment_costs`: array with 11141 fixed allowed-pair records containing `district`, `plant`, and `cost_per_tonne`.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `plants[].licensed_waste_types` is an array of strings; entries retain their listed order.
- `districts[].eligible_plants` is an array of strings; entries retain their listed order.
