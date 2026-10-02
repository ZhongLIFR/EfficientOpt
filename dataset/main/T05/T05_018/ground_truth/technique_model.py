import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T5_05 technique (tight data-derived big-M): regional 3-cycle portfolio.

    Same semantics as ordinary, but each standard row uses the tightest valid
    big-M coefficient M_q = max(0, sum of all positive coefficients - limit),
    giving a much stronger LP relaxation and fewer nodes.
    """
    d = instance
    projects = {r[0]: {"region": r[1], "funding": float(r[2]), "value": float(r[3])} for r in d["projects"]}
    standards = {r[0]: {"limit": float(r[1]), "coef": {q[0]: float(q[1]) for q in r[2]}} for r in d["review_standards"]}
    cycles = {r[0]: {"cap": float(r[1]), "mult": float(r[2]), "region_caps": r[3]} for r in d["funding_cycles"]}
    ids = sorted(projects); sids = sorted(standards); cids = sorted(cycles)

    m = gp.Model("t5_05_upgrade_tight")
    choose = m.addVars(ids, cids, vtype=GRB.BINARY, name="choose")
    met = m.addVars(sids, cids, vtype=GRB.BINARY, name="satisfied")
    for i in ids:
        m.addConstr(quicksum(choose[i, c] for c in cids) <= 1, name=f"once[{i}]")
    for c in cids:
        cyc = cycles[c]
        m.addConstr(quicksum(projects[i]["funding"] * choose[i, c] for i in ids) <= cyc["cap"], name=f"fund[{c}]")
        for region, cap in cyc["region_caps"].items():
            m.addConstr(quicksum(projects[i]["funding"] * choose[i, c] for i in ids
                                 if projects[i]["region"] == region) <= cap, name=f"region[{c},{region}]")
        for a, b in d["incompatible_project_pairs"]:
            m.addConstr(choose[a, c] + choose[b, c] <= 1, name=f"incompat[{c},{a},{b}]")
        m.addConstr(quicksum(met[q, c] for q in sids) >= d["minimum_standards_satisfied"],
                    name=f"minstd[{c}]")
        for q in sids:
            st = standards[q]
            lhs = quicksum(co * choose[i, c] for i, co in st["coef"].items())
            Mq = max(0.0, sum(co for co in st["coef"].values() if co > 0) - st["limit"])
            if Mq > 0:
                m.addConstr(lhs <= st["limit"] + Mq * (1 - met[q, c]), name=f"std[{c},{q}]")
            else:
                m.addConstr(met[q, c] == 1, name=f"std_auto[{c},{q}]")
    m.setObjective(quicksum(cycles[c]["mult"] * projects[i]["value"] * choose[i, c]
                            for i in ids for c in cids), GRB.MAXIMIZE)
    return m
