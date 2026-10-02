import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    model = gp.Model("t35_staffing_with_slacks")
    records = instance["districts"]
    n = len(records)
    x = model.addVars(n, vtype=GRB.INTEGER, lb=0, name="x")
    y = model.addVars(n, vtype=GRB.INTEGER, lb=0, name="y")
    z = model.addVars(n, vtype=GRB.INTEGER, lb=0, name="z")
    w = model.addVars(n, vtype=GRB.INTEGER, lb=0, name="w")
    s1 = model.addVars(n, vtype=GRB.INTEGER, lb=0, name="s1")
    s2 = model.addVars(n, vtype=GRB.INTEGER, lb=0, name="s2")
    s3 = model.addVars(n, vtype=GRB.INTEGER, lb=0, name="s3")
    s4 = model.addVars(n, vtype=GRB.INTEGER, lb=0, name="s4")
    model.setObjective(gp.quicksum(r["cost_x"]*x[i] + r["cost_y"]*y[i] + r["cost_z"]*z[i] + r["cost_w"]*w[i] for i, r in enumerate(records)), GRB.MINIMIZE)
    model.addConstrs((x[i] + y[i] - s1[i] == records[i]["minimum_xy"] for i in range(n)))
    model.addConstrs((y[i] + z[i] - s2[i] == records[i]["minimum_yz"] for i in range(n)))
    model.addConstrs((z[i] - w[i] + s3[i] == records[i]["maximum_z_minus_w"] for i in range(n)))
    model.addConstrs((x[i] - w[i] + s4[i] == records[i]["maximum_x_minus_w"] for i in range(n)))
    return model
