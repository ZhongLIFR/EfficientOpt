from __future__ import annotations

import json
from pathlib import Path
import gurobipy as gp
from gurobipy import GRB


def load_instance() -> dict:
    return json.loads((Path(__file__).resolve().parents[1] / "public" / "instance.json").read_text())


def build_model(instance: dict) -> gp.Model:
    site_count = len(instance["sites"]); alternatives = len(instance["sites"][0]["alternatives"])
    model = gp.Model(instance["problem_id"] + "_ordinary")
    select = model.addVars(site_count, alternatives, vtype=GRB.BINARY, name="select")
    model.addConstrs((select[g, a] + select[g, b] <= 1 for g in range(site_count) for a in range(alternatives) for b in range(a + 1, alternatives)), name="pair_conflict")
    model.addConstrs((gp.quicksum(instance["sites"][g]["alternatives"][k]["resource_use"][r] * select[g, k] for g in range(site_count) for k in range(alternatives)) <= instance["resource_budget"][r] for r in range(len(instance["resource_names"]))), name="resource_budget")
    model.setObjective(gp.quicksum(instance["sites"][g]["alternatives"][k]["value"] * select[g, k] for g in range(site_count) for k in range(alternatives)), GRB.MAXIMIZE)
    return model


if __name__ == "__main__":
    model = build_model(load_instance()); model.Params.OutputFlag = 0; model.optimize()
    print(json.dumps({"status": int(model.Status), "objective": model.ObjVal if model.SolCount else None, "solver_s": model.Runtime}, indent=2))
