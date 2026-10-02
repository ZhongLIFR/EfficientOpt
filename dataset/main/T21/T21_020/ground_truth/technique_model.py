from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    n = int(instance["node_count"])
    costs = instance["cost"]
    nodes = range(n)
    depot = 0
    arcs = [(i, j) for i in nodes for j in nodes if i != j]
    flow_arcs = [(i, j) for i, j in arcs if j != depot]

    model = gp.Model("directed_tsp_scf")
    travel = model.addVars(arcs, vtype=GRB.BINARY, name="travel")
    flow = model.addVars(flow_arcs, lb=0.0, ub=n - 1, name="flow")
    model.addConstrs(
        (gp.quicksum(travel[i, j] for j in nodes if j != i) == 1 for i in nodes),
        name="out_degree",
    )
    model.addConstrs(
        (gp.quicksum(travel[j, i] for j in nodes if j != i) == 1 for i in nodes),
        name="in_degree",
    )
    model.addConstrs(
        (gp.quicksum(flow[i, k] for i in nodes if (i, k) in flow)
         - gp.quicksum(flow[k, j] for j in nodes if (k, j) in flow) == 1
         for k in nodes if k != depot),
        name="flow_balance",
    )

    model.addConstr(
        gp.quicksum(flow[depot, j] for j in nodes if (depot, j) in flow) == n - 1,
        name="depot_supply",
    )

    model.addConstrs(
        (flow[i, j] <= (n - 1) * travel[i, j] for i, j in flow_arcs),
        name="flow_link",
    )
    model.setObjective(
        gp.quicksum(float(costs[i][j]) * travel[i, j] for i, j in arcs),
        GRB.MINIMIZE,
    )
    return model
