"""Ordinary formulation: one constraint per vertex of every gate polytope."""
from __future__ import annotations

import json
import time
from itertools import product

import numpy as np
from scipy import sparse
import gurobipy as gp
from gurobipy import GRB

from common import configure, load_instance, rss_mb


def solve(technique: bool = False) -> dict:
    if technique:
        raise RuntimeError("ordinary_model.py implements the ordinary formulation only")
    rss0 = rss_mb()
    d_ = load_instance()
    gates = d_["gates"]; K = len(gates); J = len(d_["profit"])
    b = d_["gate_limit"]
    t_build = time.perf_counter()
    mdl = gp.Model("vertex_rows")
    configure(mdl)
    x = mdl.addVars(J, lb=0.0, name="plan_level")
    xlist = [x[j] for j in range(J)]
    rows = 0
    for k in range(K):
        load = np.asarray(gates[k]["nominal_load"], dtype=float)
        A = np.asarray(gates[k]["kpi_matrix"], dtype=float)      # d x J
        V = np.array(list(product((1.0, -1.0), repeat=A.shape[0])))   # 2^d box corners
        coeff = np.vstack([load[None, :] + V @ A])               # V x J
        mdl.addMConstr(sparse.csr_matrix(coeff), xlist,
                       np.full(coeff.shape[0], GRB.LESS_EQUAL),
                       np.full(coeff.shape[0], float(b[k])))
        rows += coeff.shape[0]
    mdl.setObjective(gp.quicksum(d_["profit"][j] * x[j] for j in range(J)), GRB.MAXIMIZE)
    build_s = time.perf_counter() - t_build
    rss1 = rss_mb()
    mdl.optimize()
    rss2 = rss_mb()
    if mdl.Status != GRB.OPTIMAL:
        raise RuntimeError(f"ordinary model status {mdl.Status}")
    viol = 0.0
    for k in range(K):
        load = gates[k]["nominal_load"]; A = np.asarray(gates[k]["kpi_matrix"], dtype=float)
        V = np.array(list(product((1.0, -1.0), repeat=A.shape[0])))
        xv = np.array([x[j].X for j in range(J)])
        worst = float(np.max(V @ (A @ xv)))
        viol = max(viol, float(np.asarray(load) @ xv) + worst - b[k])
    return {
        "objective": mdl.ObjVal, "runtime_s": mdl.Runtime, "work": mdl.Work,
        "num_variables": mdl.NumVars, "num_constraints": mdl.NumConstrs, "num_nonzeros": mdl.NumNZs,
        "build_time_s": round(build_s, 4),
        "node_count": int(getattr(mdl, "NodeCount", 0) or 0),
        "simplex_iterations": int(getattr(mdl, "IterCount", 0) or 0),
        "gurobi_mem_used_mb": round(float(getattr(mdl, "MemUsed", 0.0) or 0.0), 2),
        "max_mem_used_mb": round(float(getattr(mdl, "MaxMemUsed", 0.0) or 0.0), 2),
        "rss_after_load_mb": rss0, "rss_after_build_mb": rss1, "rss_after_solve_mb": rss2,
        "constraint_violation": max(0.0, viol), "bound_violation": 0.0,
        "checksum": round(sum((j + 1) * x[j].X for j in range(J)), 6),
        "vertex_rows": rows,
    }


if __name__ == "__main__":
    print(json.dumps(solve(False)))
