import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T20 compact reconstruction: adjacent temporal persistence plus the same exact minimal-prefix closure. The auxiliary prefix state is continuous in [0,1], but the closure and binary use variables force the same optimal 0/1 state."""
    N = int(instance["nodes"]); P = int(instance["periods"])
    K = int(instance["max_open_per_period"])
    arcs = [(int(u), int(v)) for u, v in instance["arcs"]]
    cap = [float(v) for v in instance["capacity"]]
    cost = [float(v) for v in instance["cost"]]
    fixed = [float(v) for v in instance["fixed"]]
    bal = [[float(v) for v in row] for row in instance["balance"]]
    A = len(arcs)
    out_arcs = [[] for _ in range(N)]
    in_arcs = [[] for _ in range(N)]
    for a, (u, v) in enumerate(arcs):
        out_arcs[u].append(a)
        in_arcs[v].append(a)

    m = gp.Model("t4_reauth_compact")
    flow = m.addVars(A, P, lb=0.0, name="flow")
    use = m.addVars(A, P, vtype=GRB.BINARY, name="use")
    open_ = m.addVars(A, P, vtype=GRB.CONTINUOUS, ub=1.0, name="open")

    for t in range(P):
        m.addConstr(quicksum(use[a, t] for a in range(A)) <= K, name=f"cap[{t}]")
        for n in range(N):
            m.addConstr(quicksum(flow[a, t] for a in in_arcs[n])
                        - quicksum(flow[a, t] for a in out_arcs[n]) == bal[n][t],
                        name=f"bal[{n},{t}]")
    for a in range(A):
        for t in range(P):
            m.addConstr(flow[a, t] <= cap[a] * use[a, t], name=f"flowif[{a},{t}]")
            m.addConstr(use[a, t] <= open_[a, t], name=f"useif[{a},{t}]")
        for t in range(P - 1):
            m.addConstr(open_[a, t] >= open_[a, t + 1], name=f"prefix[{a},{t}]")

    for a in range(A):
        for t in range(P - 1):
            m.addConstr(
                open_[a, t] <= use[a, t] + open_[a, t + 1],
                name=f"exact_prefix[{a},{t}]",
            )
        m.addConstr(
            open_[a, P - 1] <= use[a, P - 1],
            name=f"exact_last[{a}]",
        )

    m.setObjective(quicksum(cost[a] * flow[a, t] for a in range(A) for t in range(P))
                   + quicksum(fixed[a] * open_[a, t] for a in range(A) for t in range(P)),
                   GRB.MINIMIZE)
    return m
