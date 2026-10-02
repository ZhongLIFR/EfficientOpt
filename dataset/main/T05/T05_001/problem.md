A cooperative chooses how many hectares to plant on each candidate plot in `plots`, from zero up to that plot's `maximum_hectares`. Every plot names its `region` and the `profit_per_hectare` it earns when planted. Total planted area may not exceed `total_area_cap`, and the planted area within each of the eight regions may not exceed the corresponding value in the `region_area_caps` map.

Each water-resilience standard in `water_standards` provides `water_risk_coefficients` for the plots it affects and a `risk_limit`. A standard counts as met when the sum over its affected plots of `water_risk_coefficients` times planted hectares does not exceed its `risk_limit`. At least `minimum_standards_met` standards must be counted as met; a standard not counted as met imposes no risk restriction.

Maximize total profit, the sum over all plots of `profit_per_hectare` times planted hectares. All data are explicit in `instance.json`.

Report the maximum total profit, every plot with positive planted area, and the standards counted as met.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `plots`: array with 120 records.
  Record fields:
  1. `id`: string scalar.
  2. `region`: string scalar.
  3. `maximum_hectares`: integer scalar.
  4. `profit_per_hectare`: number scalar.
- `region_area_caps`: object map from string keys to integer values.
- `total_area_cap`: integer scalar.
- `water_standards`: array with 55 records.
  Record fields:
  1. `id`: string scalar.
  2. `water_risk_coefficients`: object map from string keys to number values.
  3. `risk_limit`: number scalar.
- `minimum_standards_met`: integer scalar.

Additional fixed fields retained for instance identity or provenance (not used by the optimization model):

- `kind`: fixed instance label string; auxiliary metadata not used in the optimization model.

- `problem_id`: fixed identifier string; auxiliary metadata not used in the optimization model.

