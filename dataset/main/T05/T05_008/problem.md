A public-health network selects indivisible diagnostic-laboratory upgrades and assigns every selected upgrade to at most one of three funding cycles. Each project record gives its id, laboratory, capital cost, and annual capacity benefit. Each cycle gives a total budget, benefit multiplier, and laboratory-specific budget limits. Pairs in `incompatible_project_pairs` cannot be implemented in the same cycle.

Each `review_standards` record gives a standard id, burden limit, and covered upgrade/coefficient pairs. A standard may be counted as satisfied in a cycle only when the covered burden of upgrades assigned to that cycle does not exceed its limit. At least `minimum_standards_satisfied` standards must be counted as satisfied in every cycle.

Maximize total phase-adjusted diagnostic-capacity benefit. Report the optimal objective, selected upgrades with their cycles, and standards counted as satisfied.

## Data schema

The complete fixed instance is in `instance.json`; no value is generated or sampled while constructing or solving the model.

- `funding_cycles`: 3 positional records `[cycle_id, budget, benefit_multiplier, per_laboratory_cap_map]`.
- `projects`: 68 distinct positional records `[upgrade_id, laboratory, capital_cost, annual_capacity_benefit]`.
- `review_standards`: 42 distinct positional records `[standard_id, burden_limit, [[upgrade_id, burden_coefficient], ...]]`.
- `incompatible_project_pairs`: 105 distinct upgrade-id pairs.
- `minimum_standards_satisfied`: integer scalar equal to 33.
- `schema`: positional-field descriptions for `projects` and `review_standards`.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `incompatible_project_pairs` is an array of positional rows; each row contains 2 entries of string type.
