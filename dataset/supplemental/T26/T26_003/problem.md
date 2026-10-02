# Storage dispatch complementarity screen

A storage controller chooses bounded charging decisions. Each decision has a lower and upper complementarity condition.

Mathematical model:

Minimize sum_i 0.5*q_i*x_i^2 - a_i*x_i subject to 0 <= x_i <= u_i. The KKT complementarity conditions imply x_i = clip(a_i/q_i, 0, u_i).

Ordinary reference implementation: enumerate all complementarity active patterns.

Technique implementation: recognize separable KKT stationarity and complementarity.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
