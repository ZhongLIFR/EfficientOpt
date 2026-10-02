import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    feeders = instance["feeders"]
    load_groups = instance["load_groups"]
    restoration_costs = instance["restoration_costs"]

    feeder_info = {f["id"]: f for f in feeders}
    load_info = {lg["id"]: lg for lg in load_groups}
    cost_map = {(rc["load_group"], rc["feeder"]): rc["restoration_cost_per_kw"] for rc in restoration_costs}

    feeder_loads = {f_id: [] for f_id in feeder_info}
    eligible_pairs = []
    for lg in load_groups:
        lg_id = lg["id"]
        for f_id in lg["eligible_feeders"]:
            eligible_pairs.append((lg_id, f_id))
            feeder_loads[f_id].append(lg_id)

    m = gp.Model("microgrid_restoration")

    y = m.addVars(feeder_info.keys(), vtype=GRB.BINARY, name="y")
    x = m.addVars(eligible_pairs, lb=0.0, name="x")

    obj_energize = gp.quicksum(feeder_info[f_id]["energization_cost"] * y[f_id] for f_id in feeder_info)
    obj_restore = gp.quicksum(cost_map[pair] * x[pair] for pair in eligible_pairs)
    m.setObjective(obj_energize + obj_restore, GRB.MINIMIZE)

    for lg in load_groups:
        lg_id = lg["id"]
        m.addConstr(
            gp.quicksum(x[lg_id, f_id] for f_id in lg["eligible_feeders"]) == lg["required_power_kw"],
            name=f"demand_{lg_id}"
        )

    for f_id, f in feeder_info.items():
        loads = feeder_loads[f_id]
        if not loads:
            continue
        m.addConstr(
            gp.quicksum(x[lg_id, f_id] for lg_id in loads) <= f["power_capacity_kw"] * y[f_id],
            name=f"power_cap_{f_id}"
        )
        m.addConstr(
            gp.quicksum(load_info[lg_id]["switching_points_per_kw"] * x[lg_id, f_id] for lg_id in loads) <= f["switching_capacity_points"] * y[f_id],
            name=f"switch_cap_{f_id}"
        )

    return m