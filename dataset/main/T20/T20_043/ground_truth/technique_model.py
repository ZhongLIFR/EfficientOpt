import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T13_01 re-authored technique: compact mode-persistence production mix.

    max sum value[b][m]*x[b,m,t]
    s.t. sum_m x[b,m,t] >= demand[b][t]
         sum_m resource[b][m]*x[b,m,t] <= capacity[b][t]
         x[b,m,t] <= U[b][m]*use[b,m,t];  use[b,m,t] <= act[b,m,t]
         sum_m use[b,m,t] <= K
         act[b,m,t] <= act[b,m,t+1]        (adjacent persistence, O(B*M*P) rows)
    """
    B = int(instance["blocks"]); M = int(instance["modes"]); P = int(instance["periods"])
    K = int(instance["max_active_per_period"])
    value = [[[float(v) for v in row] for row in blk] for blk in instance["value"]]
    resource = [[[float(v) for v in row] for row in blk] for blk in instance["resource"]]
    capacity = [[float(v) for v in row] for row in instance["capacity"]]
    demand = [[float(v) for v in row] for row in instance["demand"]]
    fixed = [[[float(v) for v in row] for row in blk] for blk in instance["fixed"]]
    minrun = [[float(v) for v in row] for row in instance["minrun"]]
    maxout = [[float(v) for v in row] for row in instance["maxout"]]

    m = gp.Model("t13_reauth_compact")
    x = m.addVars(B, M, P, lb=0.0, name="x")
    use = m.addVars(B, M, P, vtype=GRB.BINARY, name="use")
    act = m.addVars(B, M, P, vtype=GRB.BINARY, name="act")

    for b in range(B):
        for t in range(P):
            m.addConstr(quicksum(x[b, mm, t] for mm in range(M)) >= demand[b][t],
                        name=f"dem[{b},{t}]")
            m.addConstr(quicksum(resource[b][mm][t] * x[b, mm, t] for mm in range(M)) <= capacity[b][t],
                        name=f"cap[{b},{t}]")
            m.addConstr(quicksum(use[b, mm, t] for mm in range(M)) <= K, name=f"maxact[{b},{t}]")
        for mm in range(M):
            ub = maxout[b][mm]
            for t in range(P):
                m.addConstr(x[b, mm, t] <= ub * use[b, mm, t], name=f"xif[{b},{mm},{t}]")
                m.addConstr(x[b, mm, t] >= minrun[b][mm] * use[b, mm, t], name=f"xmin[{b},{mm},{t}]")
                m.addConstr(use[b, mm, t] <= act[b, mm, t], name=f"useif[{b},{mm},{t}]")
            for t in range(P - 1):
                m.addConstr(act[b, mm, t] <= act[b, mm, t + 1], name=f"persistence[{b},{mm},{t}]")

    m.setObjective(quicksum(value[b][mm][t] * x[b, mm, t]
                            for b in range(B) for mm in range(M) for t in range(P))
                   - quicksum(fixed[b][mm][t] * act[b, mm, t]
                              for b in range(B) for mm in range(M) for t in range(P)),
                   GRB.MAXIMIZE)
    return m
