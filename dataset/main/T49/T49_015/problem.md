A laboratory network must calibrate instrument suites and assign 480 distinct assay batches. Each batch must receive its full required runtime and may split that runtime among the suites listed in its `eligible_instrument_suites`. Every suite record states its laboratory, supported assay types, runtime capacity, calibration-resource capacity, and fixed calibration cost. Every batch record states its assay type, home laboratory, required runtime, and calibration points consumed per processing hour. The `processing_costs` records give the fixed per-hour cost for every allowed batch-suite pair.

A suite that is not calibrated cannot process any batch. For each calibrated suite, assigned runtime must not exceed `runtime_capacity_hours`, and assigned calibration points must not exceed `calibration_capacity_points`. At most one suite in every listed `incompatible_suite_pairs` pair may be calibrated. Minimize total fixed calibration cost plus total processing cost.

Report the minimum total cost, calibrated suites, and positive batch-suite allocations.

## Data schema

The complete fixed instance is in `instance.json`; no value is generated or sampled while constructing or solving the optimization model.

- `instrument_suites`: array with 78 distinct suite records containing `id`, `lab`, `assay_types`, `runtime_capacity_hours`, `calibration_capacity_points`, and `calibration_cost`.
- `assay_batches`: array with 480 distinct batch records containing `id`, `assay_type`, `home_lab`, `required_runtime_hours`, `calibration_points_per_hour`, and `eligible_instrument_suites`.
- `processing_costs`: array with 11280 fixed allowed-pair records containing `assay_batch`, `instrument_suite`, and `processing_cost_per_hour`.
- `incompatible_suite_pairs`: array with 64 fixed suite pairs.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `incompatible_suite_pairs` is an array of positional rows; each row contains 2 entries of string type.
- `instrument_suites[].assay_types` is an array of strings; entries retain their listed order.
- `assay_batches[].eligible_instrument_suites` is an array of strings; entries retain their listed order.
