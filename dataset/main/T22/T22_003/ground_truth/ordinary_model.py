"""Compact robust counterpart and explicit-scenario formulation for T22."""

from __future__ import annotations

import gurobipy as gp


def build_compact(instance):
    model = gp.Model("t22_compact_robust")
    for gidx, g in enumerate(instance["groups"]):
        n = len(g["profit"])
        gamma = int(g.get("gamma", 2))
        x = [model.addVar(lb=0, ub=float(g["upper_bounds"][i]), obj=float(g["profit"][i])) for i in range(n)]
        z = model.addVar(lb=0)
        w = [model.addVar(lb=0) for _ in range(n)]
        model.addConstr(gp.quicksum(float(g["nominal"][i]) * x[i] for i in range(n)) + gamma * z + gp.quicksum(w) <= float(g["capacity"]))
        for i in range(n):
            model.addConstr(w[i] >= float(g["deviation"][i]) * x[i] - z)
    model.ModelSense = gp.GRB.MAXIMIZE
    return model


def build_model(instance):
    model = gp.Model("t22_explicit_scenarios")
    for gidx, g in enumerate(instance["groups"]):
        n = len(g["profit"])
        x = [model.addVar(lb=0, ub=float(g["upper_bounds"][i]), obj=float(g["profit"][i])) for i in range(n)]
        nominal = gp.quicksum(float(g["nominal"][i]) * x[i] for i in range(n))
        for scenario in g["scenarios"]:
            lhs = nominal + gp.quicksum(float(g["deviation"][i]) * x[i] for i in scenario)
            model.addConstr(lhs <= float(g["capacity"]))
    model.ModelSense = gp.GRB.MAXIMIZE
    return model
