from __future__ import annotations
import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    data = instance
    sites = {s["id"]: s for s in data["sites"]}
    services = {w["id"]: w for w in data["services"]}
    costs = {(r["service"], r["site"]): float(r["unit_cost"]) for r in data["assignment_costs"]}
    arcs = sorted(costs)
    model = gp.Model("edge_computing_deployment")
    active = model.addVars(sorted(sites), vtype=GRB.BINARY, name="active")
    load = model.addVars(arcs, lb=0.0, vtype=GRB.CONTINUOUS, name="load")
    for service_id, service in services.items():
        model.addConstr(gp.quicksum(load[service_id, site] for site in service["eligible_sites"]) == service["compute_demand"], name=f"service_demand[{service_id}]")
    for site_id, site in sites.items():
        model.addConstr(gp.quicksum(load[service, j] for service, j in arcs if j == site_id) <= site["compute_capacity"] * active[site_id], name=f"site_capacity[{site_id}]")
    for service, site in arcs:
        model.addConstr(load[service, site] <= services[service]["compute_demand"] * active[site], name=f"service_site_activation[{{service}},{{site}}]")
    model.setObjective(gp.quicksum(sites[s]["activation_cost"] * active[s] for s in sites) + gp.quicksum(costs[a] * load[a] for a in arcs), GRB.MINIMIZE)
    return model
