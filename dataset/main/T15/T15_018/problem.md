The organization operates the named business programs listed in `blocks`. Each program has its own `options` and `requirements`. Selecting an option incurs its listed `cost`. For every requirement in a program, at least `required` of the positions listed in `eligible_options` must be selected from that same program's `options` array.

Choose the selected options for every program to minimize their total cost. Report the minimum total cost and the selected option positions in each program.

All numerical data are fixed and explicitly provided in `instance.json`; do not generate or infer additional rows while solving.

## Data schema

- `business_structure`: descriptive string.
- `blocks`: array[2] of program records.
- `blocks[].name`: string.
- `blocks[].options_label`: string.
- `blocks[].requirements_label`: string.
- `blocks[].options`: array of option records.
- `blocks[].options[].id`: string.
- `blocks[].options[].cost`: positive integer.
- `blocks[].requirements`: array of requirement records.
- `blocks[].requirements[].requirement`: string.
- `blocks[].requirements[].eligible_options`: array of zero-based integer positions into the corresponding sibling `options` array.
- `blocks[].requirements[].required`: nonnegative integer not exceeding the length of `eligible_options`.
