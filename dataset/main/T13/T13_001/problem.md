An interindustry planner manages 480,000 production blocks, collected in `blocks` in `instance.json`, each standing for one industry-year combination. Every block carries its own set of operating modes in `modes`, a list of 8 entries; each mode pairs a labor requirement `resource` (an integer, in labor units) with an output `value` (an integer, in value units) that the block produces per unit of that mode's intensity.

For each block the planner chooses a production mix, i.e. how the block's activity is divided among its operating modes: the mode intensities are nonnegative and together account for the whole block. The labor consumed by a block is the sum over its modes of intensity times `resource`, and the value generated is the corresponding sum of intensity times `value`. All blocks draw on one shared labor pool whose total capacity is the scalar `resource_capacity`, expressed in the same labor units.

Choose the production mix of every block so that the shared labor capacity is respected and the total value generated across all blocks is maximized. Every mode and the capacity are explicitly listed in `instance.json`.

Report the maximum total value and the chosen production mix for every block.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `blocks`: array with 480,000 records.
  - `blocks[i].modes`: array with exactly 8 records.
  - `blocks[i].modes[k].resource`: integer labor requirement of mode `k`.
  - `blocks[i].modes[k].value`: integer output value of mode `k`.
- `resource_capacity`: number scalar.
