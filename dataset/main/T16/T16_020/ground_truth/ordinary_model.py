import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    warehouses = instance["warehouses"]
    districts = instance["districts"]
    transport_cost = instance["transport_cost"]
    demand = instance["demand_by_scenario"]
    scenario_count = int(instance["scenario_count"])
    facility_count = len(warehouses)
    district_count = len(districts)
    model = gp.Model("t16_extensive_form")
    opened = model.addVars(facility_count, vtype=GRB.BINARY, name="lease")
    shipment = model.addVars(district_count, facility_count, scenario_count, lb=0.0, name="shipment")
    shortage = model.addVars(district_count, scenario_count, lb=0.0, name="shortage")
    for district in range(district_count):
        for scenario in range(scenario_count):
            model.addConstr(
                gp.quicksum(shipment[district, facility, scenario] for facility in range(facility_count))
                + shortage[district, scenario] == demand[district][scenario]
            )
    for facility in range(facility_count):
        capacity = warehouses[facility]["storage_capacity"]
        for scenario in range(scenario_count):
            model.addConstr(
                gp.quicksum(shipment[district, facility, scenario] for district in range(district_count))
                <= capacity * opened[facility]
            )
    probability = 1.0 / scenario_count
    model.setObjective(
        gp.quicksum(warehouses[facility]["lease_cost"] * opened[facility] for facility in range(facility_count))
        + probability * gp.quicksum(
            transport_cost[district][facility] * shipment[district, facility, scenario]
            for district in range(district_count)
            for facility in range(facility_count)
            for scenario in range(scenario_count)
        )
        + probability * gp.quicksum(
            districts[district]["shortage_penalty"] * shortage[district, scenario]
            for district in range(district_count)
            for scenario in range(scenario_count)
        ),
        GRB.MINIMIZE,
    )
    return model
