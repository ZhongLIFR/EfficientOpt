# Regional consensus load-adjustment benchmark

A grid operator coordinates load-adjustment plans for 120 regions over 24 time periods. Region `k` has a preferred adjustment `p[k,h]` and a positive discomfort weight `q[k,h]` in period `h`. The operator requires all regions to agree on the same final adjustment value in each period, but each region wants the agreed value to stay close to its own preference.

For each region `k` and period `h`, choose a local variable `x[k,h]`. The objective is

`sum_k sum_h 0.5 * q[k,h] * (x[k,h] - p[k,h])^2`.

The consensus requirement is `x[0,h] = x[1,h] = ... = x[119,h]` for every period `h`. The fixed instance data are generated exactly by the formulas in `instance.json`; do not use random data.

Return the minimum objective value and the consensus adjustment profile.

This problem is intentionally written so that a generic centralized formulation creates one dense equality-constrained quadratic system per period. A modeling-aware solution should expose the separable regional quadratic objectives plus the consensus constraints and solve them by an augmented-Lagrangian / ADMM-style consensus decomposition with closed-form local updates.
