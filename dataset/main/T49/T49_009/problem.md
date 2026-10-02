A single advertising campaign must contract among 78 channels and place impression blocks for 700 distinct audience segments. Each segment has a format, market, required number of impression blocks, review workload per block, and an explicit set of eligible channels. Each channel has supported formats, impression capacity, review capacity, and a fixed contract fee. `placement_costs` gives the fixed cost per block for every allowed segment-channel pair.

Every segment's complete requirement must be placed. A channel can receive placements only if it is contracted, and its impression and review capacities cannot be exceeded. Minimize total contract and placement cost. Report the minimum cost, contracted channels, and positive placements.

## Data schema

The complete fixed instance is in `instance.json`; no value is generated or sampled during model construction or solving.

- `channels`: 78 records with `id`, `market`, `formats`, `impression_capacity_blocks`, `review_capacity_points`, and `contract_fee`.
- `segments`: 700 records with `id`, `creative_format`, `market`, `required_impression_blocks`, `review_points_per_block`, and `eligible_channels`.
- `placement_costs`: 15957 allowed-pair records with `segment`, `channel`, and `cost_per_block`.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `channels[].formats` is an array of strings; entries retain their listed order.
- `segments[].eligible_channels` is an array of strings; entries retain their listed order.
