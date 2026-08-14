# Coupled-drift commitment order

The principal game order is:

1. Modeler declares graph, prior, drift budgets, horizon, costs, and caps.
2. Encoder selects a full deterministic codebook sequence.
3. Nature selects one source-law path satisfying the declared transition set.
4. Communication and switching cost are evaluated.

The selected sequence may depend on the model inputs but not on future realized
source symbols or hidden laws. Changing this order changes the mathematical
problem.
