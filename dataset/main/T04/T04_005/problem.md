A school district transports indivisible student units from 2450 fixed cohorts to 2450 attendance groups. `supplies[i]` is the exact number of units cohort i must send, `demands[j]` is the exact number group j must receive, and `costs[i][j]` is the fixed penalty per transported unit. Total supply equals total demand.

Choose a nonnegative whole-number shipment for every cohort-group pair so that every cohort sends its full supply and every attendance group receives its full demand. Minimize total penalty and report the minimum value and complete shipment plan.

## Data schema

The complete fixed instance is in `instance.json`; no value is generated or sampled while constructing or solving the optimization model.

- `supplies`: array with 2450 fixed integer records.
- `demands`: array with 2450 fixed integer records.
- `costs`: fixed two-dimensional integer array with 2450 rows and 2450 columns.
