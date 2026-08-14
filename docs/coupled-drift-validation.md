# Coupled-drift validation strategy

The implementation uses several nonidentical checks:

- active-basis enumeration of the full path polytope;
- exact sparse LP dual multipliers;
- complementary-slackness replay;
- an independent rational grid audit for two-state cases;
- reduction to the previously merged fixed-cost drift theorem;
- complete bounded code-sequence enumeration;
- exact switching-threshold examples.

Agreement between these routes is evidence that the finite implementation matches the stated model. It is not empirical evidence about simulation theory.