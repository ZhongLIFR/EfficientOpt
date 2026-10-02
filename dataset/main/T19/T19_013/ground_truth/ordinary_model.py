import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    requirements = instance["requirements"]
    options = instance["options"]
    model = gp.Model("ordinary_explicit_requirement_allocation")
    select = model.addVars(len(options), vtype=GRB.BINARY, name="select")
    allocation = model.addVars(
        len(requirements), len(options), lb=0.0, name="allocation"
    )
    capacity_lookup = []
    for option_index, option in enumerate(options):
        capacities = {
            entry["requirement"]: entry["amount"]
            for entry in option["capacities"]
        }
        capacity_lookup.append(capacities)
    for requirement_index in range(len(requirements)):
        for option_index in range(len(options)):
            capacity = capacity_lookup[option_index].get(requirement_index, 0)
            model.addConstr(
                allocation[requirement_index, option_index]
                <= capacity * select[option_index],
                name=f"link[{requirement_index},{option_index}]",
            )
    for requirement_index, requirement in enumerate(requirements):
        model.addConstr(
            gp.quicksum(
                allocation[requirement_index, option_index]
                for option_index in range(len(options))
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
