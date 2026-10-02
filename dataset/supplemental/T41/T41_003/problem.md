# Shared resource equilibrium VI

Agents choose resource quantities with a shared congestion externality.

Mathematical model:

Solve the monotone affine VI F_i(q)=h_i*q_i + beta*sum_j q_j - a_i = 0 over the positive orthant. The generated instances have positive equilibrium, so the VI reduces to an aggregate closed-form equation.

Ordinary reference implementation: generic dense linear complementarity-style solve.

Technique implementation: closed-form positive equilibrium from VI optimality.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
