import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T18_20 technique: single-commodity flow subtour elimination (TSP)."""
    n = instance["city_count"]
    dist = instance["distances"]
    arcs = [(i, j) for i in range(n) for j in range(n) if i != j]
    m = gp.Model("t18_20_tsp_scf")
    x = m.addVars(arcs, vtype=GRB.BINARY, name="x")
    # flow on arcs entering non-depot nodes
    flow_arcs = [(i, j) for (i, j) in arcs if j != 0]
    f = m.addVars(flow_arcs, lb=0.0, name="f")
    m.addConstrs((quicksum(x[i, j] for j in range(n) if i != j) == 1 for i in range(n)), name="out")
    m.addConstrs((quicksum(x[i, j] for i in range(n) if i != j) == 1 for j in range(n)), name="in")
    # depot-originated commodity: (n-1) units leave depot, 1 delivered per node
    m.addConstr(
        quicksum(f[0, j] for j in range(1, n)) == n - 1, name="depot_out"
    )
    m.addConstrs(
        (quicksum(f[i, k] for i in range(n) if (i, k) in flow_arcs)
         - quicksum(f[k, j] for j in range(n) if (k, j) in flow_arcs) == 1
         for k in range(1, n)),
        name="flow_conservation",
    )
    m.addConstrs((f[i, j] <= (n - 1) * x[i, j] for (i, j) in flow_arcs), name="flow_link")
    m.setObjective(quicksum(dist[i][j] * x[i, j] for (i, j) in arcs), GRB.MINIMIZE)
    return m
