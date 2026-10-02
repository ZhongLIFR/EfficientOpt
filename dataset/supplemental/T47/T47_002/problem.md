# Low-rank matrix balancing for regional campaign corrections

A media-planning team must construct a real-valued correction matrix X with 920 regions and 760 campaign channels. Each row has a fixed regional correction total, and each column has a fixed channel correction total. The goal is to choose the smoothest correction matrix:

minimize 0.5 * sum_{i,j} X[i,j]^2

subject to each row sum equaling the specified row total and each column sum equaling the specified column total.

The row totals and column totals are deterministic formulas listed in `instance.json`. The column totals are scaled so the two grand totals match.

Report the minimum objective value, the maximum row-sum error, and the maximum column-sum error.

This problem is intended to test whether the solver keeps the matrix structure. The dense formulation has 699,200 scalar X variables. The optimal matrix can instead be represented by two vectors:

X[i,j] = row_total[i] / n + col_total[j] / m - total / (m*n).
