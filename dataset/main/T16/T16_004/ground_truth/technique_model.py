import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T16_10 technique: static dual-cut master of the same continuous LP.

    For fixed built capacity y the scenario recourse LP dual (pi in [0,pnl],
    z_j duals max(0, pi - op_sj)) gives
       R_s(y) = max_{pi in [0,p]} [ d*pi - sum_j avail_sj*y_j*max(0, pi-op_sj) ],
    attained at Pi_s = {0, pnl} union {op_sj in (0,pnl)}.  With continuous y
    the cut master
       min sum_j inv_j y_j + sum_s prob_s t_s
       s.t. t_s >= d*pi - sum_j avail_sj y_j (pi - op_sj)_+   for all pi in Pi_s
    is an exact deterministic-equivalent LP (identical optimum to ordinary).
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

    m = gp.Model("t16_10_cut_master_lp")
    y = m.addVars(T, lb=0.0, ub=ub, name="build")
    t = m.addVars(S, lb=0.0, name="recourse")

    for s in range(S):
        pis = {0.0, pnl}
        for j in range(T):
            cj = float(op[s][j])
            if 0.0 < cj < pnl:
                pis.add(cj)
        for pi in pis:
            m.addConstr(
                t[s] >= demand[s] * pi - quicksum(
                    float(avail[s][j]) * max(0.0, pi - float(op[s][j])) * y[j]
                    for j in range(T)),
                name=f"cut[{s}]",
            )

    m.setObjective(quicksum(inv[j] * y[j] for j in range(T))
                   + prob * quicksum(t[s] for s in range(S)), GRB.MINIMIZE)
    return m
