import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    model = gp.Model("campaign_contracting")
    
    # Parse instance data
    channels_data = instance['channels']
    segments_data = instance['segments']
    placement_costs_data = instance['placement_costs']
    
    # Build lookup dictionaries
    channel_dict = {ch['id']: ch for ch in channels_data}
    segment_dict = {seg['id']: seg for seg in segments_data}
    
    # Build sparse placement cost dictionary and valid pairs
    placement_cost = {}
    valid_pairs = set()
    for rec in placement_costs_data:
        s, c = rec['segment'], rec['channel']
        placement_cost[(s, c)] = rec['cost_per_block']
        valid_pairs.add((s, c))
    
    # Build reverse mapping: channel -> segments that can use it
    channel_to_segments = {ch['id']: [] for ch in channels_data}
    for seg in segments_data:
        for ch_id in seg['eligible_channels']:
            channel_to_segments[ch_id].append(seg['id'])
    
    # Decision variables
    # y[c]: whether channel c is contracted
    y = model.addVars(channel_dict.keys(), vtype=GRB.BINARY, name="contract")
    
    # x[s,c]: impression blocks of segment s on channel c (only for valid pairs)
    x = model.addVars(valid_pairs, vtype=GRB.CONTINUOUS, lb=0.0, name="blocks")
    
    # Objective: minimize contract fees + placement costs
    contract_cost = gp.quicksum(
        channel_dict[c]['contract_fee'] * y[c] for c in channel_dict
    )
    placement_cost_expr = gp.quicksum(
        placement_cost[(s, c)] * x[s, c] for (s, c) in valid_pairs
    )
    model.setObjective(contract_cost + placement_cost_expr, GRB.MINIMIZE)
    
    # Constraint 1: Each segment must receive its required impression blocks
    for seg_id, seg in segment_dict.items():
        eligible = seg['eligible_channels']
        model.addConstr(
            gp.quicksum(x[seg_id, c] for c in eligible if (seg_id, c) in valid_pairs)
            == seg['required_impression_blocks'],
            name=f"demand_{seg_id}"
        )
    
    # Constraint 2: Impression capacity per channel
    for ch_id, ch in channel_dict.items():
        segments_on_channel = channel_to_segments[ch_id]
        if segments_on_channel:
            model.addConstr(
                gp.quicksum(x[s, ch_id] for s in segments_on_channel if (s, ch_id) in valid_pairs)
                <= ch['impression_capacity_blocks'],
                name=f"imp_cap_{ch_id}"
            )
    
    # Constraint 3: Review capacity per channel
    for ch_id, ch in channel_dict.items():
        segments_on_channel = channel_to_segments[ch_id]
        if segments_on_channel:
            model.addConstr(
                gp.quicksum(
                    segment_dict[s]['review_points_per_block'] * x[s, ch_id]
                    for s in segments_on_channel if (s, ch_id) in valid_pairs
                )
                <= ch['review_capacity_points'],
                name=f"rev_cap_{ch_id}"
            )
    
    # Constraint 4: Linking - blocks can only be placed on contracted channels
    # Use indicator constraints: x[s,c] > 0 => y[c] = 1
    # Equivalently: x[s,c] <= M * y[c] where M is the segment's required blocks
    for (s, c) in valid_pairs:
        M = segment_dict[s]['required_impression_blocks']
        model.addConstr(
            x[s, c] <= M * y[c],
            name=f"link_{s}_{c}"
        )
    
    return model