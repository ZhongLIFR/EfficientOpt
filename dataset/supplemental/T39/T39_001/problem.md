# Normal cone robust location

A robust one-dimensional facility location task uses nonsmooth absolute losses.

Mathematical model:

Minimize f(x)=sum_i w_i |x-a_i|. The subgradient optimality condition 0 in partial f(x) is satisfied at a weighted median.

Ordinary reference implementation: dense candidate enumeration.

Technique implementation: subgradient inclusion and weighted-median extraction.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
