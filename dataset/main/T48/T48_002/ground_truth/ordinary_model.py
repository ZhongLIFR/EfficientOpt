import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    n = instance['customer_count'] + 1
    distance = instance['distance']
    
    model = gp.Model("TSP")
    
    # Decision variables
    edges = [(i, j) for i in range(n) for j in range(n) if i != j]
    x = model.addVars(edges, vtype=GRB.BINARY, name="x")
    u = model.addVars(range(1, n), lb=1, ub=n-1, vtype=GRB.CONTINUOUS, name="u")
    
    # Objective
    dist_dict = {(i, j): distance[i][j] for i, j in edges}
    model.setObjective(x.prod(dist_dict), GRB.MINIMIZE)
    
    # Constraints
    # 1. Leave each node exactly once
    model.addConstrs((x.sum(i, '*') == 1 for i in range(n)), name="out_degree")
    
    # 2. Enter each node exactly once
    model.addConstrs((x.sum('*', j) == 1 for j in range(n)), name="in_degree")
    
    # 3. Subtour elimination (Lifted MTZ)
    model.addConstrs(
        (u[i] - u[j] + (n - 1) * x[i, j] + (n - 3) * x[j, i] <= n - 2
         for i in range(1, n) for j in range(1, n) if i != j),
        name="mtz"
    )
    
    return model
