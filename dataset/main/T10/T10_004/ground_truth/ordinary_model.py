"""Generic QAP factory for T10 family items plus T8_20/T10_30 variants.

Pattern: assign n units to m sites with capacity; pairwise exchange volume x
directional pair-cost table (zero diagonal); fixed_assignment_cost minus
benefit; minimize total.  Field names differ per item.  Both McCormick
(technique=False) and convex-hull row/column marginal (technique=True) forms.

For T10_02..T10_10 fields:
  unit_count_key, site_count_key, capacity_key, fixed, benefit, pairs, paircost.
For T10_30: no *_count keys -> length of departments; edges named
communication_edges; benefit relocation_benefit; sites from cities.
"""
import gurobipy as gp
from gurobipy import GRB, quicksum

BENEFIT_KEYS = ("coordination_benefit", "relocation_benefit")
PAIR_KEYS = ("data_exchange_pairs", "communication_edges")
PAIRCOST_KEYS = ("network_pair_cost", "city_pair_cost")
CAP_KEYS = ("datacenter_capacity", "campus_capacity", "station_capacity", "center_capacity",
            "zone_capacity", "cluster_capacity", "city_capacity")


def build(instance, technique):
    # unit count / site count
    n = None
    for k in instance:
        if k.endswith("_count"):
            n = int(instance[k]); break
    m = None
    if n is None:
        # T10_30 style: departments x cities
        n = len(instance["departments"])
    cap = next((instance[k] for k in CAP_KEYS if k in instance), None)
    fc = instance["fixed_assignment_cost"]
    ben = next((instance[k] for k in BENEFIT_KEYS if k in instance), [0.0]*n)
    if m is None:
        m = len(fc[0])
    pc = next((instance[k] for k in PAIRCOST_KEYS if k in instance), None)
    pairs = next((instance[k] for k in PAIR_KEYS if k in instance), [])
    mdl = gp.Model("t10_qap")
    x = mdl.addVars(n, m, vtype=GRB.BINARY, name="assign")
    for i in range(n):
        mdl.addConstr(quicksum(x[i, c] for c in range(m)) == 1, name=f"once[{i}]")
    if cap is not None:
        for c in range(m):
            mdl.addConstr(quicksum(x[i, c] for i in range(n)) <= cap[c], name=f"cap[{c}]")
    obj = quicksum((fc[i][c] - ben[i]) * x[i, c] for i in range(n) for c in range(m))
    for e in pairs:
        if hasattr(e, "keys") and "i" in e:
            i = int(e["i"]); j = int(e["j"]); vol = float(e["volume"])
        elif hasattr(e, "keys") and "id1" in e:
            i = int(e["id1"]); j = int(e["id2"]); vol = float(e["volume"])
        else:
            i = int(e[0]); j = int(e[1]); vol = float(e[2])
        if technique:
            z = mdl.addVars(m, m, lb=0.0, ub=1.0, name=f"z_{i}_{j}")
            for c in range(m):
                mdl.addConstr(quicksum(z[c, k] for k in range(m)) == x[i, c], name=f"row_{i}_{j}_{c}")
            for k in range(m):
                mdl.addConstr(quicksum(z[c, k] for c in range(m)) == x[j, k], name=f"col_{i}_{j}_{k}")
        else:
            z = mdl.addVars(m, m, lb=0.0, ub=1.0, name=f"z_{i}_{j}")
            for c in range(m):
                for k in range(m):
                    mdl.addConstr(z[c, k] <= x[i, c], name=f"ub1")
                    mdl.addConstr(z[c, k] <= x[j, k], name=f"ub2")
                    mdl.addConstr(z[c, k] >= x[i, c] + x[j, k] - 1, name=f"lb")
        obj += quicksum(vol * pc[c][k] * z[c, k] for c in range(m) for k in range(m))
    mdl.setObjective(obj, GRB.MINIMIZE)
    return mdl


def build_model(instance):
    return build(instance, technique=False)
