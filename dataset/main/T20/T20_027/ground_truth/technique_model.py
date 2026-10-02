import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """Compact exact open-prefix model using adjacent-period implications."""
    N = int(instance["nodes"])
    P = int(instance["periods"])
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

    model = gp.Model("compact_adjacent_open_prefix")
    flow = model.addVars(A, P, lb=0.0, name="flow")
    use = model.addVars(A, P, vtype=GRB.BINARY, name="use")
    open_ = model.addVars(A, P, vtype=GRB.BINARY, name="open")
    for t in range(P):
        model.addConstr(quicksum(use[a, t] for a in range(A)) <= K, name=f"cap[{t}]")
        for n in range(N):
            model.addConstr(
                quicksum(flow[a, t] for a in in_arcs[n])
                - quicksum(flow[a, t] for a in out_arcs[n])
                == bal[n][t],
                name=f"bal[{n},{t}]",
            )
    for a in range(A):
        for t in range(P):
            model.addConstr(flow[a, t] <= cap[a] * use[a, t], name=f"flowif[{a},{t}]")
            model.addConstr(use[a, t] <= open_[a, t], name=f"useif[{a},{t}]")
        for t in range(P - 1):
            model.addConstr(open_[a, t] >= open_[a, t + 1], name=f"prefix[{a},{t}]")
    model.setObjective(
        quicksum(cost[a] * flow[a, t] for a in range(A) for t in range(P))
        + quicksum(fixed[a] * open_[a, t] for a in range(A) for t in range(P)),
        GRB.MINIMIZE,
    )
    return model
