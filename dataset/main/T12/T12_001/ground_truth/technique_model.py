import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T12_01 technique (LP relaxation): continuous min-cost railcar flow.

    Node-arc incidence matrix is totally unimodular with integral balance RHS,
    so the LP relaxation is integral and equals the integer optimum.
    """
    n = len(instance["balance"])
    arcs = instance["arcs"]
    bal = instance["balance"]
    m = gp.Model("t12_01_flow_lp")
    f = m.addVars(len(arcs), lb=0.0, name="flow")
    out = [[] for _ in range(n)]
    inn = [[] for _ in range(n)]
    for a, arc in enumerate(arcs):
        out[arc["tail"]].append(a)
        inn[arc["head"]].append(a)
    for v in range(n):
        m.addConstr(quicksum(f[a] for a in out[v]) - quicksum(f[a] for a in inn[v]) == bal[v],
                    name=f"bal[{v}]")
    m.setObjective(quicksum(arcs[a]["cost"] * f[a] for a in range(len(arcs))), GRB.MINIMIZE)
    return m
