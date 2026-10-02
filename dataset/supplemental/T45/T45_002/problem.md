# Failed-KKT reduction for fixed controls

A control model contains zero-gradient constraints that invalidate direct KKT use.

Mathematical model:

Minimize sum_i 0.5*w_i*(x_i-p_i)^2 subject to (x_i-a_i)^2 <= 0. Each constraint forces x_i=a_i but has zero gradient at feasibility, so standard KKT constraint qualification fails; the safe formulation first reduces the degenerate feasible set.

Ordinary reference implementation: generic KKT-like scan over degenerate constraints.

Technique implementation: constraint-qualification audit followed by direct reduction.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
