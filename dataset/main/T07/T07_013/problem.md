A public-school authority is selecting energy-retrofit projects for 100 campuses. Each campus offers 16 mutually incompatible packages, and selecting no package at a campus is allowed. At most one package may be selected for each campus.

Every package has a value and consumes four shared resources. The total use of each resource across all selected packages must not exceed its listed budget. Maximize total value.

Report the maximum total value, the selected campus-package pairs, and total use of every resource. All authoritative numerical data are fixed in `instance.json`; nothing is generated at solve time.

## Data schema

- `resource_names`: four resource labels.
- `resource_budget[r]`: available amount of resource `r`.
- `sites`: 100 campus records with zero-based `index`, display `code`, and 16 `alternatives`.
- Each alternative has zero-based `index`, integer `value`, and four-entry integer `resource_use`.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `resource_budget` is an array of integer values; entries retain their listed order.
