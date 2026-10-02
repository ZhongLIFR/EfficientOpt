A service company plans its daily routes from one depot to 57 customer sites. A route may serve at
most 6 sites, and at most 20 routes may be operated in a day. Opening a route costs a fixed charge
of 60; serving site `i` on a route adds `site_service_cost[i]`.

Not every pair of sites can share a route: `incompatible_pairs` lists the forbidden pairs (for
example because the two sites need different specialists on the same day).

Choose a set of routes and how much of each route to operate (route usage may be fractional) so that
every site is served at least once, the fleet limit and the compatibility restrictions hold, and the
total cost is as small as possible.

Report the minimum total cost and the routes used.

All numerical data are fixed and provided in the instance file.

## Data schema

- `site_count`, `max_sites_per_route`, `max_open_routes`, `fixed_route_charge`: integers.
- `site_service_cost`: array with 57 numbers.
- `incompatible_pairs`: array of pairs `[i, j]` of site indices that cannot share a route.
- `site_duration`: array with `site_count` numbers; service duration of each site.
- `shift_length`: scalar number; maximum route duration.
- `site_weight`: array with `site_count` numbers; weight of each site.
- `route_weight_limit`: scalar number; maximum total weight on a route.
- `site_volume`: array with `site_count` numbers; volume of each site.
- `route_volume_limit`: scalar number; maximum total volume on a route.

## Schema clarifications (structural only)
The notes below clarify JSON types and positional shape only; all numerical values remain in the local fixed instance.
- `shift_length` is an integer scalar.
- `route_weight_limit` is an integer scalar.
- `route_volume_limit` is an integer scalar.
- `site_service_cost` is an array of integer values; entries retain their listed order.
- `site_duration` is an array of integer values; entries retain their listed order.
- `site_weight` is an array of integer values; entries retain their listed order.
- `site_volume` is an array of integer values; entries retain their listed order.
- `incompatible_pairs` is an array of positional rows; each row contains 2 entries of numeric type.
