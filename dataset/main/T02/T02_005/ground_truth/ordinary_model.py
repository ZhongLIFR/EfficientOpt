import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T2_20 ordinary (naive): capacity-excess with difference/zero bookkeeping.

    Same assignment variables, but excess is modeled through an explicit
    signed difference variable plus a fixed-to-zero helper (the indirect,
    more verbose way a naive modeler might linearize max(0, load-cap)).
    """
    n = instance["num_students"]
    G = instance["num_groups"]
    C = instance["num_classes"]
    enroll = instance["enrollments"]
    cap = instance["class_capacity"]
    pref = instance["preference_penalty"]
    ew = instance["excess_weight"]

    enrolled_by_class = [[] for _ in range(C)]
    for s, classes in enumerate(enroll):
        for course in classes:
            enrolled_by_class[course].append(s)

    m = gp.Model("t2_20_naive")
    x = m.addVars(n, G, vtype=GRB.BINARY, name="assign")
    for s in range(n):
        m.addConstr(quicksum(x[s, g] for g in range(G)) == 1, name=f"one[{s}]")
    excesses = []
    for c in range(C):
        for g in range(G):
            load = quicksum(x[s, g] for s in enrolled_by_class[c])
            diff = m.addVar(lb=-GRB.INFINITY, name=f"diff[{c},{g}]")
            m.addConstr(diff == load - cap[c][g], name=f"diffc[{c},{g}]")
            e = m.addVar(lb=0.0, name=f"excess[{c},{g}]")
            # excess >= diff and excess >= 0 (diff can be negative: no excess)
            m.addConstr(e >= diff, name=f"exc_lb[{c},{g}]")
            m.addConstr(e >= 0.0, name=f"exc_nn[{c},{g}]")
            excesses.append(e)
    obj = ew * quicksum(excesses) + quicksum(
        pref[s][g] * x[s, g] for s in range(n) for g in range(G)
    )
    m.setObjective(obj, GRB.MINIMIZE)
    return m
