import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """Technique formulation: continuous transportation flow.

    Same supply/demand/cost semantics; flows are continuous.  The constraint
    matrix is totally unimodular with integral right-hand side so the LP
    optimum is integral and equals the integer-flow optimum.
    """
    supplies = instance["supplies"]
    demands = instance["demands"]
    costs = instance["costs"]
    S = len(supplies)
    D = len(demands)
    m = gp.Model("continuous_transportation_relaxation")
    x = m.addVars(S, D, lb=0.0, name="x")
    m.addConstrs((quicksum(x[i, j] for j in range(D)) == supplies[i] for i in range(S)), name="supply")
    m.addConstrs((quicksum(x[i, j] for i in range(S)) == demands[j] for j in range(D)), name="demand")
    m.setObjective(quicksum(costs[i][j] * x[i, j] for i in range(S) for j in range(D)), GRB.MINIMIZE)
    return m
