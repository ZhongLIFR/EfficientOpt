# Price-response parameter batch

A price-response model solves many nearby resource totals with unchanged curvature.

Mathematical model:

For many budgets B_s solve min_x 0.5*sum_i d_i*(x_i-p_i)^2 subject to sum_i x_i=B_s. Sensitivity analysis reuses sum_i 1/d_i and gives lambda_s=(sum_i p_i-B_s)/sum_i 1/d_i.

Ordinary reference implementation: batch of dense KKT systems.

Technique implementation: single sensitivity expression reused for the batch.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
