import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T6_18 technique (semi-continuous variables): optional mining lots.

    Same semantics as ordinary.  Each lot is a native semi-continuous
    variable (vtype=GRB.SEMICONT, bound set to [minimum, maximum]): value is
    either 0 or within the interval, with no auxiliary binary per lot.
    """
    opts = instance["options"]
    caps = instance["resource_capacities"]
    reqs = instance["requirements"]
    R = len(caps)
    Q = len(reqs)
    n = len(opts)
    m = gp.Model("t6_18_lots_semicont")
    x = m.addVars(n, vtype=GRB.SEMICONT, name="x")
    for i, o in enumerate(opts):
        x[i].LB = o["minimum"]
        x[i].UB = o["maximum"]
    for r in range(R):
        m.addConstr(quicksum(o["resources"][r] * x[i] for i, o in enumerate(opts)) <= caps[r],
                    name=f"res[{r}]")
    for q in range(Q):
        m.addConstr(quicksum(o["outputs"][q] * x[i] for i, o in enumerate(opts)) >= reqs[q],
                    name=f"out[{q}]")
    m.setObjective(quicksum(o["profit"] * x[i] for i, o in enumerate(opts)), GRB.MAXIMIZE)
    return m
