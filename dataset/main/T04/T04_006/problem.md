An attendance office must assign integer attendance units from 2300 origin groups to 2300 time groups. `supplies[i]` is the exact number of units that origin group i must send, `demands[j]` is the exact number that time group j must receive, and `costs[i][j]` is the penalty per unit assigned from origin group i to time group j. Total supply equals total demand.

Choose a nonnegative whole-number assignment for every origin-time-group pair so that every origin group sends its full supply and every time group receives its full demand. Minimize the sum of per-unit penalties over all assignments. Report the minimum total penalty and the complete assignment plan.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `supplies`: array with 2300 integer records.
- `demands`: array with 2300 integer records.
- `costs`: two-dimensional array with 2300 rows and 2300 columns.
