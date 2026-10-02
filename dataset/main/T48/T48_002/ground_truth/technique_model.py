import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    customer_count = instance['customer_count']
    N = customer_count + 1
    distance = instance['distance']
    nodes = range(N)
    
    # Sparse arc set and precomputed costs to avoid repeated scans
    arcs = [(i, j) for i in nodes for j in nodes if i != j]
    arc_cost = {(i, j): distance[i][j] for i, j in arcs}
    
    model = gp.Model("TSP")
    
    # Tour arcs
    x = model.addVars(arcs, vtype=GRB.BINARY, name="x")
    # Single-commodity flow variables
    y = model.addVars(arcs, vtype=GRB.CONTINUOUS, lb=0.0, name="y")
    
    # Objective: minimize total travel cost
    model.setObjective(x.prod(arc_cost), GRB.MINIMIZE)
    
    # Assignment constraints
    model.addConstrs((gp.quicksum(x[i, j] for j in nodes if j != i) == 1 for i in nodes), name="out")
    model.addConstrs((gp.quicksum(x[i, j] for i in nodes if i != j) == 1 for j in nodes), name="in")
    
    # Strengthening: eliminate 2-cycles
    model.addConstrs((x[i, j] + x[j, i] <= 1 for i in nodes for j in nodes if i < j), name="no2cycle")
    
    # Flow conservation: depot supplies N−1 units, each customer consumes 1
    model.addConstr(
        gp.quicksum(y[0, j] for j in nodes if j != 0) - gp.quicksum(y[i, 0] for i in nodes if i != 0) == N - 1,
        name="flow_depot"
    )
    model.addConstrs(
        (gp.quicksum(y[i, k] for i in nodes if i != k) - gp.quicksum(y[k, j] for j in nodes if j != k) == 1
         for k in nodes if k != 0),
        name="flow_cust"
    )
    
    # Capacity linking constraints
    model.addConstrs((y[i, j] <= (N - 1) * x[i, j] for i, j in arcs), name="cap")
    
    # Valid lower bound: any arc entering a customer must carry at least one unit of flow
    model.addConstrs((y[i, j] >= x[i, j] for i, j in arcs if j != 0), name="lb")
    
    return model
