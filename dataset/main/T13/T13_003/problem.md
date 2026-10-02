An economy-wide planner selects technologies for 96,000 industry blocks, collected in `blocks` in `instance.json`. Every block carries its own set of candidate technologies in `modes`, a list of 10 entries; each mode pairs a labor requirement `resource` (an integer, in labor units) with an economic value `value` (an integer, in value units) that the block earns per unit of that mode's intensity.

For each block the planner chooses a technology mix, i.e. how the block's activity is distributed across its candidate technologies: the mode intensities are nonnegative and together account for the whole block. The labor consumed by a block is the sum over its modes of intensity times `resource`, and the economic value earned is the corresponding sum of intensity times `value`. All blocks draw on one total labor pool whose capacity is the scalar `resource_capacity`, expressed in the same labor units.

Choose the technology mix of every block so that the total labor capacity is respected and the total economic value across all blocks is maximized. Every mode and the capacity are explicitly listed in `instance.json`.

Report the maximum total economic value and the chosen technology mix for every block.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `blocks`: array with 96,000 records.
  - `blocks[i].modes`: array with exactly 10 records.
  - `blocks[i].modes[k].resource`: integer labor requirement of technology `k`.
  - `blocks[i].modes[k].value`: integer economic value of technology `k`.
- `resource_capacity`: number scalar.
