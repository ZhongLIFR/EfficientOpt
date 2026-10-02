A distributed organization must solve 300 independent packing cases, one for each of its field stations. Each case contains 14 indivisible sample packs. Items belonging to different cases cannot share a cooler. Every available cooler has the same capacity.

Assign every item in its entirety to exactly one candidate unit in its own case. The total size assigned to a unit must not exceed its capacity. Minimize the total number of used units over all cases. Report the minimum total and a compact summary; do not print all assignments unless needed to verify the result.

## Data schema

- `container_capacity`: positive integer capacity of every unit.
- `regions`: array of exactly 300 independent case records.
- Every case record has zero-based integer `index`, display string `code`, and an `items` array containing exactly 14 records.
- Every item record has zero-based integer `index`, display string `code`, and positive integer `size` not exceeding `container_capacity`.

The complete fixed instance is stored explicitly in `instance.json`; no numerical values are generated or sampled at runtime.
