import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T24_11 ordinary (naive): weighted set cover with exact hard count.

    x[p] binary per package (easy cost 1, hard cost 2); every task covered at
    least once; exactly 64 hard packages selected; minimize total cost.
    """
    diff = {int(r["package_id"]): r["difficulty"] for r in instance["package_difficulty"]}
    tasks_by_pkg = {}
    for rec in instance["package_task"]:
        tasks_by_pkg.setdefault(int(rec["package_id"]), []).append(int(rec["task_id"]))
    pids = sorted(tasks_by_pkg)
    task_ids = sorted({t for lst in tasks_by_pkg.values() for t in lst})
    cover = {t: [] for t in task_ids}
    for p in pids:
        for t in tasks_by_pkg[p]:
            cover[t].append(p)

    m = gp.Model("t24_11_setcover")
    x = m.addVars(pids, vtype=GRB.BINARY, name="x")
    for t in task_ids:
        m.addConstr(quicksum(x[p] for p in cover[t]) >= 1, name=f"cov_{t}")
    hard = [p for p in pids if diff[p] == "hard"]
    m.addConstr(quicksum(x[p] for p in hard) == 64, name="hard64")
    obj = quicksum((1 if diff[p] == "easy" else 2) * x[p] for p in pids)
    m.setObjective(obj, GRB.MINIMIZE)
    return m
