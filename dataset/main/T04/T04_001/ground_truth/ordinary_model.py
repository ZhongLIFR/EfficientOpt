import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """Ordinary formulation: integer arc-flow model."""
    n = len(instance["nodes"])
    arcs = instance["arcs"]
    balance = instance["balance"]
    m = gp.Model("integer_arc_flow")
    f = m.addVars(len(arcs), lb=0.0, vtype=GRB.INTEGER, name="flow")
    for a, arc in enumerate(arcs):
        f[a].ub = arc["capacity"]
    out = [[] for _ in range(n)]
    inn = [[] for _ in range(n)]
    for a, arc in enumerate(arcs):
        out[arc["tail"]].append(a)
        inn[arc["head"]].append(a)
    for v in range(n):
        m.addConstr(quicksum(f[a] for a in out[v]) - quicksum(f[a] for a in inn[v]) == balance[v], name=f"bal[{v}]")
    m.setObjective(quicksum(arcs[a]["cost"] * f[a] for a in range(len(arcs))), GRB.MINIMIZE)
    return m
