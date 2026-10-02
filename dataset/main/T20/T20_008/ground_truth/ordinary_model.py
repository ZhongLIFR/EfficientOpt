import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    missions = instance["missions"]
    mission_count = len(missions)
    horizon = instance["time_steps"]
    dt = instance["step_duration"]
    model = gp.Model("ordinary_cumulative_trajectory_expansion")
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
        model.addConstr(position[r, 0] == mission["initial_position"])
        model.addConstr(velocity[r, 0] == mission["initial_velocity"])
        for t in range(1, horizon + 1):
            model.addConstr(
                velocity[r, t]
                == mission["initial_velocity"]
                + gp.quicksum(dt * acceleration[r, k] for k in range(t))
            )
            model.addConstr(
                position[r, t]
                == mission["initial_position"]
                + t * dt * mission["initial_velocity"]
                + gp.quicksum(
                    (t - 1 - k) * dt * dt * acceleration[r, k]
                    for k in range(t - 1)
                )
            )
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
