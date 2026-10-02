import gurobipy as gp
from gurobipy import GRB, quicksum
from collections import defaultdict

def build_model(instance):
    channels = instance['channels']
    segments = instance['segments']
    placement_costs = instance['placement_costs']
    
    chan_data = {c['id']: c for c in channels}
    seg_data = {s['id']: s for s in segments}
    
    seg_to_chans = defaultdict(list)
    chan_to_segs = defaultdict(list)
    cost_map = {}
    
    for pc in placement_costs:
        s_id = pc['segment']
        c_id = pc['channel']
        seg_to_chans[s_id].append(c_id)
        chan_to_segs[c_id].append(s_id)
        cost_map[(s_id, c_id)] = pc['cost_per_block']
        
    model = gp.Model()
    
    y = model.addVars(chan_data.keys(), vtype=GRB.BINARY, name="contract")
    x = model.addVars(cost_map.keys(), vtype=GRB.CONTINUOUS, lb=0, name="placement")
    
    rev_pts = {s_id: seg_data[s_id]['review_points_per_block'] for s_id in seg_data}
    
    for s_id in seg_data:
        req = seg_data[s_id]['required_impression_blocks']
        model.addConstr(
            quicksum(x[s_id, c_id] for c_id in seg_to_chans[s_id]) == req,
            name=f"demand_{s_id}"
        )
        
    for c_id in chan_data:
        imp_cap = chan_data[c_id]['impression_capacity_blocks']
        rev_cap = chan_data[c_id]['review_capacity_points']
        segs = chan_to_segs[c_id]
        
        model.addConstr(
            quicksum(x[s_id, c_id] for s_id in segs) <= imp_cap * y[c_id],
            name=f"imp_cap_{c_id}"
        )
        model.addConstr(
            quicksum(rev_pts[s_id] * x[s_id, c_id] for s_id in segs) <= rev_cap * y[c_id],
            name=f"rev_cap_{c_id}"
        )
        
    obj_contract = quicksum(chan_data[c_id]['contract_fee'] * y[c_id] for c_id in chan_data)
    obj_placement = quicksum(cost_map[(s_id, c_id)] * x[s_id, c_id] for s_id, c_id in cost_map)
    model.setObjective(obj_contract + obj_placement, GRB.MINIMIZE)
    
    return model