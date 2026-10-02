
A health authority must open a subset of candidate specialty clinics and assign every patient to exactly one eligible clinic. Each record in `clinics` gives a clinic id, coordinates, available treatment minutes, opening cost, and supported specialties. Each record in `patients` gives a patient id, required specialty, coordinates, treatment minutes, and the clinic ids eligible to serve that patient. `assignment_costs` contains exactly one cost record for every allowed patient-clinic pair.

An assignment is allowed only when its pair appears in `assignment_costs`. Every patient must be assigned once. A closed clinic cannot receive assignments, and the total treatment minutes assigned to an open clinic cannot exceed its capacity. Minimize clinic-opening cost plus assignment cost. Report the minimum cost, opened clinic ids, and each patient's assigned clinic.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated at runtime.

## Data schema

- `clinics`: array with 100 records. Each record has `id` (string), `x_km` (integer), `y_km` (integer), `capacity_minutes` (integer), `opening_cost` (integer), and `specialties` (array of strings).
- `patients`: array with 900 records. Each record has `id` (string), `specialty` (string), `x_km` (integer), `y_km` (integer), `treatment_minutes` (integer), and `eligible_clinics` (array of clinic-id strings).
- `assignment_costs`: array with 19,324 records. Each record has `patient` (string), `clinic` (string), and `cost` (number).

The order of records and nested arrays is the order stored in the fixed JSON file.
