import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    feeders = instance['feeders']
    load_groups = instance['load_groups']
    restoration_costs = instance['restoration_costs']
    
    # Build lookup dictionaries for efficiency
    feeder_dict = {f['id']: f for f in feeders}
    load_group_dict = {lg['id']: lg for lg in load_groups}
    
    # Build restoration cost lookup: (load_group, feeder) -> cost_per_kw
    resto_cost = {(rc['load_group'], rc['feeder']): rc['restoration_cost_per_kw'] 
                  for rc in restoration_costs}
    
    # Build reverse mapping: feeder -> list of eligible load groups
    feeder_to_loads = {f['id']: [] for f in feeders}
    for lg in load_groups:
        for fid in lg['eligible_feeders']:
            feeder_to_loads[fid].append(lg['id'])
    
    model = gp.Model('microgrid_restoration')
    
    # Decision variables
    # y[f]: whether feeder f is energized
    y = model.addVars(feeder_dict.keys(), vtype=GRB.BINARY, name='energized')
    
    # x[g,f]: kW restored from load group g by feeder f (only for eligible pairs)
    x = {}
    for lg in load_groups:
        g_id = lg['id']
        for f_id in lg['eligible_feeders']:
            x[g_id, f_id] = model.addVar(lb=0.0, vtype=GRB.CONTINUOUS, 
                                         name=f'restore_{g_id}_{f_id}')
    
    # Objective: minimize total cost
    energization_cost = gp.quicksum(feeder_dict[f_id]['energization_cost'] * y[f_id] 
                                    for f_id in feeder_dict)
    restoration_cost = gp.quicksum(resto_cost[g_id, f_id] * x[g_id, f_id] 
                                   for (g_id, f_id) in x)
    model.setObjective(energization_cost + restoration_cost, GRB.MINIMIZE)
    
    # Constraint 1: Full restoration for each load group
    for lg in load_groups:
        g_id = lg['id']
        model.addConstr(
            gp.quicksum(x[g_id, f_id] for f_id in lg['eligible_feeders']) == lg['required_power_kw'],
            name=f'full_restore_{g_id}'
        )
    
    # Constraint 2: Power capacity for each feeder
    for f_id, lg_list in feeder_to_loads.items():
        if lg_list:  # only add constraint if feeder has eligible loads
            model.addConstr(
                gp.quicksum(x[g_id, f_id] for g_id in lg_list) <= feeder_dict[f_id]['power_capacity_kw'],
                name=f'power_cap_{f_id}'
            )
    
    # Constraint 3: Switching capacity for each feeder
    for f_id, lg_list in feeder_to_loads.items():
        if lg_list:
            model.addConstr(
                gp.quicksum(load_group_dict[g_id]['switching_points_per_kw'] * x[g_id, f_id] 
                           for g_id in lg_list) <= feeder_dict[f_id]['switching_capacity_points'],
                name=f'switch_cap_{f_id}'
            )
    
    # Constraint 4: Energization linkage (can only restore if feeder is energized)
    for lg in load_groups:
        g_id = lg['id']
        req_power = lg['required_power_kw']
        for f_id in lg['eligible_feeders']:
            model.addConstr(
                x[g_id, f_id] <= req_power * y[f_id],
                name=f'link_{g_id}_{f_id}'
            )
    
    return model