import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T19_18 ordinary (naive): one binary assignment per (language, covering translator).

    For every language, designate exactly one hired translator who speaks it
    (assign[l,i] binary <= hire[i]), minimize total hiring cost.
    """
    L = instance["num_languages"]
    trans = instance["translators"]
    m = gp.Model("t19_18_naive_language_assignment")
    hire = m.addVars(len(trans), vtype=GRB.BINARY, name="hire")
    assign = {}
    for i, row in enumerate(trans):
        for l in row["languages"]:
            assign[l, i] = m.addVar(vtype=GRB.BINARY, name=f"assign[{l},{i}]")
            m.addConstr(assign[l, i] <= hire[i], name=f"link[{l},{i}]")
    for l in range(L):
        coverers = [i for i, row in enumerate(trans) if l in row["languages"]]
        m.addConstr(quicksum(assign[l, i] for i in coverers) == 1, name=f"cover[{l}]")
    m.setObjective(quicksum(row["cost"] * hire[i] for i, row in enumerate(trans)), GRB.MINIMIZE)
    return m
