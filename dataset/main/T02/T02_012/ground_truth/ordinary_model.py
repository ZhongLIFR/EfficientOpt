import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    periods = int(instance["periods"])
    observations = int(instance["obs_per_period"])
    features = int(instance["features"])
    feature_limit = int(instance["max_features"])
    responses = instance["y"]
    feature_values = instance["F"]
    bounds = [float(value) for value in instance["coefficient_bounds"]]
    fixed_costs = [float(value) for value in instance["fixed"]]
    loss = instance["loss"]

    model = gp.Model("periodic_calibration_ordinary")
    coefficient = model.addVars(features, periods, lb=-GRB.INFINITY, name="coefficient")
    enabled = model.addVars(features, periods, vtype=GRB.BINARY, name="enabled")
    residual = model.addVars(periods, observations, lb=-GRB.INFINITY, name="residual")
    absolute_residual = model.addVars(periods, observations, lb=0.0, name="absolute_residual")
    period_peak = model.addVars(periods, lb=0.0, name="period_peak") if loss == "cheb" else None

    for period in range(periods):
        model.addConstr(
            gp.quicksum(enabled[feature, period] for feature in range(features)) <= feature_limit,
            name=f"feature_limit[{period}]",
        )
        for observation in range(observations):
            prediction = gp.quicksum(
                coefficient[feature, period] * float(feature_values[period][observation][feature])
                for feature in range(features)
            )
            model.addConstr(
                residual[period, observation] == prediction - float(responses[period][observation]),
                name=f"residual_definition[{period},{observation}]",
            )
            model.addGenConstrAbs(
                absolute_residual[period, observation],
                residual[period, observation],
                name=f"absolute_value[{period},{observation}]",
            )
        if loss == "cheb":
            model.addGenConstrMax(
                period_peak[period],
                [absolute_residual[period, observation] for observation in range(observations)],
                name=f"period_maximum[{period}]",
            )

    for feature in range(features):
        for period in range(periods):
            model.addConstr(
                coefficient[feature, period] <= bounds[feature] * enabled[feature, period],
                name=f"coefficient_upper[{feature},{period}]",
            )
            model.addConstr(
                coefficient[feature, period] >= -bounds[feature] * enabled[feature, period],
                name=f"coefficient_lower[{feature},{period}]",
            )
        for period in range(periods - 1):
            model.addConstr(
                enabled[feature, period] >= enabled[feature, period + 1],
                name=f"disablement_persistence[{feature},{period}]",
            )

    fitting_loss = (
        gp.quicksum(period_peak[period] for period in range(periods))
        if loss == "cheb"
        else gp.quicksum(absolute_residual.values())
    )
    enabling_cost = gp.quicksum(
        fixed_costs[feature] * enabled[feature, period]
        for feature in range(features)
        for period in range(periods)
    )
    model.setObjective(fitting_loss + enabling_cost, GRB.MINIMIZE)
    return model
