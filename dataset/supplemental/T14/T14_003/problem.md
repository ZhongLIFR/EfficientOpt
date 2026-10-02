# Multisite ridge model consensus

Ninety sites are training the same 20-feature linear prediction vector. Site `k` has a local quadratic approximation for feature `j` with curvature `a[k,j]` and local preferred coefficient `b[k,j]`. The consortium requires all sites to agree on one shared coefficient vector.

For each site `k` and feature `j`, choose a local variable `x[k,j]`. Minimize

`sum_k sum_j 0.5 * a[k,j] * (x[k,j] - b[k,j])^2`

subject to the consensus constraints `x[0,j] = x[1,j] = ... = x[89,j]` for every feature `j`.

The fixed instance is deterministic: `a[k,j] = 1.0 + ((17*k + 13*j) mod 19) / 10` and `b[k,j] = (((37*k + 23*j) mod 101) - 50) / 10`. Do not use random data.

Return the minimum objective value and the final shared coefficient vector.

This benchmark is designed so that a generic centralized model creates a dense equality-constrained quadratic system for each feature. A modeling-aware solution should expose the separable local quadratic objectives plus consensus constraints and use augmented-Lagrangian / ADMM consensus updates.
