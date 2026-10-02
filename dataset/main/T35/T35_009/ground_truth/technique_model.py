import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    model = gp.Model("t35_portfolio_eliminate_x")
    records = instance["portfolios"]
    n = len(records)
    y = model.addVars(n, vtype=GRB.INTEGER, lb=[r["min_y"] for r in records], name="y")
    z = model.addVars(n, vtype=GRB.INTEGER, lb=[r["min_z"] for r in records], name="z")
    model.setObjective(gp.quicksum(r["return_x_bps"]*(r["total"]-y[i]-z[i]) + r["return_y_bps"]*y[i] + r["return_z_bps"]*z[i] for i, r in enumerate(records)), GRB.MINIMIZE)
    model.addConstrs((y[i] + z[i] <= records[i]["total"] - records[i]["min_x"] for i in range(n)))
    return model
