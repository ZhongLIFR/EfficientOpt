A regional authority selects indivisible wildfire-resilience projects and assigns every selected project to at most one of three funding cycles. Each project record gives its id, fire-risk zone, investment requirement, and resilience value. Each cycle gives total investment, a value multiplier, and zone-specific investment caps. Pairs in `incompatible_project_pairs` cannot be built in the same cycle.

Each `review_standards` record gives a standard id, impact limit, and covered project/coefficient pairs. A standard may be counted as satisfied in a cycle only when the covered impact of projects assigned to that cycle does not exceed its limit. At least `minimum_standards_satisfied` standards must be counted as satisfied in every cycle.

Maximize total season-adjusted resilience value. Report the optimal objective, selected projects with their cycles, and standards counted as satisfied.

## Data schema

The complete fixed instance is in `instance.json`; no value is generated or sampled while constructing or solving the model.

- `funding_cycles`: 3 positional records `[cycle_id, budget, value_multiplier, per_zone_cap_map]`.
- `projects`: 66 distinct positional records `[project_id, fire_risk_zone, investment_required, resilience_value]`.
- `review_standards`: 41 distinct positional records `[standard_id, impact_limit, [[project_id, impact_coefficient], ...]]`.
- `incompatible_project_pairs`: 110 distinct project-id pairs.
- `minimum_standards_satisfied`: integer scalar equal to 34.
- `schema`: positional-field descriptions for `projects` and `review_standards`.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `incompatible_project_pairs` is an array of positional rows; each row contains 2 entries of string type.
