# Weighted median service location

A service hub chooses one scalar location to minimize weighted absolute travel deviations.

Mathematical model:

Minimize f(x)=sum_i w_i |x-a_i|. The subgradient optimality condition 0 in partial f(x) is satisfied at a weighted median.

Ordinary reference implementation: evaluate every candidate against every scenario.

Technique implementation: use subgradient sign balance to find the weighted median.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
