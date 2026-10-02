# Robust load adjustment cone

A power operator keeps a load-adjustment vector inside a conic uncertainty envelope.

Mathematical model:

Project vector v onto the Euclidean ball ||x||_2 <= R by minimizing 0.5*||x-v||_2^2. The conic formulation is a second-order cone, and the solution is x=v if feasible else x=R*v/||v||.

Ordinary reference implementation: iterative nonlinear norm search.

Technique implementation: recognize the SOC ball projection.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
