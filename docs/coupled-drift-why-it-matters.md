# Why coupled drift matters

The static robust question asks which law could be true. The dynamic question
asks which sequence of laws could all be true **together**.

That distinction matters whenever:

- constraints limit how fast an environment can change;
- decisions today change which futures remain reachable;
- different future queries reward movement in different directions;
- representations can be reconfigured but switching is costly;
- local snapshots must belong to one coherent hidden history.

The central warning is logical:

\[
\forall t\ \exists q_t
\]

does not imply

\[
\exists(q_1,\ldots,q_T)\ \forall t.
\]

The central constructive idea is equally simple: when one coherent path is
required, its current state carries **future optionality**. The correct
predictive state must preserve not only the present output law but the reachable
family of future laws under every declared intervention and control.

This insight is broader than prefix coding. It applies to dynamic rendering,
cache and replica placement, model routing, sensor scheduling, intervention
planning, and any restricted simulation architecture that claims it can decide
each local snapshot independently.
