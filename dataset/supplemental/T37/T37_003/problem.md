# Sparse budget adjustment composite model

A budget planner seeks sparse adjustments around a baseline vector.

Mathematical model:

Minimize 0.5*||x-v||_2^2 + lambda*||x||_1 + 0.5*rho*||x||_2^2. The smooth plus nonsmooth composite form gives the proximal solution x_i = sign(v_i)*max(|v_i|-lambda,0)/(1+rho).

Ordinary reference implementation: coordinate-wise black-box search.

Technique implementation: separate smooth gradient and L1 proximal step.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
