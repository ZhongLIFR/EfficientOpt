A regional emergency-response authority must select exactly one operating plan for each of 3800 response units. Every listed plan has a response-capacity score, an operational-risk score, and a service value. The selected plans must collectively reach the published minimum response capacity and must not exceed the published maximum total risk.

Plans are indivisible choices: exactly one listed option must be selected for every unit. Maximize the total service value. Report the optimal value, total capacity, total risk, and selected option for each unit. All numerical data are fixed in `instance.json`.

## Data schema
- `options_per_unit`: number of options for every unit.
- `capacity_attribute_upper_bound`, `risk_attribute_upper_bound`: valid attribute bounds.
- `minimum_total_capacity`, `maximum_total_risk`: global requirements.
- `units`: 3800 records; each has an integer `unit` and an `options` array. Every option contains integer `option`, `capacity`, `risk`, and `value`.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `options_per_unit` is an integer scalar.
- `capacity_attribute_upper_bound` is an integer scalar.
- `risk_attribute_upper_bound` is an integer scalar.
- `minimum_total_capacity` is an integer scalar.
- `maximum_total_risk` is an integer scalar.
