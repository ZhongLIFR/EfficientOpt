A mill cuts stock rolls of fixed width 630 into 19 distinct item widths. The fixed arrays `item_widths` and `demands` give each item width and its required quantity.

A cutting pattern is any nonempty vector of nonnegative integer item counts whose total used width does not exceed `stock_width`. Any pattern may be used any nonnegative integer number of times, and overproduction is allowed.

Choose how many rolls to cut with each admissible pattern so that every item demand is met. Minimize the total number of stock rolls used. Report the minimum number of rolls and the complete cutting plan.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `stock_width`: integer scalar equal to 630.
- `item_widths`: array of 19 distinct positive integers.
- `demands`: array of 19 positive integers aligned with `item_widths`.
