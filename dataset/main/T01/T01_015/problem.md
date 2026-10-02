A database architecture team must arrange the boxes listed in `layout_entities` on a two-dimensional integer grid. `entity_columns` gives the meaning and order of each entity row. Every box must remain inside its permitted row and column windows, and no two boxes may overlap.

For each entity pair, `non_overlap_requirements` gives the clear space required for either possible row ordering and either possible column ordering. The layout must select one of these four spatial relationships as the pair's non-overlap certificate and satisfy its required gap. Because the certificates describe positions on a shared grid, their directional ordering must remain globally consistent.

The `relationships` data identifies connected boxes whose drawn connector spans contribute to visual clutter. Each relationship has an importance weight and a minimum total connector span. The matching rows in `connector_axis_calibration` describe how the diagram software measures row and column span: they give the directional adjustment for either endpoint ordering, the minimum visible span when that axis certifies separation, and the maximum permitted span on the axis. The measured nonnegative span must cover either directed endpoint separation after its corresponding calibration adjustment.

For readability, the total absolute row-and-column displacement of all boxes from their anchors must be at least `minimum_total_anchor_deviation`. Minimize the importance-weighted connector spans plus `anchor_deviation_weight` times the total anchor displacement. Report the minimum objective value.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `minimum_total_anchor_deviation`: integer scalar.
- `anchor_deviation_weight`: integer scalar.
- `entity_columns`: array of strings; labels and positional order for `layout_entities` rows.
- `layout_entities`: array of positional rows.  Row fields, in order:
  1. `entity_id` (integer)
  2. `label` (string)
  3. `row_min` (integer)
  4. `row_max` (integer)
  5. `col_min` (integer)
  6. `col_max` (integer)
  7. `anchor_row` (number)
  8. `anchor_col` (number)
- `non_overlap_columns`: array of strings; labels and positional order for `non_overlap_requirements` rows.
- `non_overlap_requirements`: array of positional rows.  Row fields, in order:
  1. `pair_id` (integer)
  2. `first_entity_id` (integer)
  3. `second_entity_id` (integer)
  4. `row_gap_first_before_second` (integer)
  5. `row_gap_second_before_first` (integer)
  6. `column_gap_first_before_second` (integer)
  7. `column_gap_second_before_first` (integer)
- `relationship_columns`: array of strings; labels and positional order for `relationships` rows.
- `relationships`: array of positional rows.  Row fields, in order:
  1. `relationship_id` (integer)
  2. `first_entity_id` (integer)
  3. `second_entity_id` (integer)
  4. `importance_weight` (integer)
  5. `minimum_total_connector_span` (number)
- `connector_axis_columns`: array of strings; labels and positional order for `connector_axis_calibration` rows.
- `connector_axis_calibration`: array of positional rows.  Row fields, in order:
  1. `relationship_id` (integer)
  2. `axis` (string)
  3. `span_adjustment_when_first_after_second` (number)
  4. `span_adjustment_when_second_after_first` (number)
  5. `minimum_span_when_separated_on_axis` (number)
  6. `maximum_axis_span` (number)
