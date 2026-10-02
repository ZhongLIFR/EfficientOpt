A school district assigns students from 1,100 distinct neighborhoods to 1,100 distinct schools in each of the 8 grades. The grade names are listed in `grades`, the neighborhood names in `neighborhoods`, and the school names in `schools`. In every grade, each neighborhood sends out its full group of `students_per_neighborhood_grade` students, and each school accepts at most `school_capacity_per_grade` students for that grade.

The cost of sending one student from a neighborhood to a school depends on the grade and is explicitly given by `assignment_cost`, a three-dimensional array with shape [8, 1,100, 1,100] whose entries are integer per-student travel costs. The decision for every grade-neighborhood-school combination is a nonnegative integer number of students. Every neighborhood's students must be fully placed and no school may exceed its per-grade capacity.

Choose the student assignment for every grade to minimize total travel cost. Report the minimum total travel cost and the complete assignment.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

- `grades`: array[8] of distinct strings.
- `neighborhoods`: array[1100] of distinct strings.
- `schools`: array[1100] of distinct strings.
- `students_per_neighborhood_grade`: positive number scalar.
- `school_capacity_per_grade`: positive number scalar.
- `assignment_cost`: array[8][1100][1100] of integer per-student costs; the axes are grade, neighborhood, and school in the listed orders.
