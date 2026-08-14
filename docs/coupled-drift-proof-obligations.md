# Coupled-drift proof obligations

A coupled-drift result is acceptable only when the certificate replays all of the following:

1. Every period law is nonnegative and sums exactly to one.
2. The initial reference law is the declared nominal prior.
3. Every consecutive total-variation distance is at most the declared mobility budget.
4. The reported objective is the exact rational cost of the reported path.
5. Every transformed halfspace is satisfied.
6. Dual multipliers are nonnegative.
7. Dual stationarity reproduces the period-cost objective.
8. Complementary slackness holds exactly.
9. Primal and dual values agree exactly.
10. The independent marginal envelope is no smaller than the coupled value.
11. Code-sequence search is complete below its declared cap.
12. Switching cost is accounted for separately from encoded length.

A failure of any obligation invalidates the certificate rather than downgrading it to an approximate success.