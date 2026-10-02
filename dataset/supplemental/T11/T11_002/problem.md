# Second-order cone portfolio radius projection

A risk desk projects a high-dimensional exposure vector onto a Euclidean risk-radius constraint.

Mathematical model:

Project vector v onto the Euclidean ball ||x||_2 <= R by minimizing 0.5*||x-v||_2^2. The conic formulation is a second-order cone, and the solution is x=v if feasible else x=R*v/||v||.

Ordinary reference implementation: generic Lagrange multiplier bisection.

Technique implementation: direct SOC projection formula.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
