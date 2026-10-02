A planner schedules patrol deployments for security patrol staffing over 160,000 consecutive periods. Any nonnegative integer number of deployments may start in a period. A deployment started in period `s` remains active in that period and the following `duration - 1` periods, truncated at the end of the horizon. Its cost is `start_cost` from its start-period record.

For every period, the number of active deployments must be at least that period's `demand`. Minimize total start cost. Report the minimum cost and the number of deployments started in each period.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

- `problem_id`: string identifier; not used in the optimization model.
- `business_context`, `deployment_label`: descriptive strings; not used in the optimization model.
- `periods`: ordered array with 160,000 records.
  - `name`: string period identifier.
  - `demand`: nonnegative integer active-deployment requirement.
  - `start_cost`: positive integer cost per deployment started in this period.
  - `duration`: positive integer number of consecutive active periods for a deployment started here.

The order of `periods` is chronological. No values or records may be generated at solve time.
