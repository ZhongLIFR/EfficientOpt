A mining company manages 2,000 distinct mines over 40 years. For each mine and year it decides whether the mine operates and whether it remains open. An operating mine must be open. Once closed, a mine cannot reopen, although an open mine need not operate.

`value[i][t]` is the operating value for mine `i` in year `t`, and `royalty[i]` is paid in every year that mine remains open. In each year, at most `max_operating` mines may operate. Maximize total operating value minus royalty charges.

All numerical data are fixed and explicitly provided in `instance.json`; no values are generated at solve time.

## Data schema

- `mines`: integer number of mines.
- `years`: integer number of years.
- `max_operating`: integer per-year operating limit.
- `royalty`: numeric array of length `mines`.
- `value`: `mines` by `years` fixed numeric array.
