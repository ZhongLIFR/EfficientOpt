import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T20_15 ordinary (naive): expanded future-implication model.

    operate[i,t] binary; opened[i,t] binary = mine i open in year t.  The
    no-reopening rule is expanded into every transitive open-state implication
    opened[i,t] >= opened[i,tau] for t < tau, plus operate <= opened.  This is
    O(M*Y^2/2) rows. Royalty is paid per open year; value is earned in operating
    years; a per-year cap limits simultaneous operation.
    """
    M = int(instance["mines"])
    Y = int(instance["years"])
    cap = int(instance["max_operating"])
    royalty = [float(v) for v in instance["royalty"]]
    value = [[float(v) for v in row] for row in instance["value"]]
    m = gp.Model("t20_15_naive_implication")
    op = m.addVars(M, Y, vtype=GRB.BINARY, name="operate")
    opn = m.addVars(M, Y, vtype=GRB.BINARY, name="opened")
    for t in range(Y):
        m.addConstr(quicksum(op[i, t] for i in range(M)) <= cap, name=f"cap_{t}")
    for i in range(M):
        for t in range(Y):
            m.addConstr(op[i, t] <= opn[i, t], name=f"link_{i}_{t}")
            for tau in range(t + 1, Y):
                m.addConstr(opn[i, t] >= opn[i, tau], name=f"open_{i}_{t}_{tau}")
    obj = gp.LinExpr()
    for i in range(M):
        for t in range(Y):
            obj += value[i][t] * op[i, t] - royalty[i] * opn[i, t]
    m.setObjective(obj, GRB.MAXIMIZE)
    return m
