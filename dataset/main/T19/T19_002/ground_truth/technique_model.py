import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T19_19 technique: compact covering model.

    One hire binary per translator and one row per language counting hired
    speakers (>= minimum_interpreters_per_language). Team-size bounds, agency
    group caps, incompatible pairs identical. No slot/designee variables;
    same optimum as the naive slot model.
    """
    L = int(instance["num_languages"])
    k = int(instance["minimum_interpreters_per_language"])
    trans = instance["translators"]
    n = len(trans)
    cost = [float(t["cost"]) for t in trans]
    m = gp.Model("t19_19_compact_cover")
    hire = m.addVars(n, vtype=GRB.BINARY, name="hire")

    speakers = [[] for _ in range(L)]
    for i, t in enumerate(trans):
        for l in t["languages"]:
            speakers[l].append(i)
    for l in range(L):
        m.addConstr(quicksum(hire[i] for i in speakers[l]) >= k, name=f"cover[{l}]")

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
