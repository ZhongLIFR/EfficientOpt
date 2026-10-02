A school assigns each student to exactly one attendance group across several classes. Each student's enrollment list identifies the classes they attend. Safe class capacity is given separately for every class and group, and each student-group choice has a preference penalty.

For every class and group, the load is the number of assigned students enrolled in that class. Only the amount by which this load exceeds the corresponding safe capacity is penalized. `excess_weight` scales the total capacity-excess penalty.

Choose one group for every student to minimize weighted capacity excess plus student preference penalties. Report the minimum total penalty and the complete group assignment.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.
The bullets below describe the fixed JSON structure (field names, types, shapes, and array lengths).

- `instance`: object with fields:
  - `instance.problem_id`: string
  - `instance.num_students`: integer
  - `instance.num_groups`: integer
  - `instance.num_classes`: integer
  - `instance.enrollments`: array[500] of array
  - `instance.class_capacity`: array[36] of array
  - `instance.preference_penalty`: array[500] of array
  - `instance.excess_weight`: number
  - `instance._difficulty_seed`: integer

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `enrollments` is an array of positional rows; each row contains 4 entries of numeric type.
- `class_capacity` is an array of positional rows; each row contains 5 entries of numeric type.
- `preference_penalty` is an array of positional rows; each row contains 5 entries of numeric type.
