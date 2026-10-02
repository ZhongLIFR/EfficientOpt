import gurobipy as gp
from gurobipy import GRB


INCLUDE_TRIANGLES = False


def _rows(records, columns):
    return [dict(zip(columns, record)) for record in records]


def build_model(instance):
    entities = _rows(instance["layout_entities"], instance["entity_columns"])
    pairs = _rows(instance["non_overlap_requirements"], instance["non_overlap_columns"])
    relationships = _rows(instance["relationships"], instance["relationship_columns"])
    calibrations = _rows(instance["connector_axis_calibration"], instance["connector_axis_columns"])

    model = gp.Model("layout_with_triangles" if INCLUDE_TRIANGLES else "layout_without_redundant_triangles")
    row_position = {}
    column_position = {}
    anchor_offset = {}
    anchor_deviation = {}
    for entity in entities:
        entity_id = int(entity["entity_id"])
        row_position[entity_id] = model.addVar(
            lb=float(entity["row_min"]), ub=float(entity["row_max"]), vtype=GRB.INTEGER,
            name=f"row[{entity_id}]",
        )
        column_position[entity_id] = model.addVar(
            lb=float(entity["col_min"]), ub=float(entity["col_max"]), vtype=GRB.INTEGER,
            name=f"column[{entity_id}]",
        )
        anchor_deviation[entity_id, "row"] = model.addVar(lb=0.0, name=f"row_deviation[{entity_id}]")
        anchor_deviation[entity_id, "col"] = model.addVar(lb=0.0, name=f"column_deviation[{entity_id}]")
        anchor_offset[entity_id, "row"] = model.addVar(lb=-GRB.INFINITY, name=f"row_offset[{entity_id}]")
        anchor_offset[entity_id, "col"] = model.addVar(lb=-GRB.INFINITY, name=f"column_offset[{entity_id}]")
        model.addConstr(anchor_offset[entity_id, "row"] == row_position[entity_id] - float(entity["anchor_row"]))
        model.addConstr(anchor_offset[entity_id, "col"] == column_position[entity_id] - float(entity["anchor_col"]))
        model.addGenConstrAbs(anchor_deviation[entity_id, "row"], anchor_offset[entity_id, "row"])
        model.addGenConstrAbs(anchor_deviation[entity_id, "col"], anchor_offset[entity_id, "col"])
    model.addConstr(gp.quicksum(anchor_deviation.values()) >= float(instance["minimum_total_anchor_deviation"]))

    direction = {}
    pair_map = {}
    for pair in pairs:
        pair_id = int(pair["pair_id"])
        first = int(pair["first_entity_id"])
        second = int(pair["second_entity_id"])
        pair_map[first, second] = (pair_id, True)
        pair_map[second, first] = (pair_id, False)
        for key in ("row_first_second", "row_second_first", "col_first_second", "col_second_first"):
            direction[pair_id, key] = model.addVar(vtype=GRB.BINARY, name=f"direction[{pair_id},{key}]")
        model.addConstr(gp.quicksum(direction[pair_id, key] for key in (
            "row_first_second", "row_second_first", "col_first_second", "col_second_first"
        )) == 1.0)
        model.addGenConstrIndicator(
            direction[pair_id, "row_first_second"], 1,
            row_position[second] - row_position[first] >= float(pair["row_gap_first_before_second"]),
        )
        model.addGenConstrIndicator(
            direction[pair_id, "row_second_first"], 1,
            row_position[first] - row_position[second] >= float(pair["row_gap_second_before_first"]),
        )
        model.addGenConstrIndicator(
            direction[pair_id, "col_first_second"], 1,
            column_position[second] - column_position[first] >= float(pair["column_gap_first_before_second"]),
        )
        model.addGenConstrIndicator(
            direction[pair_id, "col_second_first"], 1,
            column_position[first] - column_position[second] >= float(pair["column_gap_second_before_first"]),
        )

    def directed(first, second, axis):
        pair_id, forward = pair_map[first, second]
        if axis == "row":
            key = "row_first_second" if forward else "row_second_first"
        else:
            key = "col_first_second" if forward else "col_second_first"
        return direction[pair_id, key]

    if INCLUDE_TRIANGLES:
        ids = sorted(row_position)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                for k in range(j + 1, len(ids)):
                    first, second, third = ids[i], ids[j], ids[k]
                    for axis in ("row", "col"):
                        model.addConstr(
                            directed(first, second, axis)
                            + directed(second, third, axis)
                            + directed(third, first, axis) <= 2.0
                        )
                        model.addConstr(
                            directed(first, third, axis)
                            + directed(third, second, axis)
                            + directed(second, first, axis) <= 2.0
                        )

    calibration_by_relationship = {}
    for calibration in calibrations:
        calibration_by_relationship[int(calibration["relationship_id"]), str(calibration["axis"])] = calibration

    connector_span = {}
    objective = gp.LinExpr()
    for relationship in relationships:
        relationship_id = int(relationship["relationship_id"])
        first = int(relationship["first_entity_id"])
        second = int(relationship["second_entity_id"])
        connector_span[relationship_id, "row"] = model.addVar(lb=0.0, name=f"row_span[{relationship_id}]")
        connector_span[relationship_id, "col"] = model.addVar(lb=0.0, name=f"column_span[{relationship_id}]")
        model.addConstr(
            connector_span[relationship_id, "row"] + connector_span[relationship_id, "col"]
            >= float(relationship["minimum_total_connector_span"])
        )
        for axis, positions in (("row", row_position), ("col", column_position)):
            calibration = calibration_by_relationship[relationship_id, axis]
            span = connector_span[relationship_id, axis]
            model.addConstr(
                span + positions[second] - positions[first]
                >= float(calibration["span_adjustment_when_first_after_second"])
            )
            model.addConstr(
                span + positions[first] - positions[second]
                >= float(calibration["span_adjustment_when_second_after_first"])
            )
            pair_id, _ = pair_map[first, second]
            keys = ("row_first_second", "row_second_first") if axis == "row" else (
                "col_first_second", "col_second_first"
            )
            for key in keys:
                model.addGenConstrIndicator(
                    direction[pair_id, key], 1,
                    span >= float(calibration["minimum_span_when_separated_on_axis"]),
                )
            model.addConstr(span <= float(calibration["maximum_axis_span"]))
        objective += float(relationship["importance_weight"]) * (
            connector_span[relationship_id, "row"] + connector_span[relationship_id, "col"]
        )

    objective += float(instance["anchor_deviation_weight"]) * gp.quicksum(anchor_deviation.values())
    model.setObjective(objective, GRB.MINIMIZE)
    return model
