A city selects indivisible filtration, disinfection, heat-recovery, ventilation, and safety upgrades from `projects` and assigns every selected upgrade to at most one of the three `funding_cycles`. Each project record gives its id, aquatic centre, capital cost, and annual service benefit. Each cycle gives a total budget, a benefit multiplier, and per-centre spending limits. Projects listed together in `incompatible_project_pairs` cannot be installed in the same cycle.

Each record in `review_standards` gives a standard id, a burden limit, and covered project/coefficient pairs. A standard may be counted as satisfied in a cycle only when the total covered burden of projects assigned to that cycle does not exceed its limit. At least `minimum_standards_satisfied` standards must be counted as satisfied in every cycle.

Maximize total phase-adjusted service benefit. Report the optimal objective, every selected project with its cycle, and the standards counted as satisfied in each cycle.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `funding_cycles`: 3 positional records `[cycle_id, budget, benefit_multiplier, per_centre_cap_map]`.
- `projects`: 72 distinct positional records `[upgrade_id, aquatic_centre, capital_cost, annual_service_benefit]`.
- `review_standards`: 44 distinct positional records `[standard_id, burden_limit, [[upgrade_id, burden_coefficient], ...]]`.
- `incompatible_project_pairs`: 120 distinct pairs of project ids.
- `minimum_standards_satisfied`: integer scalar equal to 34.
- `schema`: positional-field descriptions for `projects` and `review_standards`.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `incompatible_project_pairs` is an array of positional rows; each row contains 2 entries of string type.
