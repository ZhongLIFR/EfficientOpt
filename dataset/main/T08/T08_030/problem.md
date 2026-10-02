The planner chooses a nonnegative continuous quantity for each of 180 activities in each of 16 periods. Every activity has a per-period upper bound, base margin, eligible-spend coefficient, and two operating-resource requirements. Each period has two resource capacities. A period earns the published bonus rate on all eligible spend exactly when its total eligible spend reaches the published threshold; the period record also supplies a valid upper bound on eligible spend.

Across the full campaign, each activity has a published total limit, and the weighted quantity over all periods and activities must satisfy each published campaign-resource limit. Maximize base margin plus earned bonus. All data are fixed in `instance.json`; array indexing and field meanings follow the descriptions above. Report the proven maximum and compact campaign totals.

## Data schema
The complete fixed instance is in `instance.json`; values are explicit and are not generated at runtime.
Field paths use `[]` for array records.
- `period_count`: integer.
- `bonus_rate`: number.
- `activities`: array.
- `periods`: array.
- `activity_total_limits`: array.
- `campaign_resource_limits`: array.
- Nested record fields:
  - `activities[].activity`: integer.
  - `activities[].maximum_quantity`: integer.
  - `activities[].base_margin_per_unit`: integer.
  - `activities[].eligible_spend_per_unit`: integer.
  - `activities[].resource_a_use`: integer.
  - `activities[].resource_b_use`: integer.
  - `periods[].period`: integer.
  - `periods[].resource_a_capacity`: integer.
  - `periods[].resource_b_capacity`: integer.
  - `periods[].bonus_threshold`: number.
  - `periods[].eligible_spend_upper_bound`: integer.
  - `periods[].campaign_resource_coeffs`: array.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `activities` is an array of records; each record has the nested fields listed below.
- `periods` is an array of records; each record has the nested fields listed below.
- `periods[].campaign_resource_coeffs` is an array of numeric values; entries retain their listed order.
- `activity_total_limits` is an array of numeric values; entries retain their listed order.
- `campaign_resource_limits` is an array of numeric values; entries retain their listed order.
