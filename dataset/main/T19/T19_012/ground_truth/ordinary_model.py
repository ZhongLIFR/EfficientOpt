import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    requirements = instance["requirements"]
    options = instance["options"]
    model = gp.Model("ordinary_explicit_binary_assignment")
    select = model.addVars(len(options), vtype=GRB.BINARY, name="select")

    by_requirement = [[] for _ in requirements]
    for option_index, option in enumerate(options):
        for entry in option["capacities"]:
            if entry["amount"] > 0:
                by_requirement[entry["requirement"]].append(option_index)

    assign = {}
    for requirement_index, requirement in enumerate(requirements):
        demand = int(requirement["demand"])
        coverers = by_requirement[requirement_index]
        for slot in range(demand):
            for option_index in coverers:
                assign[requirement_index, slot, option_index] = model.addVar(
                    vtype=GRB.BINARY,
                    name=f"assign[{requirement_index},{slot},{option_index}]",
                )
                model.addConstr(
                    assign[requirement_index, slot, option_index] <= select[option_index],
                    name=f"link[{requirement_index},{slot},{option_index}]",
                )
            model.addConstr(
                gp.quicksum(assign[requirement_index, slot, option_index]
                            for option_index in coverers) == 1,
                name=f"slot[{requirement_index},{slot}]",
            )
        for option_index in coverers:
            model.addConstr(
                gp.quicksum(assign[requirement_index, slot, option_index]
                            for slot in range(demand)) <= 1,
                name=f"distinct[{requirement_index},{option_index}]",
            )

    model.setObjective(
        gp.quicksum(option["fixed_cost"] * select[option_index]
                    for option_index, option in enumerate(options)),
        GRB.MINIMIZE,
    )
    return model
