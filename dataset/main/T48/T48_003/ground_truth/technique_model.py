import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T48_04 technique: single-commodity flow subtour elimination + forbidden arcs."""
    n = instance["node_count"]
    cost = instance["cost"]
    forbidden = {tuple(a) for a in instance["forbidden_arcs"]}
    arcs = [(i, j) for i in range(n) for j in range(n) if i != j and (i, j) not in forbidden]
    flow_arcs = [(i, j) for (i, j) in arcs if j != 0]
    m = gp.Model("t48_04_technique_flow")
    x = m.addVars(arcs, vtype=GRB.BINARY, name="x")
    f = m.addVars(flow_arcs, lb=0.0, name="f")
    m.addConstrs((quicksum(x[i, j] for j in range(n) if (i, j) in arcs) == 1 for i in range(n)), name="out")
    m.addConstrs((quicksum(x[i, j] for i in range(n) if (i, j) in arcs) == 1 for j in range(n)), name="in")
    # depot-originated commodity: one unit delivered to each customer
    m.addConstrs(
        (quicksum(f[i, k] for i in range(n) if (i, k) in flow_arcs)
         - quicksum(f[k, j] for j in range(n) if (k, j) in flow_arcs) == 1
         for k in range(1, n)),
        name="flow_conservation",
    )
    m.addConstrs((f[i, j] <= (n - 1) * x[i, j] for (i, j) in flow_arcs), name="flow_link")
    m.setObjective(quicksum(cost[i][j] * x[i, j] for (i, j) in arcs), GRB.MINIMIZE)
    m._x = x
    return m
