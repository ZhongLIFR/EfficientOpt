import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T15_12 re-authored technique: compact per-block lane persistence.

    Independent blocks (regions/grades); each block ships from its sources to its
    sinks at minimum cost.  A lane in service stays in service (prefix), a lane
    carries at most its capacity, and at most K lanes per block may be used per
    period.

      open[b,s,d,t] >= open[b,s,d,t+1]        (adjacent prefix, O(L*P) rows)
    """
    B = int(instance["blocks"]); S = int(instance["sources"])
    D = int(instance["sinks"]); P = int(instance["periods"])
    K = int(instance["max_open_per_period"])
    supply = [[float(v) for v in row] for row in instance["supply"]]
    demand = [[[float(v) for v in row] for row in blk] for blk in instance["demand"]]
    cost = [[[float(v) for v in row] for row in blk] for blk in instance["cost"]]
    fixed = [[[float(v) for v in row] for row in blk] for blk in instance["fixed"]]
    cap = [[[float(v) for v in row] for row in blk] for blk in instance["capacity"]]

    m = gp.Model("t15_reauth_compact")
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
                for t in range(P - 1):
                    m.addConstr(open_[b, s, d, t] >= open_[b, s, d, t + 1],
                                name=f"prefix[{b},{s},{d},{t}]")

    m.setObjective(quicksum(cost[b][s][d] * ship[b, s, d, t]
                            for b in range(B) for s in range(S) for d in range(D) for t in range(P))
                   + quicksum(fixed[b][s][d] * open_[b, s, d, t]
                              for b in range(B) for s in range(S) for d in range(D) for t in range(P)),
                   GRB.MINIMIZE)
    return m
