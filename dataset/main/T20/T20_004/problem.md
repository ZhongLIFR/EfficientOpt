A police station must schedule shifts over a horizon of 100,000 consecutive time periods so that the staffing requirement of every period is met. The number of officers required in each period is given by `demand`. Every shift lasts `shift_length` consecutive periods: a shift started at period s covers periods s through s + `shift_length` − 1 within the horizon. The cost array `start_cost` gives, for every period s, the cost of starting one shift in that period, so starting a shift at period s costs `start_cost[s]`. Any number of shifts may start in the same period.

Report the minimum total start cost and the number of shifts started in every period.

All numerical data are fixed and explicitly provided in `instance.json`.

## Data schema

The complete fixed instance is in `instance.json`; no values are generated or sampled at runtime.

- `demand`: array with 100,000 records.
- `shift_length`: integer scalar.
- `start_cost`: array with 100,000 records.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `demand` is an array of integer values; entries retain their listed order.
- `start_cost` is an array of integer values; entries retain their listed order.
