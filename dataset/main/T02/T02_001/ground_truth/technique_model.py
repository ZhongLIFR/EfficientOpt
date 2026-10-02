import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    """Direct epigraph formulation of minimum peak acceleration."""
    n = int(instance["periods"])
    bound = float(instance["acceleration_bound"])

    model = gp.Model("rocket_peak_technique")
    position = model.addVars(n + 1, lb=-GRB.INFINITY, name="position")
    velocity = model.addVars(n + 1, lb=-GRB.INFINITY, name="velocity")
    acceleration = model.addVars(n, lb=-bound, ub=bound, name="acceleration")
    peak = model.addVar(lb=0.0, name="peak_acceleration")

    model.addConstr(position[0] == float(instance["initial_position"]), name="initial_position")
    model.addConstr(velocity[0] == float(instance["initial_velocity"]), name="initial_velocity")
    for period in range(n):
        model.addConstr(
            position[period + 1] == position[period] + velocity[period],
            name=f"position_balance[{period}]",
        )
        model.addConstr(
            velocity[period + 1] == velocity[period] + acceleration[period],
            name=f"velocity_balance[{period}]",
        )
        model.addConstr(peak >= acceleration[period], name=f"positive_peak[{period}]")
        model.addConstr(peak >= -acceleration[period], name=f"negative_peak[{period}]")
    model.addConstr(position[n] == float(instance["final_position"]), name="final_position")
    model.addConstr(velocity[n] == float(instance["final_velocity"]), name="final_velocity")
    model.setObjective(peak, GRB.MINIMIZE)
    return model
