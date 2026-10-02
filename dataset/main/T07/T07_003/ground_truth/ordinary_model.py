"""Ordinary model for T07_003: MTZ order (big-M) subtour elimination.

Self-contained: the original bundle shipped a 205-byte stub that imported
``t7_tsp_models`` from a hard-coded path on another machine
(``the original local runner library``), which is not required here.  The named
formulation has been reconstructed from the item's own audit evidence
("ordinary = MTZ order big-M", n = 100 closed metric TSP) and validated:

  * model dimensions match the published ones exactly: 9 999 variables /
    9 902 constraints / 48 906 nonzeros
  * solved to the archived optimum 745.2501 in 1442.836 s on this machine
    (published 392.627 s; same model, different search path)

The library body is inlined below so this file runs on its own.
"""

from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance: dict) -> gp.Model:
    """x[i,j] binary arc (n(n-1) = 9 900) + u[i] continuous order of the n-1
    non-depot nodes (99); constraints: out-degree n, in-degree n and
    (n-1)(n-2) = 9 702 MTZ subtour eliminations -> 9 902."""
    cost = instance["route_cost"]
    n = len(cost)
    depot = int(instance.get("depot_city", 0))

    model = gp.Model("tsp_mtz")
    arcs = [(i, j) for i in range(n) for j in range(n) if i != j]
    x = model.addVars(arcs, vtype=GRB.BINARY, name="x")
    nodes = [i for i in range(n) if i != depot]
    u = model.addVars(nodes, lb=1.0, ub=float(n - 1), name="u")

    model.setObjective(gp.quicksum(cost[i][j] * x[i, j] for i, j in arcs), GRB.MINIMIZE)

    for i in range(n):
        model.addConstr(gp.quicksum(x[i, j] for j in range(n) if j != i) == 1)
    for j in range(n):
        model.addConstr(gp.quicksum(x[i, j] for i in range(n) if i != j) == 1)
    for i in nodes:
        for j in nodes:
            if i != j:
                model.addConstr(u[i] - u[j] + n * x[i, j] <= n - 1)
    return model
