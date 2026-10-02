import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T19_18 technique: compact set-cover (one hire variable, one row per language)."""
    L = instance["num_languages"]
    trans = instance["translators"]
    covering = [[] for _ in range(L)]
    for i, row in enumerate(trans):
        for l in row["languages"]:
            covering[l].append(i)
    m = gp.Model("t19_18_compact_set_cover")
    hire = m.addVars(len(trans), vtype=GRB.BINARY, name="hire")
    for l in range(L):
        m.addConstr(quicksum(hire[i] for i in covering[l]) >= 1, name=f"cover[{l}]")
    m.setObjective(quicksum(row["cost"] * hire[i] for i, row in enumerate(trans)), GRB.MINIMIZE)
    return m
