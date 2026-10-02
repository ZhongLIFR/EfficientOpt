# Simplex proximal allocation

An ad allocator projects unconstrained scores onto a fixed total nonnegative budget.

Mathematical model:

Project v onto the simplex {x>=0, sum_i x_i=B}: minimize 0.5*||x-v||_2^2. The proximal projection has x_i=max(v_i-theta,0), where theta is found by a sorted threshold.

Ordinary reference implementation: generic dual bisection projection.

Technique implementation: simplex proximal operator with sorted threshold.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
