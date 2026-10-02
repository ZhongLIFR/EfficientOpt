import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T15_12 re-authored ordinary (naive): explicit all-pairs implications.

    Same problem, same feasible integer region and same optimum as the compact
    model, but the per-block lane persistence is written for EVERY ordered
    period pair:

        open[b,s,d,t] >= use[b,s,d,tau]     for all tau >= t   (O(L*P^2/2) rows)
    """
    B = int(instance["blocks"]); S = int(instance["sources"])
    D = int(instance["sinks"]); P = int(instance["periods"])
    K = int(instance["max_open_per_period"])
    supply = [[float(v) for v in row] for row in instance["supply"]]
    demand = [[[float(v) for v in row] for row in blk] for blk in instance["demand"]]
    cost = [[[float(v) for v in row] for row in blk] for blk in instance["cost"]]
    fixed = [[[float(v) for v in row] for row in blk] for blk in instance["fixed"]]
    cap = [[[float(v) for v in row] for row in blk] for blk in instance["capacity"]]

    m = gp.Model("t15_reauth_naive_allpairs")
    ship = m.addVars(B, S, D, P, lb=0.0, name="ship")
    use = m.addVars(B, S, D, P, vtype=GRB.BINARY, name="use")
    open_ = m.addVars(B, S, D, P, vtype=GRB.BINARY, name="open")

    for b in range(B):
        for t in range(P):
            m.addConstr(quicksum(use[b, s, d, t] for s in range(S) for d in range(D)) <= K,
                        name=f"cap[{b},{t}]")
        for s in range(S):
            for t in range(P):
                m.addConstr(quicksum(ship[b, s, d, t] for d in range(D)) <= supply[b][s],
                            name=f"supply[{b},{s},{t}]")
        for d in range(D):
            for t in range(P):
                m.addConstr(quicksum(ship[b, s, d, t] for s in range(S)) == demand[b][d][t],
                            name=f"demand[{b},{d},{t}]")
        for s in range(S):
            for d in range(D):
                for t in range(P):
                    m.addConstr(ship[b, s, d, t] <= cap[b][s][d] * use[b, s, d, t],
                                name=f"shipif[{b},{s},{d},{t}]")
                    m.addConstr(use[b, s, d, t] <= open_[b, s, d, t],
                                name=f"useif[{b},{s},{d},{t}]")
                    for tau in range(t + 1, P):
                        m.addConstr(open_[b, s, d, t] >= use[b, s, d, tau],
                                    name=f"persist[{b},{s},{d},{t},{tau}]")

    m.setObjective(quicksum(cost[b][s][d] * ship[b, s, d, t]
                            for b in range(B) for s in range(S) for d in range(D) for t in range(P))
                   + quicksum(fixed[b][s][d] * open_[b, s, d, t]
                              for b in range(B) for s in range(S) for d in range(D) for t in range(P)),
                   GRB.MINIMIZE)
    return m
