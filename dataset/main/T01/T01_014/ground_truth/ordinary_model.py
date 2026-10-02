import gurobipy as gp
from gurobipy import GRB


def _derived_anchor_clique(num_tasks, edges):
    adjacency = [set() for _ in range(num_tasks)]
    for first, second in edges:
        adjacency[first].add(second)
        adjacency[second].add(first)
    best = []
    starts = sorted(range(num_tasks), key=lambda task: (-len(adjacency[task]), task))
    for start in starts:
        clique = [start]
        candidates = set(adjacency[start])
        while candidates:
            task = max(
                candidates,
                key=lambda item: (len(candidates & adjacency[item]), len(adjacency[item]), -item),
            )
            clique.append(task)
            candidates &= adjacency[task]
        if len(clique) > len(best):
            best = clique
    return best


def build_model(instance):
    model = gp.Model("equality_coordination_ordinary")
    categories = instance["categories"]
    rows = instance["rows"]
    num_categories = len(categories)
    allocation = model.addVars(
        len(rows), num_categories, vtype=GRB.INTEGER, lb=0, name="allocation"
    )
    allocation_cost = gp.quicksum(
        float(row["cost"][category]) * allocation[row_index, category]
        for row_index, row in enumerate(rows)
        for category in range(num_categories)
    )
    for row_index, row in enumerate(rows):
        expression = gp.quicksum(
            float(row["eq_coeff"][category]) * allocation[row_index, category]
            for category in range(num_categories)
        )
        model.addConstr(expression >= float(row["minimum_required"]), name=f"minimum_required[{row_index}]")
        model.addConstr(expression <= float(row["maximum_available"]), name=f"maximum_available[{row_index}]")
        for side_index, side in enumerate(row["side"]):
            side_expression = gp.quicksum(
                float(side["coeff"][category]) * allocation[row_index, category]
                for category in range(num_categories)
            )
            if side["sense"] == "<=":
                model.addConstr(side_expression <= float(side["rhs"]), name=f"side_le[{row_index},{side_index}]")
            elif side["sense"] == ">=":
                model.addConstr(side_expression >= float(side["rhs"]), name=f"side_ge[{row_index},{side_index}]")
            else:
                raise ValueError(f"unsupported side-constraint sense: {side['sense']}")

    coordination = instance["coordination"]
    num_tasks = int(coordination["num_tasks"])
    num_windows = int(coordination["num_windows"])
    edges = [(int(edge[0]), int(edge[1])) for edge in coordination["conflict_edges"]]
    used = model.addVars(num_windows, vtype=GRB.BINARY, name="window_used")
    assigned = model.addVars(num_tasks, num_windows, vtype=GRB.BINARY, name="task_window")
    model.addConstrs(
        (gp.quicksum(assigned[task, window] for window in range(num_windows)) >= 1 for task in range(num_tasks)),
        name="task_at_least_once",
    )
    model.addConstrs(
        (gp.quicksum(assigned[task, window] for window in range(num_windows)) <= 1 for task in range(num_tasks)),
        name="task_at_most_once",
    )
    model.addConstrs((used[window] >= used[window + 1] for window in range(num_windows - 1)), name="used_order")
    model.addConstrs(
        (assigned[task, window] <= used[window] for task in range(num_tasks) for window in range(num_windows)),
        name="activation",
    )
    model.addConstrs(
        (assigned[first, window] + assigned[second, window] <= used[window]
         for first, second in edges for window in range(num_windows)),
        name="conflict",
    )
    for window, task in enumerate(_derived_anchor_clique(num_tasks, edges)):
        model.addConstr(assigned[task, window] == 1, name=f"symmetry_anchor[{task},{window}]")

    activation_cost = float(coordination["window_activation_cost"]) * gp.quicksum(used.values())
    model.setObjective(allocation_cost + activation_cost, GRB.MINIMIZE)
    model.update()
    return model
