from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def _shared_blocks_dual(d: dict) -> gp.Model:
    blocks = d["blocks"]
    m = gp.Model("T13_shared_resource_dual")
    lam = m.addVar(lb=0.0, name="resource_price")
    upper = m.addVars(len(blocks), lb=-GRB.INFINITY, name="block_upper_value")
    for i, block in enumerate(blocks):
        for mode in block["modes"]:
            m.addConstr(upper[i] + float(mode["resource"]) * lam >= float(mode["value"]), name=f"mode_bound[{i}]")
    m.setObjective(float(d["resource_capacity"]) * lam + gp.quicksum(upper[i] for i in range(len(blocks))), GRB.MINIMIZE)
    return m


def _routing_dual(d: dict) -> gp.Model:
    n = len(d["commodities"])
    m = gp.Model("T13_shared_backbone_reduced")
    shared = m.addVars(n, lb=0.0, name="shared_flow")
    for i in range(n):
        m.addConstr(shared[i] <= float(d["demand"][i]), name=f"shared_capacity[{i}]")
    saving = [float(d["bypass_route_cost"][i]) - float(d["shared_route_cost"][i]) for i in range(n)]
    m.setObjective(
        gp.quicksum(float(d["bypass_route_cost"][i]) * float(d["demand"][i]) - float(saving[i]) * shared[i] for i in range(n)),
        GRB.MINIMIZE,
    )
    m.addConstr(gp.quicksum(shared[i] for i in range(n)) <= float(d["shared_capacity"]), name="backbone_capacity")
    return m


def build_model(instance: dict) -> gp.Model:
    if "blocks" in instance:
        return _shared_blocks_dual(instance)
    if "commodities" in instance:
        return _routing_dual(instance)
    raise ValueError("unrecognized T13 instance schema")
