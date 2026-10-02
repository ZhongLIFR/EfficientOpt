A regional charging operator allocates nonnegative charging quantities across a fixed set of service contracts. Each contract belongs to one service group, consumes several shared resources per unit, and has a contract-specific continuous piecewise-linear cost curve over its stated quantity range.

The total allocated quantity must meet the system requirement, every service group must receive at least its required quantity, and every shared-resource capacity must be respected. Minimize total charging cost and report the minimum objective value.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `records`: array of contract objects. Each has `group`, strictly increasing `breakpoints`, aligned `values`, and `resource_use` aligned with `resources`.
- `groups`: array of objects with `group` and `minimum_quantity`.
- `resources`: array of objects with `resource` and `capacity`.
- `total_required`: numeric system-wide minimum quantity.
- `quantity_unit`: descriptive string.

Every contract quantity is restricted to the closed interval from its first to its last listed breakpoint. The listed cost values define the complete cost curve on that interval.
