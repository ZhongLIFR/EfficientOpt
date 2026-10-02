from collections import defaultdict

import gurobipy as gp
from gurobipy import GRB


TECHNIQUE = False
REQUIRED_HARD_PACKAGES = 65
HARD_QUOTA_IS_EXACT = False


def _load_relations(instance):
    cost = {
        int(record["package_id"]): 1 if str(record["difficulty"]) == "easy" else 2
        for record in instance["package_difficulty"]
    }
    coverage = defaultdict(set)
    task_packages = defaultdict(list)
    for record in instance["package_task"]:
        package_id = int(record["package_id"])
        task_id = int(record["task_id"])
        coverage[package_id].add(task_id)
        task_packages[task_id].append(package_id)
    for package_id in cost:
        coverage[package_id]
    return cost, coverage, task_packages


def _find_dominated_packages(cost, coverage):
    task_packages = defaultdict(list)
    for package_id, tasks in coverage.items():
        for task_id in tasks:
            task_packages[task_id].append(package_id)
    dominated = set()
    for package_id in sorted(cost):
        tasks = coverage[package_id]
        if not tasks:
            dominated.add(package_id)
            continue
        anchor = min(tasks, key=lambda task_id: len(task_packages[task_id]))
        for replacement_id in task_packages[anchor]:
            if replacement_id == package_id or cost[replacement_id] != cost[package_id]:
                continue
            replacement_tasks = coverage[replacement_id]
            if len(replacement_tasks) < len(tasks):
                continue
            if tasks.issubset(replacement_tasks) and (
                tasks != replacement_tasks or replacement_id < package_id
            ):
                dominated.add(package_id)
                break
    return dominated


def build_model(instance):
    cost, coverage, task_packages = _load_relations(instance)
    dominated = _find_dominated_packages(cost, coverage) if TECHNIQUE else set()
    active_packages = [
        package_id for package_id in sorted(cost) if package_id not in dominated
    ]
    active_set = set(active_packages)

    model = gp.Model("same_difficulty_dominance" if TECHNIQUE else "all_packages")
    selected = model.addVars(active_packages, vtype=GRB.BINARY, name="selected")
    model.setObjective(
        gp.quicksum(cost[package_id] * selected[package_id] for package_id in active_packages),
        GRB.MINIMIZE,
    )
    task_ids = sorted(task_packages)
    for task_id in task_ids:
        members = [
            package_id
            for package_id in task_packages[task_id]
            if package_id in active_set
        ]
        if not members:
            raise ValueError(f"no active package covers task {task_id}")
        model.addConstr(
            gp.quicksum(selected[package_id] for package_id in members) >= 1,
            name=f"cover[{task_id}]",
        )
    hard_count = gp.quicksum(
        selected[package_id]
        for package_id in active_packages
        if cost[package_id] == 2
    )
    if HARD_QUOTA_IS_EXACT:
        model.addConstr(hard_count == REQUIRED_HARD_PACKAGES, name="required_hard_packages")
    else:
        model.addConstr(hard_count >= REQUIRED_HARD_PACKAGES, name="minimum_hard_packages")
    return model
