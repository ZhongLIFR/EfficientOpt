from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def _shared_blocks_primal(d: dict) -> gp.Model:
    blocks = d["blocks"]
    m = gp.Model("T13_shared_resource_primal")
    x = {(i, k): m.addVar(lb=0.0, name=f"intensity[{i},{k}]") for i, block in enumerate(blocks) for k in range(len(block["modes"]))}
    for i, block in enumerate(blocks):
        m.addConstr(gp.quicksum(x[i, k] for k in range(len(block["modes"]))) == 1.0, name=f"mix[{i}]")
    m.addConstr(gp.quicksum(float(mode["resource"]) * x[i, k] for i, block in enumerate(blocks) for k, mode in enumerate(block["modes"])) <= float(d["resource_capacity"]), name="resource_capacity")
    m.setObjective(gp.quicksum(float(mode["value"]) * x[i, k] for i, block in enumerate(blocks) for k, mode in enumerate(block["modes"])), GRB.MAXIMIZE)
    return m


def _routing_primal(d: dict) -> gp.Model:
    n = len(d["commodities"])
    m = gp.Model("T13_shared_backbone_primal")
    shared = m.addVars(n, lb=0.0, name="shared_flow")
    bypass = m.addVars(n, lb=0.0, name="bypass_flow")
    for i in range(n):
        m.addConstr(shared[i] + bypass[i] == float(d["demand"][i]), name=f"demand[{i}]")
    m.addConstr(gp.quicksum(shared[i] for i in range(n)) <= float(d["shared_capacity"]), name="backbone_capacity")
    m.setObjective(gp.quicksum(float(d["shared_route_cost"][i]) * shared[i] + float(d["bypass_route_cost"][i]) * bypass[i] for i in range(n)), GRB.MINIMIZE)
    return m


def build_model(instance: dict) -> gp.Model:
    if "blocks" in instance:
        return _shared_blocks_primal(instance)
    if "commodities" in instance:
        return _routing_primal(instance)
    raise ValueError("unrecognized T13 instance schema")
