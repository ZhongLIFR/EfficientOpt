import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T16_10 ordinary: continuous two-stage generation-investment LP.

    Build capacity y_j in [0, cap_ub_j] per technology before scenarios;
    per-scenario dispatch x_sj <= avail_sj * y_j, shortage u_s covers load.
    All decisions continuous (no integrality in the statement).
    """
    T = len(instance["technologies"])
    S = len(instance["scenarios"])
    inv = [float(v) for v in instance["investment_cost"]]
    ub = [float(v) for v in instance["capacity_upper_bound"]]
    demand = [float(v) for v in instance["demand"]]
    avail = instance["availability"]     # S x T
    op = instance["operating_cost"]      # S x T
    pnl = float(instance["shortage_penalty"])
    prob = 1.0 / S

    m = gp.Model("t16_10_invest_lp")
    y = m.addVars(T, lb=0.0, ub=ub, name="build")
    x = m.addVars(S, T, lb=0.0, name="dispatch")
    u = m.addVars(S, lb=0.0, name="shortage")

    for s in range(S):
        m.addConstr(quicksum(x[s, t] for t in range(T)) + u[s] >= demand[s], name=f"dmd_{s}")
        for t in range(T):
            m.addConstr(x[s, t] <= float(avail[s][t]) * y[t], name=f"cap_{s}_{t}")

    obj = quicksum(inv[t] * y[t] for t in range(T))
    obj += prob * quicksum(pnl * u[s] for s in range(S))
    obj += prob * quicksum(float(op[s][t]) * x[s, t] for s in range(S) for t in range(T))
    m.setObjective(obj, GRB.MINIMIZE)
    return m
