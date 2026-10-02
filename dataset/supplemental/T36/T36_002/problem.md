# DCP exponential price calibration

A pricing model calibrates bounded log-intensities with exponential convex loss.

Mathematical model:

Minimize sum_i exp(x_i) - a_i*x_i subject to lower <= x_i <= upper. Convexity and DCP recognition give stationarity exp(x_i)=a_i, hence x_i=clip(log(a_i), lower, upper).

Ordinary reference implementation: univariate black-box convex search.

Technique implementation: recognize DCP exponential objective and use stationarity.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
