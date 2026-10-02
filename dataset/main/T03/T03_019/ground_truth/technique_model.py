from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def _greedy_clique(task_count, edges):
    adjacency = [set() for _ in range(task_count)]
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    start = max(range(task_count), key=lambda v: (len(adjacency[v]), -v))
    clique = [start]
    candidates = set(adjacency[start])
    while candidates:
        vertex = max(candidates, key=lambda v: (len(candidates & adjacency[v]), len(adjacency[v]), -v))
        clique.append(vertex)
        candidates &= adjacency[vertex]
    return clique


def build_model(instance: dict) -> gp.Model:
    task_count = int(instance["num_tasks"])
    window_count = int(instance["num_windows"])
    edges = [(int(a), int(b)) for a, b in instance["conflict_edges"]]
    model = gp.Model("coloring_clique_bound")
    assigned = model.addVars(task_count, window_count, vtype=GRB.BINARY, name="assigned")
    used = model.addVars(window_count, vtype=GRB.BINARY, name="used")
    clique = _greedy_clique(task_count, edges)
    for w in range(len(clique)):
        used[w].LB = 1
    model.addConstrs((gp.quicksum(assigned[t, w] for w in range(window_count)) == 1 for t in range(task_count)), name="task_once")
    model.addConstrs((used[w] >= used[w + 1] for w in range(window_count - 1)), name="used_order")
    model.addConstrs((assigned[t, w] <= used[w] for t in range(task_count) for w in range(window_count)), name="activation")
    model.addConstrs((assigned[a, w] + assigned[b, w] <= used[w] for a, b in edges for w in range(window_count)), name="conflict")
    model.setObjective(float(instance["window_cost"]) * gp.quicksum(used.values()), GRB.MINIMIZE)
    return model
