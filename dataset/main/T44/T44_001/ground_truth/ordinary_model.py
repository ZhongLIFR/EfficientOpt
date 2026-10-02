import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T44 ordinary (naive): integer flow variables (identical polytope, MIP view)."""
    supplies = instance["supplies"]
    demands = instance["demands"]
    costs = instance["costs"]
    S = len(supplies)
    D = len(demands)
    m = gp.Model("t44_integer_flow")
    x = m.addVars(S, D, lb=0.0, vtype=GRB.INTEGER, name="x")
    m.addConstrs((quicksum(x[i, j] for j in range(D)) == supplies[i] for i in range(S)), name="supply")
    m.addConstrs((quicksum(x[i, j] for i in range(S)) == demands[j] for j in range(D)), name="demand")
    m.setObjective(quicksum(costs[i][j] * x[i, j] for i in range(S) for j in range(D)), GRB.MINIMIZE)
    return m
