import gurobipy as gp
from gurobipy import GRB


def _maximum_clique_size(vertex_count, edges):
    adjacency = [0] * vertex_count
    for left, right in edges:
        adjacency[left] |= 1 << right
        adjacency[right] |= 1 << left

    best = 0

    def color_order(candidates):
        order = []
        bounds = []
        remaining = candidates
        color = 0
        while remaining:
            color += 1
            available = remaining
            while available:
                bit = available & -available
                vertex = bit.bit_length() - 1
                order.append(vertex)
                bounds.append(color)
                remaining &= ~bit
                available &= ~bit
                available &= ~adjacency[vertex]
        return order, bounds

    def expand(candidates, size):
        nonlocal best
        if not candidates:
            best = max(best, size)
            return
        order, bounds = color_order(candidates)
        for index in range(len(order) - 1, -1, -1):
            if size + bounds[index] <= best:
                return
            vertex = order[index]
            bit = 1 << vertex
            if candidates & bit:
                expand(candidates & adjacency[vertex], size + 1)
                candidates &= ~bit

    expand((1 << vertex_count) - 1, 0)
    return best


def build_model(instance):
    rows = instance["rows"]
    coordination = instance["coordination"]
    task_count = int(coordination["num_tasks"])
    window_count = int(coordination["num_windows"])
    edges = [tuple(map(int, edge)) for edge in coordination["conflict_edges"]]

    model = gp.Model("bounded_planning_technique")
    x = model.addVars(
        len(rows), vtype=GRB.INTEGER,
        lb=[int(row["x_over_y"]) + int(row["y_over_z"]) for row in rows],
        ub=[int(row["ub_x"]) for row in rows], name="x",
    )
    y = model.addVars(
        len(rows), vtype=GRB.INTEGER,
        lb=[int(row["y_over_z"]) for row in rows],
        ub=[int(row["ub_y"]) for row in rows], name="y",
    )
    z = model.addVars(
        len(rows), vtype=GRB.INTEGER, lb=0,
        ub=[int(row["ub_z"]) for row in rows], name="z",
    )

    model.addConstrs(
        (x[r] + y[r] + z[r] <= int(rows[r]["capacity"]) for r in range(len(rows))),
        name="capacity",
    )
    model.addConstrs(
        (x[r] - y[r] >= int(rows[r]["x_over_y"]) for r in range(len(rows))),
        name="x_over_y",
    )
    model.addConstrs(
        (y[r] - z[r] >= int(rows[r]["y_over_z"]) for r in range(len(rows))),
        name="y_over_z",
    )

    assigned = model.addVars(task_count, window_count, vtype=GRB.BINARY, name="assigned")
    used = model.addVars(window_count, vtype=GRB.BINARY, name="used")
    clique_lower_bound = _maximum_clique_size(task_count, edges)
    for window in range(clique_lower_bound):
        used[window].LB = 1
    model.addConstrs(
        (gp.quicksum(assigned[task, window] for window in range(window_count)) == 1
         for task in range(task_count)),
        name="task_once",
    )
    model.addConstrs(
        (used[window] >= used[window + 1] for window in range(window_count - 1)),
        name="used_order",
    )
    model.addConstrs(
        (assigned[task, window] <= used[window]
         for task in range(task_count) for window in range(window_count)),
        name="activation",
    )
    model.addConstrs(
        (assigned[left, window] + assigned[right, window] <= used[window]
         for left, right in edges for window in range(window_count)),
        name="conflict",
    )

    row_cost = gp.quicksum(
        float(row["cost_x"]) * x[r]
        + float(row["cost_y"]) * y[r]
        + float(row["cost_z"]) * z[r]
        for r, row in enumerate(rows)
    )
    window_cost = float(coordination["window_activation_cost"]) * gp.quicksum(used.values())
    model.setObjective(row_cost + window_cost, GRB.MINIMIZE)
    return model
