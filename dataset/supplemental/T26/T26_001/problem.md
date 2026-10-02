# Complementarity-aware bid clipping

A market platform computes bounded continuous bid adjustments. The natural KKT system has lower-bound and upper-bound complementarity for every bid.

Mathematical model:

Minimize sum_i 0.5*q_i*x_i^2 - a_i*x_i subject to 0 <= x_i <= u_i. The KKT complementarity conditions imply x_i = clip(a_i/q_i, 0, u_i).

Ordinary reference implementation: enumerate lower/free/upper active statuses.

Technique implementation: solve KKT complementarity by clipping each coordinate.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
