import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    arms = instance['arms']
    parts = instance['parts']
    slots = instance['processing_slots']
    arcs = instance['allowed_route_arcs']
    mutex = instance['mutex']

    arm_proc = {a['arm_id']: a['processing_time'] for a in arms}
    arm_ids = list(arm_proc.keys())

    part_info = {p['id']: p for p in parts}
    part_ids = list(part_info.keys())

    slot_info = {s['slot_id']: s for s in slots}
    slot_ids = list(slot_info.keys())

    part_slots = {}
    for s in slots:
        pid = s['part_id']
        if pid not in part_slots:
            part_slots[pid] = []
        part_slots[pid].append(s)
    for pid in part_slots:
        part_slots[pid].sort(key=lambda x: x['pass_index'])
        
    part_slot_ids = {p: [s['slot_id'] for s in part_slots[p]] for p in part_ids}

    arcs_out = {u: [] for u in ['SOURCE'] + slot_ids}
    arcs_in = {v: [] for v in slot_ids + ['SINK']}
    for arc in arcs:
        u, v, t = arc['from_slot'], arc['to_slot'], arc['setup_time']
        arcs_out[u].append((v, t))
        arcs_in[v].append((u, t))

    model = gp.Model()

    x = {}
    for a in arm_ids:
        for u in arcs_out:
            for v, t in arcs_out[u]:
                x[a, u, v] = model.addVar(vtype=GRB.BINARY, name=f"x_{a}_{u}_{v}")

    y = {}
    for a in arm_ids:
        for s in slot_ids:
            y[a, s] = model.addVar(vtype=GRB.BINARY, name=f"y_{a}_{s}")

    C = {}
    for a in arm_ids:
        for s in slot_ids:
            C[a, s] = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=512, name=f"C_{a}_{s}")

    z = {}
    for p in part_ids:
        z[p] = model.addVar(vtype=GRB.BINARY, name=f"z_{p}")

    model.update()

    M = 520

    for a in arm_ids:
        model.addConstr(gp.quicksum(x[a, 'SOURCE', v] for v, _ in arcs_out['SOURCE']) == 1)
        model.addConstr(gp.quicksum(x[a, u, 'SINK'] for u, _ in arcs_in['SINK']) == 1)
        for s in slot_ids:
            model.addConstr(gp.quicksum(x[a, u, s] for u, _ in arcs_in[s]) == y[a, s])
            model.addConstr(gp.quicksum(x[a, s, v] for v, _ in arcs_out[s]) == y[a, s])

    for s in slot_ids:
        model.addConstr(gp.quicksum(y[a, s] for a in arm_ids) <= 1)

    for a in arm_ids:
        proc = arm_proc[a]
        for v, t in arcs_out['SOURCE']:
            if v != 'SINK':
                model.addConstr(C[a, v] >= proc + t - M * (1 - x[a, 'SOURCE', v]))
        for u in slot_ids:
            for v, t in arcs_out[u]:
                if v != 'SINK':
                    model.addConstr(C[a, v] >= C[a, u] + proc + t - M * (1 - x[a, u, v]))

    for p in part_ids:
        demand = part_info[p]['demand']
        expr = gp.quicksum(arm_proc[a] * y[a, s] for a in arm_ids for s in part_slot_ids[p])
        model.addConstr(expr >= demand * z[p])
        model.addConstr(gp.quicksum(y[a, s] for a in arm_ids for s in part_slot_ids[p]) <= len(part_slot_ids[p]) * z[p])

    for p in part_ids:
        slots_p = part_slots[p]
        for i in range(len(slots_p) - 1):
            s_curr = slots_p[i]['slot_id']
            s_next = slots_p[i+1]['slot_id']
            model.addConstr(gp.quicksum(y[a, s_next] for a in arm_ids) <= gp.quicksum(y[a, s_curr] for a in arm_ids))
            for a in arm_ids:
                for b in arm_ids:
                    proc_a = arm_proc[a]
                    model.addConstr(C[a, s_next] - proc_a >= C[b, s_curr] - M * (2 - y[a, s_next] - y[b, s_curr]))
                    model.addConstr(C[a, s_next] - proc_a <= C[b, s_curr] + 5 + M * (2 - y[a, s_next] - y[b, s_curr]))

    for p in part_ids:
        recovery = part_info[p]['recovery_time']
        slots_p = part_slots[p]
        for i, s in enumerate(slots_p):
            sid = s['slot_id']
            higher_slots = [s_h['slot_id'] for s_h in slots_p[i+1:]]
            for a in arm_ids:
                higher_y = gp.quicksum(y[a_h, sh] for a_h in arm_ids for sh in higher_slots)
                model.addConstr(C[a, sid] + recovery <= 512 + M * (1 - y[a, sid]) + M * higher_y)

    for p in part_ids:
        start = part_info[p]['start_time']
        end = part_info[p]['end_time']
        for s in part_slots[p]:
            sid = s['slot_id']
            for a in arm_ids:
                proc = arm_proc[a]
                model.addConstr(C[a, sid] >= start + proc - M * (1 - y[a, sid]))
                model.addConstr(C[a, sid] <= end + M * (1 - y[a, sid]))

    for m in mutex:
        model.addConstr(z[m['id1']] + z[m['id2']] <= 1)

    model.setObjective(gp.quicksum(part_info[p]['demand'] * z[p] for p in part_ids), GRB.MAXIMIZE)

    return model