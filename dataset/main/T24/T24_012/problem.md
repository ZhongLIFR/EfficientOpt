A regional health operator must assign exactly one service package to each clinic outreach team. Each package provides a documented benefit score and consumes nurse hours, clinic-room time, refrigerated storage, and transport slots. The operator must respect the total capacity of each shared resource while maximizing the total benefit across all teams.

Every team must receive exactly one of its listed packages. Packages cannot be blended, and no unlisted package is available. All package benefits and resource requirements are fixed in `instance.json`.

Report the maximum total benefit and a compact summary of resource use and selected packages.

## Data schema

- `resource_names`: ordered resource names.
- `resource_capacities`: integer capacities parallel to `resource_names`.
- `groups`: array of team records. Each record has integer `group` and an `options` array; each option has integer `option`, integer `value`, and integer `resource_use` parallel to `resource_names`.

The complete fixed instance is stored explicitly in `instance.json`; no numerical values are generated or sampled at runtime.
