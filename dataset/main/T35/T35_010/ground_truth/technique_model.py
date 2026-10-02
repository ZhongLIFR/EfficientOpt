import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    model = gp.Model("t35_team_eliminate_z")
    records = instance["teams"]
    n = len(records)
    x = model.addVars(n, vtype=GRB.INTEGER, lb=0, name="x")
    y = model.addVars(n, vtype=GRB.INTEGER, lb=0, name="y")
    model.setObjective(gp.quicksum(r["effort_x"]*x[i] + r["effort_y"]*y[i] + r["effort_z"]*(r["total_tasks"]-x[i]-y[i]) for i, r in enumerate(records)), GRB.MINIMIZE)
    model.addConstrs((x[i] + y[i] <= records[i]["total_tasks"] for i in range(n)))
    model.addConstrs((x[i] + y[i] >= records[i]["min_x_plus_y"] for i in range(n)))
    model.addConstrs((x[i] >= records[i]["total_tasks"] - records[i]["max_y_plus_z"] for i in range(n)))
    return model
