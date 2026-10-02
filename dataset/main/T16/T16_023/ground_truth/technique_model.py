import math
import gurobipy as gp
from gurobipy import GRB


MAX_ITERATIONS = 200


def solve_algorithm(instance, context):
    facility_count = int(instance["facility_count"])
    scenario_count = int(instance["scenario_count"])
    hire_cost = [float(v) for v in instance["hire_cost"]]
    capacity = [float(v) for v in instance["capacity"]]
    demand = [float(v) for v in instance["demand"]]
    availability = instance["availability"]
    service_cost = instance["service_cost"]
    shortage_penalty = float(instance["shortage_penalty"])
    probability = 1.0 / scenario_count

    master = gp.Model("t16_analytic_benders_master")
    opened = master.addVars(facility_count, vtype=GRB.BINARY, name="open")
    theta = master.addVar(lb=0.0, name="expected_recourse")
    master.setObjective(gp.quicksum(hire_cost[j] * opened[j] for j in range(facility_count)) + theta, GRB.MINIMIZE)

    scenario_data = []
    for s in range(scenario_count):
        costs = [float(v) for v in service_cost[s]]
        usable = [float(availability[s][j]) * capacity[j] for j in range(facility_count)]
        breakpoints = sorted({0.0, shortage_penalty} | {c for c in costs if 0.0 <= c <= shortage_penalty})
        scenario_data.append((demand[s], costs, usable, breakpoints))

    try:
        for iteration in range(MAX_ITERATIONS):
            status = context.optimize(master)
            if status != "OPTIMAL":
                return {"solver_status": status, "objective_value": None, "solution_summary": f"iterations={iteration}"}
            y = [float(opened[j].X) for j in range(facility_count)]
            theta_value = float(theta.X)
            chosen = []
            expected = 0.0
            for d, costs, usable, breakpoints in scenario_data:
                best_value = -math.inf
                best_pi = 0.0
                for pi in breakpoints:
                    value = d * pi - sum(usable[j] * y[j] * max(0.0, pi - costs[j]) for j in range(facility_count))
                    if value > best_value:
                        best_value, best_pi = value, pi
                chosen.append(best_pi)
                expected += probability * best_value
            if expected <= theta_value + 1e-6:
                return {
                    "solver_status": "OPTIMAL",
                    "objective_value": float(master.ObjVal),
                    "solution_summary": f"iterations={iteration + 1}; opened={sum(round(v) for v in y)}",
                }
            rhs = probability * gp.quicksum(
                d * pi - gp.quicksum(usable[j] * max(0.0, pi - costs[j]) * opened[j] for j in range(facility_count))
                for (d, costs, usable, _), pi in zip(scenario_data, chosen)
            )
            master.addConstr(theta >= rhs, name=f"benders_{iteration}")
        return {"solver_status": "TIME_LIMIT", "objective_value": None, "solution_summary": f"iterations={MAX_ITERATIONS}"}
    finally:
        master.dispose()
