from __future__ import annotations

import json
from pathlib import Path

import gurobipy as gp
from gurobipy import GRB


def load_instance() -> dict:
    return json.loads((Path(__file__).resolve().parents[1] / "public" / "instance.json").read_text())


def build_model(instance: dict) -> gp.Model:
    products = range(len(instance["products"]))
    periods = range(len(instance["periods"]))
    model = gp.Model(instance["problem_id"] + "_ordinary")
    production = model.addVars(products, periods, lb=0, ub={(p, t): instance["maximum_batch"][p][t] for p in products for t in periods}, name="production")
    active = model.addVars(products, periods, vtype=GRB.BINARY, name="active")
    model.addConstrs((production[p, t] >= instance["minimum_batch"][p][t] * active[p, t] for p in products for t in periods), name="minimum_batch")
    model.addConstrs((production[p, t] <= instance["maximum_batch"][p][t] * active[p, t] for p in products for t in periods), name="maximum_batch")
    inventory = model.addVars(products, periods, lb=0, name="inventory")
    model.addConstrs((production[p, 0] - inventory[p, 0] == instance["demand"][p][0] for p in products), name="initial_balance")
    model.addConstrs((inventory[p, t - 1] + production[p, t] - inventory[p, t] == instance["demand"][p][t] for p in products for t in range(1, len(instance["periods"]))), name="balance")
    model.addConstrs((gp.quicksum(production[p, t] for p in products) <= instance["line_capacity"][t] for t in periods), name="line_capacity")
    model.setObjective(gp.quicksum(instance["baling_cost"][p][t] * production[p, t] + instance["holding_cost"][p][t] * inventory[p, t] for p in products for t in periods), GRB.MINIMIZE)
    return model


if __name__ == "__main__":
    model = build_model(load_instance())
    model.Params.OutputFlag = 0
    model.optimize()
    print(json.dumps({"status": int(model.Status), "objective": model.ObjVal if model.SolCount else None, "solver_s": model.Runtime}, indent=2))
