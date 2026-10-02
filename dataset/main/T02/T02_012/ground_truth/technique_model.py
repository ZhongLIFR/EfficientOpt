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

    model = gp.Model("periodic_calibration_technique")
    coefficient = model.addVars(features, periods, lb=-GRB.INFINITY, name="coefficient")
    enabled = model.addVars(features, periods, vtype=GRB.BINARY, name="enabled")
    period_peak = model.addVars(periods, lb=0.0, name="period_peak") if loss == "cheb" else None
    absolute_residual = (
        model.addVars(periods, observations, lb=0.0, name="absolute_residual")
        if loss == "l1"
        else None
    )

    for period in range(periods):
        model.addConstr(
            gp.quicksum(enabled[feature, period] for feature in range(features)) <= feature_limit,
            name=f"feature_limit[{period}]",
        )
        for observation in range(observations):
            residual = gp.quicksum(
                coefficient[feature, period] * float(feature_values[period][observation][feature])
                for feature in range(features)
            ) - float(responses[period][observation])
            epigraph = period_peak[period] if loss == "cheb" else absolute_residual[period, observation]
            model.addConstr(epigraph >= residual, name=f"residual_upper[{period},{observation}]")
            model.addConstr(epigraph >= -residual, name=f"residual_lower[{period},{observation}]")

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
        gp.quicksum(period_peak.values())
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
