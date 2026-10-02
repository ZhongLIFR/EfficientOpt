"""Fixed-runner two-vehicle arc formulation for T21 routing blocks."""

from __future__ import annotations

import gurobipy as gp


def build_model(instance):
    model = gp.Model("t21_two_vehicle_arc_formulation")
    objective = gp.LinExpr()
    for b, block in enumerate(instance["blocks"]):
        cost = block["cost"]
        customers = list(range(1, 11))
        nodes = list(range(11))
        arc = model.addVars(2, nodes, nodes, vtype=gp.GRB.BINARY, name=f"arc[{b}]")
        visit = model.addVars(2, customers, vtype=gp.GRB.BINARY, name=f"visit[{b}]")
        order = model.addVars(2, customers, lb=1.0, ub=5.0, name=f"order[{b}]")
        for v in range(2):
            for i in nodes:
                model.addConstr(arc[v, i, i] == 0, name=f"no_loop[{b},{v},{i}]")
            model.addConstr(gp.quicksum(arc[v, 0, j] for j in customers) == 1, name=f"depart[{b},{v}]")
            model.addConstr(gp.quicksum(arc[v, i, 0] for i in customers) == 1, name=f"return[{b},{v}]")
            for i in customers:
                model.addConstr(gp.quicksum(arc[v, i, j] for j in nodes if j != i) == visit[v, i], name=f"out[{b},{v},{i}]")
                model.addConstr(gp.quicksum(arc[v, j, i] for j in nodes if j != i) == visit[v, i], name=f"in[{b},{v},{i}]")
            model.addConstr(gp.quicksum(visit[v, i] for i in customers) == 5, name=f"five_customers[{b},{v}]")
            for i in customers:
                for j in customers:
                    if i != j:
                        model.addConstr(order[v, j] >= order[v, i] + 1 - 5 * (1 - arc[v, i, j]), name=f"mtz[{b},{v},{i},{j}]")
        for i in customers:
            model.addConstr(gp.quicksum(visit[v, i] for v in range(2)) == 1, name=f"assign[{b},{i}]")
        for v in range(2):
            objective += gp.quicksum(float(cost[i][j]) * arc[v, i, j] for i in nodes for j in nodes if i != j)
    model.setObjective(objective, gp.GRB.MINIMIZE)
    return model
