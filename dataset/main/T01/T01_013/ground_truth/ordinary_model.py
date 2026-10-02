import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    orders = instance["work_orders"]
    resource_capacities = instance["resource_capacities"]
    minimum_service_scores = instance["minimum_service_scores"]
    segments = {row["segment"]: row for row in instance["segment_limits"]}

    model = gp.Model("two_plan_portfolio_explicit_pair")
    choose_a = {}
    choose_b = {}
    for i, row in enumerate(orders):
        choose_a[i] = model.addVar(vtype=GRB.BINARY, name=f"choose_a[{i}]")
        choose_b[i] = model.addVar(vtype=GRB.BINARY, name=f"choose_b[{i}]")
        model.addConstr(choose_a[i] + choose_b[i] == 1, name=f"one_plan[{i}]")

    for r, capacity in enumerate(resource_capacities):
        model.addConstr(
            gp.quicksum(
                row["resource_a"][r] * choose_a[i] + row["resource_b"][r] * choose_b[i]
                for i, row in enumerate(orders)
            ) <= capacity,
            name=f"resource[{r}]",
        )

    for s, minimum in enumerate(minimum_service_scores):
        model.addConstr(
            gp.quicksum(
                row["service_a"][s] * choose_a[i] + row["service_b"][s] * choose_b[i]
                for i, row in enumerate(orders)
            ) >= minimum,
            name=f"service[{s}]",
        )

    by_segment = {segment: [] for segment in segments}
    for i, row in enumerate(orders):
        by_segment[row["segment"]].append(i)
    for segment, indices in by_segment.items():
        limits = segments[segment]
        total_b = gp.quicksum(choose_b[i] for i in indices)
        model.addConstr(total_b >= limits["minimum_plan_b"], name=f"segment_min[{segment}]")
        model.addConstr(total_b <= limits["maximum_plan_b"], name=f"segment_max[{segment}]")

    model.setObjective(
        gp.quicksum(
            row["cost_a"] * choose_a[i] + row["cost_b"] * choose_b[i]
            for i, row in enumerate(orders)
        ),
        GRB.MINIMIZE,
    )
    return model
