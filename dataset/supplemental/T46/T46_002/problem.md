# Interior-point-friendly diagonal allocation QP

An investment desk chooses nonnegative exposures for 900 assets. Asset `i` has target exposure `p[i]` and diagonal quadratic risk weight `d[i]`. The desk must allocate exactly a fixed total budget `B`.

Minimize

`sum_i 0.5 * d[i] * (x[i] - p[i])^2`

subject to `sum_i x[i] = B` and `x[i] >= 0` for all assets.

The fixed instance is deterministic: `d[i] = 1.0 + (i mod 23) / 10`, `p[i] = 0.1 + ((37*i) mod 101) / 20`, and `B = 0.45 * sum_i p[i]`.

Return the minimum objective value and total allocated exposure.

This benchmark targets interior-point-friendly modeling. A poor formulation expands the diagonal Hessian into repeated dense KKT systems during active-set repair. The intended formulation preserves diagonal Hessian plus nonnegative cone structure and solves the barrier/dual form using a scalar dual search.
