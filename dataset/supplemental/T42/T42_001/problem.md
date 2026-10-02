# Parametric frontier batch

A frontier analysis repeatedly changes the right-hand-side budget of the same convex model.

Mathematical model:

For many budgets B_s solve min_x 0.5*sum_i d_i*(x_i-p_i)^2 subject to sum_i x_i=B_s. Sensitivity analysis reuses sum_i 1/d_i and gives lambda_s=(sum_i p_i-B_s)/sum_i 1/d_i.

Ordinary reference implementation: independent dense solve for each parameter.

Technique implementation: precompute parametric KKT sensitivity.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
