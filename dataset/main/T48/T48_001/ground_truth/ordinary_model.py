import gurobipy as gp
from gurobipy import GRB, quicksum

def build_model(instance):
    customer_count = instance['customer_count']
    N = customer_count + 1
    dist = instance['distance']
    
    # Precompute distance matrix as list of lists for fast indexing
    dist_mat = [list(row) for row in dist]
        
    model = gp.Model("TSP")
    
    # Binary variables for edges
    x = model.addVars(N, N, vtype=GRB.BINARY, name="x")
    # Fix diagonal to 0 (no self-loops)
    for i in range(N):
        x[i, i].ub = 0
        
    # MTZ continuous variables for subtour elimination
    # u[i] represents the visit order of customer i (1 to N-1)
    u = model.addVars(range(1, N), lb=1, ub=N-1, vtype=GRB.CONTINUOUS, name="u")
        
    # Degree constraints: exactly one outgoing and one incoming edge per node
    model.addConstrs((x.sum(i, '*') == 1 for i in range(N)), name="outflow")
    model.addConstrs((x.sum('*', j) == 1 for j in range(N)), name="inflow")
    
    # MTZ subtour elimination constraints
    model.addConstrs(
        (u[i] - u[j] + N * x[i, j] <= N - 1 for i in range(1, N) for j in range(1, N) if i != j),
        name="mtz"
    )
    
    # Objective: minimize total travel cost
    obj = quicksum(dist_mat[i][j] * x[i, j] for i in range(N) for j in range(N) if i != j)
    model.setObjective(obj, GRB.MINIMIZE)
    
    return model