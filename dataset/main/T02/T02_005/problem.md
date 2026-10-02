A school assigns each of 500 students to exactly one of 5 attendance groups across 36 classes. Each student's enrollment list identifies the classes they attend. Safe class capacity is given separately for every class and group, and each student-group choice has a preference penalty.

For every class and group, the load is the number of assigned students enrolled in that class. Only the amount by which this load exceeds the corresponding safe capacity is penalized. `excess_weight` scales the total capacity-excess penalty.

Choose one group for every student to minimize weighted capacity excess plus student preference penalties. Report the minimum total penalty and the complete group assignment.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `num_students`: integer scalar equal to 500.
- `num_groups`: integer scalar equal to 5.
- `num_classes`: integer scalar equal to 36.
- `enrollments`: array with 500 records; each record explicitly lists the classes attended by one student.
- `class_capacity`: array with 36 records; each record gives the capacities of all attendance groups for one class.
- `preference_penalty`: array with 500 records; each record gives one student's penalty for every attendance group.
- `excess_weight`: positive number scalar.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `enrollments` is an array of positional rows; each row contains 4 entries of numeric type.
- `class_capacity` is an array of positional rows; each row contains 5 entries of numeric type.
- `preference_penalty` is an array of positional rows; each row contains 5 entries of numeric type.
