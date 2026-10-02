# Three-mode tensor balancing with low-rank marginal structure

A campaign operations team must construct a real-valued region-channel-period correction tensor X with 96 regions, 88 channels, and 74 periods. The tensor must match three sets of marginal totals:

sum_{j,k} X[i,j,k] equals the region total for every region i,
sum_{i,k} X[i,j,k] equals the channel total for every channel j,
sum_{i,j} X[i,j,k] equals the period total for every period k.

The objective is:

minimize 0.5 * sum_{i,j,k} X[i,j,k]^2.

The deterministic formulas for all marginal totals are listed in `instance.json`; channel and period totals are scaled so all three grand totals agree.

Report the minimum objective value and the maximum marginal errors.

The dense formulation has 625,152 scalar tensor variables. The optimal tensor has an additive low-rank three-mode form:

X[i,j,k] = r_i/(J*K) + c_j/(I*K) + t_k/(I*J) - 2*total/(I*J*K).
