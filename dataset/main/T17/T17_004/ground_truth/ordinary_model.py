"""Ordinary formulation: enumerate every compatible route (subset of sites) and cover."""
from __future__ import annotations

import json
import time
from itertools import combinations

import gurobipy as gp
from gurobipy import GRB

from common import configure, load_instance, rss_mb


def solve(technique: bool = False) -> dict:
    if technique:
        raise RuntimeError("ordinary_model.py implements the ordinary formulation only")
    rss0 = rss_mb()
    d = load_instance()
    n = d["site_count"]; K = d["max_sites_per_route"]; J = d["max_open_routes"]
    cm = [0] * n
    for a, b in d["incompatible_pairs"]:
        cm[a] |= 1 << b
        cm[b] |= 1 << a
    t_build = time.perf_counter()
    routes = []
    dur = d["site_duration"]; shift = d["shift_length"]
    wgt = d["site_weight"]; wlim = d["route_weight_limit"]
    vol = d["site_volume"]; vlim = d["route_volume_limit"]
    # enumerate by subset SIZE (C(n, <=K)) instead of all 2^n masks, so larger n stays tractable
    for size in range(1, min(K, n) + 1):
        for combo in combinations(range(n), size):
            mask = 0
            for i in combo:
                mask |= 1 << i
            ok = True
            total_dur = total_w = total_v = 0
            for i in combo:
                if cm[i] & mask:
                    ok = False
                    break
                total_dur += dur[i]; total_w += wgt[i]; total_v += vol[i]
            if ok and total_dur <= shift and total_w <= wlim and total_v <= vlim:
                routes.append(mask)
    mdl = gp.Model("full_covering_lp"); configure(mdl)
    x = mdl.addVars(len(routes), lb=0.0, ub=1.0, name="route_use")
    for i in range(n):
        mdl.addConstr(gp.quicksum(x[p] for p in range(len(routes)) if routes[p] >> i & 1) >= 1,
                      name=f"cover_{i}")
    mdl.addConstr(gp.quicksum(x[p] for p in range(len(routes))) <= J, name="fleet_limit")
    cost = [d["fixed_route_charge"] + sum(d["site_service_cost"][i] for i in range(n)
                                          if routes[p] >> i & 1) for p in range(len(routes))]
    mdl.setObjective(gp.quicksum(cost[p] * x[p] for p in range(len(routes))), GRB.MINIMIZE)
    build_s = time.perf_counter() - t_build
    rss1 = rss_mb()
    mdl.optimize()
    rss2 = rss_mb()
    if mdl.Status != GRB.OPTIMAL:
        raise RuntimeError(f"ordinary model status {mdl.Status}")
    viol = max(0.0, sum(x[p].X for p in range(len(routes))) - J)
    for i in range(n):
        viol = max(viol, 1.0 - sum(x[p].X for p in range(len(routes)) if routes[p] >> i & 1))
    return {
        "objective": mdl.ObjVal, "runtime_s": mdl.Runtime, "work": mdl.Work,
        "num_variables": mdl.NumVars, "num_constraints": mdl.NumConstrs, "num_nonzeros": mdl.NumNZs,
        "build_time_s": round(build_s, 4),
        "node_count": int(getattr(mdl, "NodeCount", 0) or 0),
        "simplex_iterations": int(getattr(mdl, "IterCount", 0) or 0),
        "gurobi_mem_used_mb": float(getattr(mdl, "MemUsed", 0.0) or 0.0),
        "max_mem_used_mb": float(getattr(mdl, "MaxMemUsed", 0.0) or 0.0),
        "rss_after_load_mb": rss0, "rss_after_build_mb": rss1, "rss_after_solve_mb": rss2,
        "constraint_violation": viol, "bound_violation": 0.0,
        "checksum": round(sum((p + 1) * x[p].X for p in range(len(routes))), 6),
        "route_count": len(routes),
    }


if __name__ == "__main__":
    print(json.dumps(solve(False)))
