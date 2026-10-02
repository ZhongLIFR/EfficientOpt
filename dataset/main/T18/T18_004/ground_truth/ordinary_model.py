from __future__ import annotations

import json
from pathlib import Path

import gurobipy as gp
import numpy as np
from gurobipy import GRB


def load_instance() -> dict:
    return json.loads((Path(__file__).resolve().parents[1] / "public" / "instance.json").read_text())


def build_model(instance: dict) -> gp.Model:
    costs = np.asarray(instance["assignment_cost"], dtype=np.float64)
    n = len(instance["workers"])
    model = gp.Model(instance["problem_id"] + "_ordinary")
    assign = model.addMVar((n, n), lb=0.0, ub=1.0, vtype=GRB.BINARY, name="assign")
    model.addConstr(assign.sum(axis=1) == 1, name="worker_once")
    model.addConstr(assign.sum(axis=0) == 1, name="task_once")
    model.setObjective(costs.reshape(-1) @ assign.reshape(-1), GRB.MINIMIZE)
    return model


if __name__ == "__main__":
    model = build_model(load_instance())
    model.Params.OutputFlag = 0
    model.optimize()
    print(json.dumps({"status": int(model.Status), "objective": model.ObjVal if model.SolCount else None, "solver_s": model.Runtime}, indent=2))
