import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    def rec_to_dict(rec, cols):
        if isinstance(rec, dict):
            return rec
        return {c: rec[i] for i, c in enumerate(cols)}

    entity_cols = instance.get('entity_columns', [
        'entity_id', 'label', 'row_min', 'row_max', 'col_min', 'col_max', 'anchor_row', 'anchor_col'
    ])
    nonoverlap_cols = instance.get('non_overlap_columns', [
        'pair_id', 'first_entity_id', 'second_entity_id',
        'row_gap_first_before_second', 'row_gap_second_before_first',
        'column_gap_first_before_second', 'column_gap_second_before_first'
    ])
    relationship_cols = instance.get('relationship_columns', [
        'relationship_id', 'first_entity_id', 'second_entity_id', 'importance_weight',
        'minimum_total_connector_span'
    ])
    calibration_cols = instance.get('connector_axis_columns', [
        'relationship_id', 'axis',
        'span_adjustment_when_first_after_second',
        'span_adjustment_when_second_after_first',
        'minimum_span_when_separated_on_axis', 'maximum_axis_span'
    ])

    entities = [rec_to_dict(r, entity_cols) for r in instance['layout_entities']]
    pairs = [rec_to_dict(r, nonoverlap_cols) for r in instance['non_overlap_requirements']]
    rels = [rec_to_dict(r, relationship_cols) for r in instance['relationships']]
    cals_raw = [rec_to_dict(r, calibration_cols) for r in instance['connector_axis_calibration']]

    ids = [int(e['entity_id']) for e in entities]
    row_min = {int(e['entity_id']): float(e['row_min']) for e in entities}
    row_max = {int(e['entity_id']): float(e['row_max']) for e in entities}
    col_min = {int(e['entity_id']): float(e['col_min']) for e in entities}
    col_max = {int(e['entity_id']): float(e['col_max']) for e in entities}
    anchor_row = {int(e['entity_id']): float(e['anchor_row']) for e in entities}
    anchor_col = {int(e['entity_id']): float(e['anchor_col']) for e in entities}

    m = gp.Model('database_architecture_layout_optimization')

    r = m.addVars(ids, lb=row_min, ub=row_max, vtype=GRB.INTEGER, name='row')
    c = m.addVars(ids, lb=col_min, ub=col_max, vtype=GRB.INTEGER, name='col')

    dev_r = m.addVars(ids, lb=0.0, vtype=GRB.CONTINUOUS, name='dev_row')
    dev_c = m.addVars(ids, lb=0.0, vtype=GRB.CONTINUOUS, name='dev_col')
    offset_r = m.addVars(ids, lb=-GRB.INFINITY, vtype=GRB.CONTINUOUS, name='offset_row')
    offset_c = m.addVars(ids, lb=-GRB.INFINITY, vtype=GRB.CONTINUOUS, name='offset_col')

    for i in ids:
        m.addConstr(offset_r[i] == r[i] - anchor_row[i], name=f'offset_row_def[{i}]')
        m.addConstr(offset_c[i] == c[i] - anchor_col[i], name=f'offset_col_def[{i}]')
        m.addGenConstrAbs(dev_r[i], offset_r[i], name=f'abs_row[{i}]')
        m.addGenConstrAbs(dev_c[i], offset_c[i], name=f'abs_col[{i}]')

    total_dev = gp.quicksum(dev_r[i] + dev_c[i] for i in ids)
    m.addConstr(total_dev >= float(instance['minimum_total_anchor_deviation']), name='minimum_total_anchor_deviation')

    cert_keys = []
    pair_by_unordered = {}
    normalized_pairs = []
    directions = ('r12', 'r21', 'c12', 'c21')
    for p in pairs:
        pid = int(p['pair_id'])
        i = int(p['first_entity_id'])
        j = int(p['second_entity_id'])
        normalized_pairs.append((pid, i, j, p))
        pair_by_unordered[frozenset((i, j))] = (pid, i, j)
        for d in directions:
            cert_keys.append((pid, d))

    y = m.addVars(cert_keys, vtype=GRB.BINARY, name='cert')

    for pid, i, j, p in normalized_pairs:
        m.addConstr(gp.quicksum(y[pid, d] for d in directions) == 1, name=f'one_certificate[{pid}]')

        gap = float(p['row_gap_first_before_second'])
        min_lhs = row_min[j] - row_max[i]
        max_lhs = row_max[j] - row_min[i]
        if max_lhs < gap:
            y[pid, 'r12'].ub = 0.0
        M = max(0.0, gap - min_lhs)
        m.addConstr(r[j] - r[i] + M * (1 - y[pid, 'r12']) >= gap, name=f'nonoverlap_r12[{pid}]')

        gap = float(p['row_gap_second_before_first'])
        min_lhs = row_min[i] - row_max[j]
        max_lhs = row_max[i] - row_min[j]
        if max_lhs < gap:
            y[pid, 'r21'].ub = 0.0
        M = max(0.0, gap - min_lhs)
        m.addConstr(r[i] - r[j] + M * (1 - y[pid, 'r21']) >= gap, name=f'nonoverlap_r21[{pid}]')

        gap = float(p['column_gap_first_before_second'])
        min_lhs = col_min[j] - col_max[i]
        max_lhs = col_max[j] - col_min[i]
        if max_lhs < gap:
            y[pid, 'c12'].ub = 0.0
        M = max(0.0, gap - min_lhs)
        m.addConstr(c[j] - c[i] + M * (1 - y[pid, 'c12']) >= gap, name=f'nonoverlap_c12[{pid}]')

        gap = float(p['column_gap_second_before_first'])
        min_lhs = col_min[i] - col_max[j]
        max_lhs = col_max[i] - col_min[j]
        if max_lhs < gap:
            y[pid, 'c21'].ub = 0.0
        M = max(0.0, gap - min_lhs)
        m.addConstr(c[i] - c[j] + M * (1 - y[pid, 'c21']) >= gap, name=f'nonoverlap_c21[{pid}]')

    cal = {}
    for a in cals_raw:
        rid = int(a['relationship_id'])
        axis_raw = str(a['axis']).lower()
        axis = 'row' if axis_raw.startswith('r') else 'col'
        cal[(rid, axis)] = {
            'adj_first_after_second': float(a['span_adjustment_when_first_after_second']),
            'adj_second_after_first': float(a['span_adjustment_when_second_after_first']),
            'min_when_sep': float(a['minimum_span_when_separated_on_axis']),
            'max_span': float(a['maximum_axis_span'])
        }

    span = {}
    connector_obj_terms = []
    for rel in rels:
        rid = int(rel['relationship_id'])
        i = int(rel['first_entity_id'])
        j = int(rel['second_entity_id'])
        w = float(rel['importance_weight'])

        row_cal = cal[(rid, 'row')]
        col_cal = cal[(rid, 'col')]
        srow = m.addVar(lb=0.0, ub=row_cal['max_span'], vtype=GRB.CONTINUOUS, name=f'span_row[{rid}]')
        scol = m.addVar(lb=0.0, ub=col_cal['max_span'], vtype=GRB.CONTINUOUS, name=f'span_col[{rid}]')
        span[(rid, 'row')] = srow
        span[(rid, 'col')] = scol

        m.addConstr(srow >= r[i] - r[j] + row_cal['adj_first_after_second'], name=f'span_row_first_after_second[{rid}]')
        m.addConstr(srow >= r[j] - r[i] + row_cal['adj_second_after_first'], name=f'span_row_second_after_first[{rid}]')
        m.addConstr(scol >= c[i] - c[j] + col_cal['adj_first_after_second'], name=f'span_col_first_after_second[{rid}]')
        m.addConstr(scol >= c[j] - c[i] + col_cal['adj_second_after_first'], name=f'span_col_second_after_first[{rid}]')

        pair_info = pair_by_unordered[frozenset((i, j))]
        pid = pair_info[0]
        m.addConstr(srow >= row_cal['min_when_sep'] * (y[pid, 'r12'] + y[pid, 'r21']), name=f'min_visible_row_if_separated[{rid}]')
        m.addConstr(scol >= col_cal['min_when_sep'] * (y[pid, 'c12'] + y[pid, 'c21']), name=f'min_visible_col_if_separated[{rid}]')

        m.addConstr(srow + scol >= float(rel['minimum_total_connector_span']), name=f'min_total_connector_span[{rid}]')
        connector_obj_terms.append(w * (srow + scol))

    anchor_weight = float(instance['anchor_deviation_weight'])
    m.setObjective(gp.quicksum(connector_obj_terms) + anchor_weight * total_dev, GRB.MINIMIZE)
    m.update()
    return m
