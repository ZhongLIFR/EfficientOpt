# Degenerate zero-set CQ audit

A calibration model encodes exact fixed values through squared inequalities.

Mathematical model:

Minimize sum_i 0.5*w_i*(x_i-p_i)^2 subject to (x_i-a_i)^2 <= 0. Each constraint forces x_i=a_i but has zero gradient at feasibility, so standard KKT constraint qualification fails; the safe formulation first reduces the degenerate feasible set.

Ordinary reference implementation: search while treating failed-CQ constraints as generic nonlinear constraints.

Technique implementation: detect CQ failure and reduce to fixed variables.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
