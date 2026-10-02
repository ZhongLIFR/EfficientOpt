# Block-diagonal microgrid balancing QP

Ninety independent microgrids each plan generation across 8 periods. Microgrid `g` has preferred generation `p[g,t]` and diagonal quadratic deviation cost weight `d[g,t]`. Each microgrid has its own energy balance requirement `sum_t x[g,t] = D[g]`.

Minimize

`sum_g sum_t 0.5 * d[g,t] * (x[g,t] - p[g,t])^2`

subject to `sum_t x[g,t] = D[g]` for every microgrid `g`.

The fixed instance is deterministic: `d[g,t] = 1.0 + ((13*g + 7*t) mod 19) / 10`, `p[g,t] = 3.0 + ((17*g + 23*t) mod 37) / 10`, and `D[g] = 0.85 * sum_t p[g,t]`.

Return the minimum objective value and the generation matrix.

This benchmark targets interior-point-friendly modeling. A poor formulation destroys the block-diagonal KKT structure by forming one dense system. The intended formulation preserves independent microgrid balance blocks, which is exactly the sparse structure an interior-point solver should exploit.
