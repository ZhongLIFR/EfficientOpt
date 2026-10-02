A mining company must decide, for each of `mines` mines and each of `years` years, whether the mine operates in that year and whether it remains open. An operating mine must be open. Once a mine is closed, it cannot reopen, although an open mine need not operate. For every mine and year, `value` gives the operating value obtained if the mine operates in that year, and each mine also has a fixed annual `royalty` that is paid for every year in which the mine is kept open. In each year at most `max_operating` mines may operate.

Report the maximum total net value and the complete operating and open-or-closed schedule for every mine and year.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.mines`: integer
  - `instance.years`: integer
  - `instance.max_operating`: integer
  - `instance.royalty`: array[2400] of number
  - `instance.value`: array[2400] of array

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `value` is an array of positional rows; each row contains 31 entries of numeric type.
