# Second-order cone projection batch

A conic optimizer receives 1,200 independent second-order cone blocks. For each block `k`, the current point is `(t[k], y[k,0], ..., y[k,7])`. The task is to project every block onto the second-order cone

`{(u,v): ||v||_2 <= u}`.

Minimize the total squared Euclidean projection distance over all cone blocks and report the projected objective.

The fixed instance is deterministic: `t[k] = ((37*k) mod 100) / 10 - 2` and `y[k,i] = (((17*k + 11*i) mod 101) - 50) / 25`.

This benchmark targets interior-point-friendly conic modeling. A poor formulation expands the norm and handles each cone through generic nonlinear line search. The intended formulation keeps the second-order cone structure and uses the standard cone projection formula.
