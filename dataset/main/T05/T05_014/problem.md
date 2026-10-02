A mountain authority selects indivisible avalanche-protection projects and assigns every selected project to at most one of three funding cycles. Each project record gives its id, valley, capital cost, and annual risk reduction. Each funding cycle gives a total budget, benefit multiplier, and valley-specific spending limits. Projects listed together in `incompatible_project_pairs` cannot be undertaken in the same cycle.

Each `review_standards` record gives a standard id, a burden limit, and covered project/coefficient pairs. A standard may be counted as satisfied in a cycle only when the covered burden of projects assigned to that cycle does not exceed the limit. At least `minimum_standards_satisfied` standards must be counted as satisfied in every cycle.

Maximize total cycle-adjusted annual risk reduction. Report the optimal objective, selected projects with their cycles, and standards counted as satisfied.

## Data schema

The complete fixed instance is in `instance.json`; no value is generated or sampled while constructing or solving the optimization model.

- `funding_cycles`: 3 positional records `[cycle_id, budget, benefit_multiplier, per_valley_cap_map]`.
- `projects`: 75 distinct positional records `[project_id, valley, capital_cost, annual_risk_reduction]`.
- `review_standards`: 45 distinct positional records `[standard_id, burden_limit, [[project_id, burden_coefficient], ...]]`.
- `incompatible_project_pairs`: 125 distinct project-id pairs.
- `minimum_standards_satisfied`: integer scalar equal to 36.
- `schema`: positional-field descriptions for `projects` and `review_standards`.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `incompatible_project_pairs` is an array of positional rows; each row contains 2 entries of string type.
