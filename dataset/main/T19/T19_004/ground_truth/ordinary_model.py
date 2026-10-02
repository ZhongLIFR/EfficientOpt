import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T19_19 ordinary (naive): slot-designee covering model.

    For each language and each of its `minimum_interpreters_per_language`
    rotation slots, designate exactly one *distinct* hired translator who
    speaks it (assign[l,t,i] binary <= hire[i], and per (l,i) at most one
    slot). Team-size bounds, agency-group caps and incompatible pairs on hire
    exactly as in the problem. Exact equivalent of the compact covering model.
    """
    L = int(instance["num_languages"])
    k = int(instance["minimum_interpreters_per_language"])
    trans = instance["translators"]
    n = len(trans)
    cost = [float(t["cost"]) for t in trans]
    m = gp.Model("t19_19_naive_slot_designee")
    hire = m.addVars(n, vtype=GRB.BINARY, name="hire")

    assign = {}
    for l in range(L):
        coverers = [i for i in range(n) if l in trans[i]["languages"]]
        for t in range(k):
            for i in coverers:
                assign[l, t, i] = m.addVar(vtype=GRB.BINARY, name=f"a[{l},{t},{i}]")
                m.addConstr(assign[l, t, i] <= hire[i], name=f"link[{l},{t},{i}]")
        for t in range(k):
            m.addConstr(quicksum(assign[l, t, i] for i in coverers) == 1, name=f"slot[{l},{t}]")
        for i in coverers:
            m.addConstr(quicksum(assign[l, t, i] for t in range(k)) <= 1, name=f"one[{l},{i}]")

    m.addConstr(quicksum(hire) >= int(instance["team_size_minimum"]), name="min_size")
    m.addConstr(quicksum(hire) <= int(instance["team_size_maximum"]), name="max_size")
    for g in instance["agency_groups"]:
        gi = [i for i in g["translators"]]
        if gi:
            m.addConstr(quicksum(hire[i] for i in gi) <= int(g["maximum_hires"]), name=f"grp_{g['name']}")
    for a, b in instance["incompatible_pairs"]:
        m.addConstr(hire[a] + hire[b] <= 1, name=f"inc_{a}_{b}")

    m.setObjective(quicksum(cost[i] * hire[i] for i in range(n)), GRB.MINIMIZE)
    return m
