A national planner coordinates 88,000 economic sector blocks, collected in `blocks` in `instance.json`. Every block offers its own set of operating modes in `modes`, a list of 9 entries; each mode pairs a required input `resource` (an integer, in input units) with an output `value` (an integer, in value units) that the sector produces per unit of that mode's intensity.

For each block the planner chooses an operating mix, i.e. how the block's activity is split among its operating modes: the mode intensities are nonnegative and together account for the whole block. The input consumed by a block is the sum over its modes of intensity times `resource`, and the output value is the corresponding sum of intensity times `value`. All blocks draw on one shared input pool whose total capacity is the scalar `resource_capacity`, expressed in the same input units.

Choose the operating mix of every block so that the shared input capacity is respected and the total output value across all blocks is maximized. Every mode and the capacity are explicitly listed in `instance.json`.

Report the maximum total output value and the chosen operating mix for every block.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `blocks`: array with 88,000 records.
  - `blocks[i].modes`: array with exactly 9 records.
  - `blocks[i].modes[k].resource`: integer input requirement of mode `k`.
  - `blocks[i].modes[k].value`: integer output value of mode `k`.
- `resource_capacity`: number scalar.

All block modes and the shared resource capacity are explicitly fixed in instance.json; no values are generated during solving.
