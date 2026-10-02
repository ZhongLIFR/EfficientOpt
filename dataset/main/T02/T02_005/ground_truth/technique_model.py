import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T2_20 technique (T02 epigraph): capacity excess via direct lower bound.

    x[s,g] = 1 student s -> group g.  load[c,g] = students in class c assigned
    to group g.  excess[c,g] >= load[c,g] - cap[c][g], excess >= 0, minimized
    (weighted).  This is the standard epigraph (hypograph-free) formulation.
    """
    n = instance["num_students"]
    G = instance["num_groups"]
    C = instance["num_classes"]
    enroll = instance["enrollments"]      # n x (courses)
    cap = instance["class_capacity"]      # C x G
    pref = instance["preference_penalty"]  # n x G
    ew = instance["excess_weight"]

    enrolled_by_class = [[] for _ in range(C)]
    for s, classes in enumerate(enroll):
        for course in classes:
            enrolled_by_class[course].append(s)

    m = gp.Model("t2_20_epigraph")
    x = m.addVars(n, G, vtype=GRB.BINARY, name="assign")
    for s in range(n):
        m.addConstr(quicksum(x[s, g] for g in range(G)) == 1, name=f"one[{s}]")
    excesses = []
    for c in range(C):
        for g in range(G):
            load = quicksum(x[s, g] for s in enrolled_by_class[c])
            e = m.addVar(lb=0.0, name=f"excess[{c},{g}]")
            m.addConstr(e >= load - cap[c][g], name=f"exc[{c},{g}]")
            excesses.append(e)
    obj = ew * quicksum(excesses) + quicksum(
        pref[s][g] * x[s, g] for s in range(n) for g in range(G)
    )
    m.setObjective(obj, GRB.MINIMIZE)
    return m
