import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    requirements = instance["requirements"]
    options = instance["options"]
    model = gp.Model("technique_compact_requirement_cover")
    select = model.addVars(len(options), vtype=GRB.BINARY, name="select")
    by_requirement = [[] for _ in requirements]
    for option_index, option in enumerate(options):
        for entry in option["capacities"]:
            by_requirement[entry["requirement"]].append(
                (option_index, entry["amount"])
            )
    for requirement_index, requirement in enumerate(requirements):
        model.addConstr(
            gp.quicksum(
                amount * select[option_index]
                for option_index, amount in by_requirement[requirement_index]
            )
            >= requirement["demand"],
            name=f"requirement[{requirement_index}]",
        )
    model.setObjective(
        gp.quicksum(
            option["fixed_cost"] * select[option_index]
            for option_index, option in enumerate(options)
        ),
        GRB.MINIMIZE,
    )
    return model
