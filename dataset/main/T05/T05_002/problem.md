A city chooses a nonnegative implementation intensity for each of the 121 redevelopment projects in `projects`, up to that project's `maximum_intensity`. Every project names its `district` and the `public_value_per_unit` earned per unit of intensity. Total intensity may not exceed `total_intensity_cap`, and the intensity within each administrative district may not exceed the corresponding value in `district_intensity_caps`.

Each community agreement in `community_agreements` lists `disruption_coefficients` for the projects it affects and a `disruption_limit`. An agreement counts as honoured when the sum over its affected projects of `disruption_coefficients` times intensity does not exceed its `disruption_limit`. At least `minimum_agreements_honoured` agreements must be counted as honoured; an agreement not counted as honoured imposes no disruption restriction.

Maximize total public value, the sum over all projects of `public_value_per_unit` times intensity. Report the maximum total public value, every project with positive intensity, and the agreements counted as honoured.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `projects`: array with 121 records. Each record contains `id`, `district`, `maximum_intensity`, and `public_value_per_unit`.
- `district_intensity_caps`: object mapping district identifiers to capacity values.
- `total_intensity_cap`: integer scalar.
- `community_agreements`: array with 64 records. Each record contains `id`, an explicit `disruption_coefficients` map, and `disruption_limit`.
- `minimum_agreements_honoured`: integer scalar.
