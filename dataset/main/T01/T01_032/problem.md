A manufacturing program contains a fixed set of work orders. For every work order, exactly one of two fully specified execution plans, plan A or plan B, must be selected.

Each plan has a direct cost, consumes several shared resources, and contributes several service scores. The chosen plans must jointly respect every resource capacity, meet every minimum service-score requirement, and satisfy the stated lower and upper limits on how many plan-B selections may be made in each portfolio segment. All work orders participate in shared constraints, so choices must be optimized jointly. Minimize total direct cost and report the minimum objective value.

## Data schema

The complete fixed instance is stored explicitly in `instance.json`; no values are generated or sampled at runtime.

- `resource_names`: ordered array of resource labels.
- `service_names`: ordered array of service-score labels.
- `resource_capacities`: array aligned with `resource_names`.
- `minimum_service_scores`: array aligned with `service_names`.
- `segment_limits`: array of objects with `segment`, `minimum_plan_b`, and `maximum_plan_b`.
- `work_orders`: array of objects. Each object contains:
  - `id`: unique work-order identifier.
  - `segment`: segment label used by `segment_limits`.
  - `cost_a`, `cost_b`: direct cost of the two plans.
  - `resource_a`, `resource_b`: resource-use arrays aligned with `resource_names`.
  - `service_a`, `service_b`: service-score arrays aligned with `service_names`.
