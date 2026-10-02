An operator must match 650,000 satellite passes one-to-one with 650,000 ground-contact windows. Each member of the left group is eligible for exactly eight members of the right group, with an integer contact penalty for every eligible pair. Ineligible pairs may not be selected.

Choose exactly one eligible right-side member for every left-side member, and use every right-side member exactly once. Minimize the total contact penalty. Report the minimum total and the selected pairs.

All authoritative numerical data are explicitly stored in `instance.json`; no data is generated at solve time.

## Data schema

- `worker_count` and `task_count`: the equal sizes of the two indexed groups; indices run from zero through count minus one.
- `left_entity` and `right_entity`: business meanings of the two index sets.
- `options`: one array per left-side index, in index order. Each entry contains exactly eight `[right_index, cost]` pairs. These are all and only the eligible pairs and their integer costs.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `worker_count` is an integer scalar.
- `options` is an array of positional rows; each row contains 8 entries of array type.
