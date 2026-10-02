import gurobipy as gp
from collections import defaultdict

def build_model(instance):
    model = gp.Model()

    slots_data = instance['slots']
    segments_data = instance['segments']
    actions_data = instance['actions']
    ac_data = instance['action_contributions']
    nodes_data = instance['nodes']
    eqs_data = instance['equations']
    eq_terms_data = instance['equation_terms']
    fb_data = instance['fallback']
    fb_bounds_data = instance['fallback_bounds']

    slot_req = {s['slot_id']: s['requirement'] for s in slots_data}
    fb_bounds = {fb['fallback_id']: fb for fb in fb_bounds_data}

    # Map segments/actions to their switch node ids
    seg_to_nodes = defaultdict(list)
    act_to_nodes = defaultdict(list)
    for n in nodes_data:
        if n['node_kind'] == 'segment_switch':
            seg_to_nodes[n['ref_id']].append(n['node_id'])
        elif n['node_kind'] == 'action_switch':
            act_to_nodes[n['ref_id']].append(n['node_id'])

    # Create all node binary variables
    node_ids = [n['node_id'] for n in nodes_data]
    node_vars = model.addVars(node_ids, vtype=gp.GRB.BINARY, name="n")

    # Segment enable variables: reuse switch node var if available
    seg_enable = {}
    extra_se = []
    for s in segments_data:
        sid = s['segment_id']
        if sid in seg_to_nodes:
            seg_enable[sid] = node_vars[seg_to_nodes[sid][0]]
        else:
            extra_se.append(sid)
    if extra_se:
        extra_se_v = model.addVars(extra_se, vtype=gp.GRB.BINARY, name="se")
        for sid in extra_se:
            seg_enable[sid] = extra_se_v[sid]

    # Equality for segments with multiple switch nodes
    for sid, nids in seg_to_nodes.items():
        for nid in nids[1:]:
            model.addConstr(node_vars[nid] == node_vars[nids[0]])

    # Action select variables: reuse switch node var if available
    action_select = {}
    extra_as = []
    for a in actions_data:
        aid = a['action_id']
        if aid in act_to_nodes:
            action_select[aid] = node_vars[act_to_nodes[aid][0]]
        else:
            extra_as.append(aid)
    if extra_as:
        extra_as_v = model.addVars(extra_as, vtype=gp.GRB.BINARY, name="as")
        for aid in extra_as:
            action_select[aid] = extra_as_v[aid]

    # Equality for actions with multiple switch nodes
    for aid, nids in act_to_nodes.items():
        for nid in nids[1:]:
            model.addConstr(node_vars[nid] == node_vars[nids[0]])

    # Segment coverage continuous variables
    seg_ids = [s['segment_id'] for s in segments_data]
    seg_ub = {s['segment_id']: s['threshold_high'] for s in segments_data}
    seg_coverage = model.addVars(seg_ids, lb=0, ub=seg_ub, name="sc")

    # Segment coverage bounds when enabled
    for s in segments_data:
        sid = s['segment_id']
        e = seg_enable[sid]
        c = seg_coverage[sid]
        model.addConstr(c <= s['threshold_high'] * e)
        model.addConstr(c >= s['threshold_low'] * e)

    # Fallback variables
    fallback_vars = {}
    for f in fb_data:
        fid = f['fallback_id']
        if fid in fb_bounds:
            b = fb_bounds[fid]
            fallback_vars[fid] = model.addVar(lb=b['min_amount'], ub=b['max_amount'], name=f"fb_{fid}")
        else:
            fallback_vars[fid] = model.addVar(lb=0, name=f"fb_{fid}")

    # Group data by slot for coverage constraints
    slot_segs = defaultdict(list)
    for s in segments_data:
        slot_segs[s['slot_id']].append(s['segment_id'])

    slot_ac = defaultdict(list)
    for ac in ac_data:
        slot_ac[ac['slot_id']].append((ac['action_id'], ac['contribution']))

    slot_fb = defaultdict(list)
    for f in fb_data:
        slot_fb[f['slot_id']].append(f['fallback_id'])

    for sid, req in slot_req.items():
        expr = gp.quicksum(seg_coverage[seg_id] for seg_id in slot_segs[sid]) \
             + gp.quicksum(contrib * action_select[aid] for aid, contrib in slot_ac[sid]) \
             + gp.quicksum(fallback_vars[fid] for fid in slot_fb[sid])
        model.addConstr(expr == req)

    # Policy equations
    eq_terms = defaultdict(list)
    for et in eq_terms_data:
        eq_terms[et['eq_id']].append((et['node_id'], et['sign']))

    for eq in eqs_data:
        eid = eq['eq_id']
        rhs = eq['rhs']
        expr = gp.quicksum(sign * node_vars[nid] for nid, sign in eq_terms[eid])
        model.addConstr(expr == rhs)

    # Objective
    obj = gp.quicksum(s['unit_price'] * seg_coverage[s['segment_id']] for s in segments_data) \
        + gp.quicksum(a['fixed_price'] * action_select[a['action_id']] for a in actions_data) \
        + gp.quicksum(n['price'] * node_vars[n['node_id']] for n in nodes_data) \
        + gp.quicksum(f['unit_price'] * fallback_vars[f['fallback_id']] for f in fb_data)

    model.setObjective(obj, gp.GRB.MINIMIZE)

    return model