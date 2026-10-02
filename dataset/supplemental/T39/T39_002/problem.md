# Subgradient staffing target

A staffing planner chooses a target level under weighted absolute deviation.

Mathematical model:

Minimize f(x)=sum_i w_i |x-a_i|. The subgradient optimality condition 0 in partial f(x) is satisfied at a weighted median.

Ordinary reference implementation: all-candidate absolute loss scan.

Technique implementation: normal-cone/subgradient median condition.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
