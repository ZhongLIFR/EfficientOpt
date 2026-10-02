import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    model = gp.Model("t35_portfolio_full")
    records = instance["portfolios"]
    n = len(records)
    x = model.addVars(n, vtype=GRB.INTEGER, lb=[r["min_x"] for r in records], name="x")
    y = model.addVars(n, vtype=GRB.INTEGER, lb=[r["min_y"] for r in records], name="y")
    z = model.addVars(n, vtype=GRB.INTEGER, lb=[r["min_z"] for r in records], name="z")
    model.setObjective(gp.quicksum(r["return_x_bps"]*x[i] + r["return_y_bps"]*y[i] + r["return_z_bps"]*z[i] for i, r in enumerate(records)), GRB.MINIMIZE)
    model.addConstrs((x[i] + y[i] + z[i] == records[i]["total"] for i in range(n)))
    return model
