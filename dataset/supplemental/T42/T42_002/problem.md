# Budget sweep sensitivity QP

A portfolio team solves the same equality-constrained diagonal QP over many budget levels.

Mathematical model:

For many budgets B_s solve min_x 0.5*sum_i d_i*(x_i-p_i)^2 subject to sum_i x_i=B_s. Sensitivity analysis reuses sum_i 1/d_i and gives lambda_s=(sum_i p_i-B_s)/sum_i 1/d_i.

Ordinary reference implementation: rebuild and solve a dense KKT system for every budget.

Technique implementation: reuse sensitivity formula across all parameters.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
