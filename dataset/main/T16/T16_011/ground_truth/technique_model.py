import gurobipy as gp
from gurobipy import GRB


MAX_ITERATIONS = 120
RELATIVE_TOLERANCE = 1e-6


def solve_algorithm(instance, context):
    warehouses = instance["warehouses"]
    districts = instance["districts"]
    transport_cost = instance["transport_cost"]
    demand = instance["demand_by_scenario"]
    scenario_count = int(instance["scenario_count"])
    facility_count = len(warehouses)
    district_count = len(districts)
    probability = 1.0 / scenario_count

    recourse = gp.Model("t16_recourse")
    shipment = recourse.addVars(district_count, facility_count, scenario_count, lb=0.0, name="shipment")
    shortage = recourse.addVars(district_count, scenario_count, lb=0.0, name="shortage")
    demand_rows = recourse.addConstrs(
        (gp.quicksum(shipment[i, j, s] for j in range(facility_count)) + shortage[i, s]
         == demand[i][s] for i in range(district_count) for s in range(scenario_count)),
        name="demand",
    )
    capacity_rows = recourse.addConstrs(
        (gp.quicksum(shipment[i, j, s] for i in range(district_count)) <= 0.0
         for j in range(facility_count) for s in range(scenario_count)),
        name="capacity",
    )
    recourse.setObjective(
        probability * gp.quicksum(
            transport_cost[i][j] * shipment[i, j, s]
            for i in range(district_count) for j in range(facility_count) for s in range(scenario_count)
        ) + probability * gp.quicksum(
            districts[i]["shortage_penalty"] * shortage[i, s]
            for i in range(district_count) for s in range(scenario_count)
        ),
        GRB.MINIMIZE,
    )

    master = gp.Model("t16_benders_master")
    opened = master.addVars(facility_count, vtype=GRB.BINARY, name="lease")
    eta = master.addVars(scenario_count, lb=0.0, name="scenario_recourse")
    master.setObjective(
        gp.quicksum(warehouses[j]["lease_cost"] * opened[j] for j in range(facility_count))
        + gp.quicksum(eta[s] for s in range(scenario_count)),
        GRB.MINIMIZE,
    )

    upper_bound = None
    lower_bound = None
    iterations = 0
    last_opened = None
    try:
        for iteration in range(MAX_ITERATIONS):
            status = context.optimize(master)
            if status != "OPTIMAL":
                return {"solver_status": status, "objective_value": None, "solution_summary": f"iterations={iteration}"}
            lower_bound = float(master.ObjVal)
            last_opened = [int(round(opened[j].X)) for j in range(facility_count)]
            for j in range(facility_count):
                rhs = float(warehouses[j]["storage_capacity"]) * last_opened[j]
                for s in range(scenario_count):
                    capacity_rows[j, s].RHS = rhs
            status = context.optimize(recourse)
            if status != "OPTIMAL":
                return {"solver_status": status, "objective_value": None, "solution_summary": f"iterations={iteration}"}
            for s in range(scenario_count):
                cut = gp.quicksum(demand[i][s] * demand_rows[i, s].Pi for i in range(district_count))
                cut += gp.quicksum(
                    warehouses[j]["storage_capacity"] * capacity_rows[j, s].Pi * opened[j]
                    for j in range(facility_count)
                )
                master.addConstr(eta[s] >= cut, name=f"benders_{iteration}_{s}")
            upper_bound = sum(warehouses[j]["lease_cost"] * last_opened[j] for j in range(facility_count)) + float(recourse.ObjVal)
            iterations = iteration + 1
            if upper_bound - lower_bound <= RELATIVE_TOLERANCE * max(1.0, abs(upper_bound)):
                return {
                    "solver_status": "OPTIMAL",
                    "objective_value": upper_bound,
                    "solution_summary": f"iterations={iterations}; opened={sum(last_opened)}",
                }
        return {"solver_status": "TIME_LIMIT", "objective_value": None, "solution_summary": f"iterations={iterations}"}
    finally:
        master.dispose()
        recourse.dispose()
