# Scenario newsvendor retail order

A retailer solves independent stochastic order quantities over many demand scenarios.

Mathematical model:

For each product choose integer order q to minimize the average scenario cost E[h(q-D)_+ + p(D-q)_+]. Scenario decomposition gives the newsvendor quantile q at p/(p+h).

Ordinary reference implementation: scan every order level against every scenario.

Technique implementation: decompose by product and use scenario quantiles.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
