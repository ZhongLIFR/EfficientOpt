# Exchange-form warehouse allocation

Ninety warehouses plan shipment quantities over 18 periods. Warehouse `k` has a preferred shipment `p[k,h]` in period `h`, and deviation from that preference has quadratic penalty weight `q[k,h]`. In every period, total shipment across all warehouses must exactly match the period demand `D[h]`.

Choose shipment quantities `x[k,h]` to minimize

`sum_k sum_h 0.5 * q[k,h] * (x[k,h] - p[k,h])^2`

subject to `sum_k x[k,h] = D[h]` for every period `h`.

The fixed instance is deterministic: `q[k,h] = 1.0 + ((11*k + 7*h) mod 23) / 10`, `p[k,h] = (83 + ((19*k + 31*h) mod 157)) / 10`, and `D[h] = sum_k p[k,h] + (((17*h) mod 41) - 20) * 0.35`. Do not use random data.

Return the minimum objective value and the shipment matrix.

This benchmark is designed so that a generic centralized formulation can introduce copied shipment variables and dense KKT systems. A modeling-aware solution should recognize the separable local quadratic objectives coupled only by one exchange constraint per period and solve it through an augmented-Lagrangian / ADMM exchange decomposition.
