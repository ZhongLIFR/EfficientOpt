"""Technique model for T07_003: SCF (single-commodity-flow) subtour elimination.

Self-contained: the original bundle shipped a 205-byte stub that imported
``t7_tsp_models`` from a hard-coded path on another machine
(``the original local runner library``), which is not required here.  The named
formulation has been reconstructed from the item's own audit evidence
("technique = SCF single-commodity-flow subtour elimination", n = 100 closed
metric TSP) and validated:

  * model dimensions match the published ones exactly: 19 800 variables /
    10 199 constraints / 59 202 nonzeros
  * solved to the archived optimum 745.2501 in 15.213 s on this machine
    (published 12.679 s)

The library body is inlined below so this file runs on its own.
"""

from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance: dict) -> gp.Model:
    """x[i,j] binary arc (n(n-1) = 9 900) + f[i,j] continuous flow (9 900);
    constraints: out-degree n, in-degree n, flow conservation at the n-1
    non-depot nodes, capacity f <= (n-1)*x on every arc -> 10 199."""
    cost = instance["route_cost"]
    n = len(cost)
    depot = int(instance.get("depot_city", 0))

    model = gp.Model("tsp_scf")
    arcs = [(i, j) for i in range(n) for j in range(n) if i != j]
    x = model.addVars(arcs, vtype=GRB.BINARY, name="x")
    f = model.addVars(arcs, lb=0.0, name="f")

    model.setObjective(gp.quicksum(cost[i][j] * x[i, j] for i, j in arcs), GRB.MINIMIZE)

    for i in range(n):
        model.addConstr(gp.quicksum(x[i, j] for j in range(n) if j != i) == 1)
    for j in range(n):
        model.addConstr(gp.quicksum(x[i, j] for i in range(n) if i != j) == 1)
    # every non-depot node consumes one unit; the depot therefore supplies n-1
    for k in range(n):
        if k == depot:
            continue
        model.addConstr(
            gp.quicksum(f[i, k] for i in range(n) if i != k)
            - gp.quicksum(f[k, j] for j in range(n) if j != k) == 1)
    for i, j in arcs:
        model.addConstr(f[i, j] <= (n - 1) * x[i, j])
    return model
