import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    """Literal absolute-value/max formulation of minimum peak acceleration."""
    n = int(instance["periods"])
    bound = float(instance["acceleration_bound"])

    model = gp.Model("rocket_peak_ordinary")
    position = model.addVars(n + 1, lb=-GRB.INFINITY, name="position")
    velocity = model.addVars(n + 1, lb=-GRB.INFINITY, name="velocity")
    acceleration = model.addVars(n, lb=-bound, ub=bound, name="acceleration")
    absolute_acceleration = model.addVars(n, lb=0.0, name="absolute_acceleration")
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
        model.addGenConstrAbs(
            absolute_acceleration[period], acceleration[period], name=f"absolute_acceleration[{period}]"
        )
    model.addConstr(position[n] == float(instance["final_position"]), name="final_position")
    model.addConstr(velocity[n] == float(instance["final_velocity"]), name="final_velocity")
    model.addGenConstrMax(peak, list(absolute_acceleration.values()), name="maximum_acceleration")
    model.setObjective(peak, GRB.MINIMIZE)
    return model
