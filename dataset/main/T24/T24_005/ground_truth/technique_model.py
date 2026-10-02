import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T24_11 technique candidate: dominance-reduced set cover.

    Same semantics as ordinary. A package is removed when another package of
    the SAME difficulty covers a superset of its tasks at the same unit cost
    (difficulty classes are preserved, so the exact-64 hard constraint and the
    cost scale are unaffected). Column count after reduction is typically far
    smaller than 63k.
    """
    diff = {int(r["package_id"]): r["difficulty"] for r in instance["package_difficulty"]}
    tasks_by_pkg = {}
    for rec in instance["package_task"]:
        tasks_by_pkg.setdefault(int(rec["package_id"]), []).append(int(rec["task_id"]))
    pids = sorted(tasks_by_pkg)
    task_ids = sorted({t for lst in tasks_by_pkg.values() for t in lst})
    t2i = {t: i for i, t in enumerate(task_ids)}

    masks = {}
    for p in pids:
        mask = 0
        for t in tasks_by_pkg[p]:
            mask |= 1 << t2i[t]
        masks[p] = (mask, diff[p])

    # same-difficulty superset dominance
    by_diff = {"easy": [], "hard": []}
    for p, (mask, d) in masks.items():
        by_diff[d].append((p, mask))
    keep = []
    for d in ("easy", "hard"):
        arr = sorted(by_diff[d], key=lambda pm: -pm[1].bit_count())
        kept = []
        for p, mask in arr:
            dom = False
            for q, mq in kept:
                if mq & mask == mask:  # q covers superset of p
                    dom = True
                    break
            if not dom:
                kept.append((p, mask))
                keep.append(p)
    keep = sorted(keep)

    cover = {t: [] for t in task_ids}
    for p in keep:
        for t in tasks_by_pkg[p]:
            cover[t].append(p)

    m = gp.Model("t24_11_setcover_dom")
    x = m.addVars(keep, vtype=GRB.BINARY, name="x")
    for t in task_ids:
        m.addConstr(quicksum(x[p] for p in cover[t]) >= 1, name=f"cov_{t}")
    hard = [p for p in keep if diff[p] == "hard"]
    m.addConstr(quicksum(x[p] for p in hard) == 64, name="hard64")
    obj = quicksum((1 if diff[p] == "easy" else 2) * x[p] for p in keep)
    m.setObjective(obj, GRB.MINIMIZE)
    m._nkeep = len(keep)
    return m
