import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T20_15 technique: compact monotone-prefix model.

    Same semantics expressed with opened[i,t] monotone non-increasing in t
    (once closed, never reopened) plus operate[i,t] <= opened[i,t]: only
    O(M*Y) rows instead of O(M*Y^2/2). Exact same feasible region in
    (operate, opened).
    """
    M = int(instance["mines"])
    Y = int(instance["years"])
    cap = int(instance["max_operating"])
    royalty = [float(v) for v in instance["royalty"]]
    value = [[float(v) for v in row] for row in instance["value"]]
    m = gp.Model("t20_15_compact_prefix")
    op = m.addVars(M, Y, vtype=GRB.BINARY, name="operate")
    opn = m.addVars(M, Y, vtype=GRB.BINARY, name="opened")
    for t in range(Y):
        m.addConstr(quicksum(op[i, t] for i in range(M)) <= cap, name=f"cap_{t}")
    for i in range(M):
        for t in range(Y):
            m.addConstr(op[i, t] <= opn[i, t], name=f"link_{i}_{t}")
        for t in range(Y - 1):
            m.addConstr(opn[i, t] >= opn[i, t + 1], name=f"mono_{i}_{t}")
    obj = gp.LinExpr()
    for i in range(M):
        for t in range(Y):
            obj += value[i][t] * op[i, t] - royalty[i] * opn[i, t]
    m.setObjective(obj, GRB.MAXIMIZE)
    return m
