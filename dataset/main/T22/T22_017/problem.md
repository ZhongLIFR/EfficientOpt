A plant plans the production level of 150 products, listed by their unit profit in `profit`
(same index order as everywhere else in `instance.json`). Production levels may be split
fractionally and cannot be negative.

Operations are limited by 2000 resource ceilings, each described by one record of `limits`:
- `support`: the 12 product indices whose resource consumption this ceiling covers;
- `nominal`: the nominal consumption per produced unit for each of those products;
- `deviation`: how far the actual consumption of that product may deviate from the nominal value.

A ceiling is met only if it holds for **every** admissible deviation pattern of its support: each
product's consumption may move up or down by at most its `deviation`, and the total relative
deviation across the support, measured as the sum of |actual deviation| / `deviation`, may not
exceed `uncertainty_budget`. The right-hand side of ceiling `k` is `limit_value[k]`.

Choose the production levels so that every ceiling holds under every admissible deviation pattern,
and total profit is as large as possible.

Report the maximum profit satisfying all listed deviation patterns and the production levels.

All numerical data are fixed and provided in the instance file.

## Data schema

The complete fixed instance is in the instance file; no values are generated or sampled during execution.

- `limits`: array with 2000 records; fields `support` (array of 12 product indices),
  `nominal` (array of 12 numbers), `deviation` (array of 12 numbers).
- `profit`: array with 150 numbers; unit profit per product.
- `limit_value`: array with 2000 numbers; right-hand side of each ceiling.
- `uncertainty_budget`: number; the deviation budget that applies to each ceiling separately.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `uncertainty_budget` is an integer scalar.
- `limits[].deviation` is an array of integer values; entries retain their listed order.
- `limits[].nominal` is an array of integer values; entries retain their listed order.
- `limits[].support` is an array of integer values; entries retain their listed order.
- `profit` is an array of integer values; entries retain their listed order.
- `limit_value` is an array of integer values; entries retain their listed order.
