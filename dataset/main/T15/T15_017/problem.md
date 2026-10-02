An organization must choose a portfolio of options for each of the 7 programs listed in `programs` in `instance.json`. Every program has its own option list and requirement list. Selecting an option incurs its listed positive integer `cost`.

For every requirement, at least `required` options among the zero-based positions in `eligible_options` must be selected from that same program. Decisions belonging to one program do not satisfy requirements of another program.

Choose all option portfolios to minimize their total cost. Report the minimum total cost and the selected option positions for every program.

All numerical data are fixed and explicitly listed in `instance.json`; no values are generated or sampled while solving.

## Data schema

- `programs`: array with 7 program records (option/requirement counts by program: 100/78, 104/77, 107/83, 109/81, 116/87, 117/86, 123/91).
- `programs[].name`: string identifier.
- `programs[].options`: array of option records.
- `programs[].options[].id`: string identifier.
- `programs[].options[].cost`: positive integer.
- `programs[].requirements`: array of requirement records.
- `programs[].requirements[].id`: string identifier.
- `programs[].requirements[].eligible_options`: array of zero-based integer positions into the sibling `options` array.
- `programs[].requirements[].required`: integer equal to 1 or 2 and no larger than the length of `eligible_options`.
