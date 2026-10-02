import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T6_18 ordinary (naive binary activation): optional mining lots.

    Each lot i either idle (x=0) or produces x in [minimum_i, maximum_i].
    3 shared resource caps and 2 output requirements.  Maximize profit.

    Naive: continuous x_i with an explicit binary y_i enforcing
    x_i >= minimum_i*y_i and x_i <= maximum_i*y_i.
    """
    opts = instance["options"]
    caps = instance["resource_capacities"]
    reqs = instance["requirements"]
    R = len(caps)
    Q = len(reqs)
    n = len(opts)
    m = gp.Model("t6_18_lots_naive")
    x = m.addVars(n, lb=0.0, name="x")
    y = m.addVars(n, vtype=GRB.BINARY, name="y")
    for i, o in enumerate(opts):
        m.addConstr(x[i] >= o["minimum"] * y[i], name=f"minrun[{i}]")
        m.addConstr(x[i] <= o["maximum"] * y[i], name=f"maxrun[{i}]")
    for r in range(R):
        m.addConstr(quicksum(o["resources"][r] * x[i] for i, o in enumerate(opts)) <= caps[r],
                    name=f"res[{r}]")
    for q in range(Q):
        m.addConstr(quicksum(o["outputs"][q] * x[i] for i, o in enumerate(opts)) >= reqs[q],
                    name=f"out[{q}]")
    m.setObjective(quicksum(o["profit"] * x[i] for i, o in enumerate(opts)), GRB.MAXIMIZE)
    return m
