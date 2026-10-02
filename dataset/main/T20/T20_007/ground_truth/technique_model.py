import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    missions = instance["missions"]
    mission_count = len(missions)
    horizon = instance["time_steps"]
    dt = instance["step_duration"]
    model = gp.Model("technique_sparse_trajectory_recurrence")
    acceleration = model.addVars(mission_count, horizon, lb=-GRB.INFINITY, name="acceleration")
    absolute = model.addVars(mission_count, horizon, lb=0.0, name="absolute_acceleration")
    position = model.addVars(mission_count, horizon + 1, lb=-GRB.INFINITY, name="position")
    velocity = model.addVars(mission_count, horizon + 1, lb=-GRB.INFINITY, name="velocity")
    for r, mission in enumerate(missions):
        for t in range(horizon):
            acceleration[r, t].LB = -mission["acceleration_bound"]
            acceleration[r, t].UB = mission["acceleration_bound"]
            model.addConstr(absolute[r, t] >= acceleration[r, t])
            model.addConstr(absolute[r, t] >= -acceleration[r, t])
            model.addConstr(velocity[r, t + 1] == velocity[r, t] + dt * acceleration[r, t])
            model.addConstr(position[r, t + 1] == position[r, t] + dt * velocity[r, t])
        model.addConstr(position[r, 0] == mission["initial_position"])
        model.addConstr(velocity[r, 0] == mission["initial_velocity"])
        model.addConstr(position[r, horizon] == mission["final_position"])
        model.addConstr(velocity[r, horizon] == mission["final_velocity"])
    for t in range(horizon):
        model.addConstr(
            gp.quicksum(absolute[r, t] for r in range(mission_count))
            <= instance["shared_absolute_acceleration_limit"]
        )
    model.setObjective(
        gp.quicksum(
            missions[r]["fuel_weight"] * absolute[r, t]
            for r in range(mission_count)
            for t in range(horizon)
        ),
        GRB.MINIMIZE,
    )
    return model
