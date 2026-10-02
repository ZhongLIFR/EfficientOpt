A program operates independently in 12,500 service regions. Each region has one sterile equipment depot, 14 indexed health centers, and any number of identical medical logistics vehicles. Every route starts and ends at depot 0. Each customer must be visited exactly once, and the total demand on a route cannot exceed vehicle capacity 4.

Minimize the sum of directed travel costs over all regions. Report the minimum total cost. Split deliveries, repeated visits, open routes, and travel between regions are forbidden.

All authoritative demands and complete directed distance matrices are explicitly stored in `instance.json`; no data is generated at solve time.
## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `region_count`: integer equal to 12500.
- `customer_count`: integer equal to 14.
- `vehicle_capacity`: integer equal to 4.
- `regions`: array[12500] of records with fields:
    - `index`: integer
    - `customer_demand`: array[14] of integer
    - `distance`: array[15] of array

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `regions[].distance` is an array of positional rows; each row contains 15 entries of numeric type.
