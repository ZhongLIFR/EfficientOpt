A fire service is selecting improvement packages for 40 fire station locations. Each location offers 16 mutually incompatible packages, and selecting no package at a location is allowed. At most one package may be selected at each location.

Every package has a value and consumes four shared resources. Total use of each resource must not exceed its listed budget. Maximize total value. Report the maximum value, selected location-package pairs, and total use of each resource.

All authoritative numerical data are explicitly stored in `instance.json`; no data is generated at solve time.

## Data schema

- `resource_names`: four resource labels.
- `resource_budget[r]`: available amount of resource `r`.
- `sites`: 40 location records with zero-based `index`, display `code`, and 16 `alternatives`.
- Each alternative has zero-based `index`, integer `value`, and four-entry integer `resource_use`.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `resource_budget` is an array of integer values; entries retain their listed order.
