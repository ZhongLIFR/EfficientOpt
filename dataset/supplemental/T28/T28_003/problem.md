# Cold-chain service-level repair

A cold-chain distributor checks a fixed allocation of perishable products across 96 delivery zones and 30 products. Each zone-product pair has a required service quantity `required[z,p]` and the current allocation can cover only `available[z,p]`. Treating all service requirements as hard constraints makes the fixed plan infeasible.

The distributor allows service shortfall, but each shortfall must be explicitly measured. Critical products have penalty 140 per missing unit, and standard products have penalty 55 per missing unit. Introduce nonnegative slack `s[z,p]` so that `available[z,p] + s[z,p] >= required[z,p]`; minimize the total class-weighted service shortfall penalty.

The fixed instance is deterministic: `required[z,p] = 650 + ((41*z + 29*p) mod 500)`, `available[z,p] = max(0, required[z,p] - 3 * (70 + ((17*z + 31*p) mod 260)))`, and a pair is critical if `(z + 2*p) mod 5 == 0`.

Return the minimum total penalty and a summary separating critical and standard shortfall.

This benchmark targets soft service constraints: the useful model is not another hard infeasible model, but a feasibility-relaxation model with interpretable shortfall variables and reasonable penalties.
