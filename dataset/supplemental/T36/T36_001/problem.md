# Convex demand intensity fitting

A demand system fits many bounded convex intensity variables.

Mathematical model:

Minimize sum_i exp(x_i) - a_i*x_i subject to lower <= x_i <= upper. Convexity and DCP recognition give stationarity exp(x_i)=a_i, hence x_i=clip(log(a_i), lower, upper).

Ordinary reference implementation: generic ternary search for each variable.

Technique implementation: DCP atom recognition with closed-form clipping.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
