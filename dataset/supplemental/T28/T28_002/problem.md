# Production commitment feasibility repair

A factory checks product-period commitments for 150 products over 30 periods. Product `i` in period `t` has demand `demand[i,t]` and base capacity `base[i,t]`. The original hard commitment `base[i,t] >= demand[i,t]` is infeasible. The factory can repair each product-period row using two interpretable slack mechanisms:

- overtime slack `o[i,t]`, bounded by `0 <= o[i,t] <= max_overtime[i,t]`, with penalty 7 per unit;
- unmet-demand slack `s[i,t] >= 0`, with penalty 31 per unit.

The repaired row is `base[i,t] + o[i,t] + s[i,t] >= demand[i,t]`. Minimize total repair penalty.

The fixed instance is deterministic: `demand[i,t] = 900 + ((29*i + 31*t) mod 500)`, `base[i,t] = demand[i,t] - (100 + ((17*i + 13*t) mod 250))`, and `max_overtime[i,t] = 80 + ((19*i + 7*t) mod 160)`.

Return the minimum repair penalty, total overtime used, and total unmet demand.

This benchmark tests whether a modeler uses meaningful feasibility relaxation. A poor approach repeatedly enumerates repair budgets. The intended model uses explicit slack variables with economically meaningful penalties and directly explains which shortage remains after all cheaper overtime is used.
