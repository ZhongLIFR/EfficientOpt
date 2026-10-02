# Queue-rate DCP calibration

A queueing model calibrates service-rate log variables using a convex exponential term.

Mathematical model:

Minimize sum_i exp(x_i) - a_i*x_i subject to lower <= x_i <= upper. Convexity and DCP recognition give stationarity exp(x_i)=a_i, hence x_i=clip(log(a_i), lower, upper).

Ordinary reference implementation: treat each term as a black-box convex function.

Technique implementation: verify convexity and apply DCP stationarity.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
