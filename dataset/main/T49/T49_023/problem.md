A service operator must satisfy the service coverage requirement of every one of 168 time slots exactly. Each record in `slots` names a `slot_id` and the `requirement` that must be covered in that slot. Each record in `segments` describes an adjustable service segment with its `segment_id`, the `slot_id` it belongs to, the `threshold_low` and `threshold_high` between which its coverage must lie when it is enabled, and the `unit_price` paid per unit of coverage. Each record in `actions` describes a discrete service action with its `action_id` and `fixed_price`, and each record in `action_contributions` gives the `contribution` that a selected `action_id` makes to one `slot_id`.

Each record in `fallback` describes an emergency resource with its `fallback_id`, the `slot_id` it serves, and the `unit_price` per purchased unit, while `fallback_bounds` holds one record per bounded resource with its `fallback_id`, `min_amount`, and `max_amount`. An adjustable segment provides coverage only when it is enabled, and the provided amount must lie between `threshold_low` and `threshold_high`; a discrete action is either selected or not, costs its `fixed_price`, and adds its `action_contributions` to the affected slots; an emergency resource can be purchased in any amount for its `slot_id` at `unit_price`, respecting `min_amount` and `max_amount` when they are given. For every slot, the total coverage from enabled segments, selected actions, and purchased emergency resources must equal the slot's `requirement`.

The plan must also satisfy a set of policy modules. Each record in `nodes` defines one binary decision node with its `node_id`, its `node_kind` (`segment_switch`, `action_switch`, or `aux`), the `ref_id` of the segment or action it switches when applicable, and the `price` incurred when the node is set to one. Each record in `equations` gives an `eq_id` and its `rhs`, and each record in `equation_terms` links an `eq_id` to a `node_id` with a `sign` of plus or minus one, so the signed sum of the referenced node values must equal that equation's `rhs`.

Minimize the total cost, which is the sum of `unit_price` times coverage over all enabled segments, plus `fixed_price` over all selected actions, plus `price` over all nodes set to one, plus `unit_price` times the purchased amount over all emergency resources. All data are explicitly supplied in `instance.json`.

Report the minimum total cost, the selected binary nodes, the coverage amount of every adjustable segment, and the purchase amount of every emergency resource.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `action_contributions`: array with 19,872 records.
  Record fields:
  1. `action_id` (string)
  2. `slot_id` (string)
  3. `contribution` (number)
- `actions`: array with 5,930 records.
  Record fields:
  1. `action_id` (string)
  2. `fixed_price` (number)
- `equation_terms`: array with 111,415 records.
  Record fields:
  1. `eq_id` (string)
  2. `node_id` (string)
  3. `sign` (integer)
- `equations`: array with 12,391 records.
  Record fields:
  1. `eq_id` (string)
  2. `rhs` (integer)
- `fallback`: array with 189 records.
  Record fields:
  1. `fallback_id` (string)
  2. `slot_id` (string)
  3. `unit_price` (integer)
- `fallback_bounds`: array with 21 records.
  Record fields:
  1. `fallback_id` (string)
  2. `min_amount` (number)
  3. `max_amount` (number)
- `nodes`: array with 27,342 records.
  Record fields:
  1. `node_id` (string)
  2. `node_kind` (string)
  3. `ref_id` (string)
  4. `price` (integer)
- `segments`: array with 12,229 records.
  Record fields:
  1. `segment_id` (string)
  2. `slot_id` (string)
  3. `threshold_low` (number)
  4. `threshold_high` (integer)
  5. `unit_price` (number)
- `slots`: array with 168 records.
  Record fields:
  1. `slot_id` (string)
  2. `requirement` (number)
