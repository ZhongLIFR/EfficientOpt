import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """Technique formulation: continuous min-cost arc flow.

    Single-source single-sink integral demand (balance: +D at source, -D at
    sink, 0 elsewhere).  The network matrix is TU with integral RHS, so the
    LP relaxation is already integral: solving the continuous flow gives the
    integer optimum.
    """
    n = len(instance["nodes"])
    arcs = instance["arcs"]
    balance = instance["balance"]
    m = gp.Model("continuous_arc_flow_relaxation")
    f = m.addVars(len(arcs), lb=0.0, name="flow")
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
