# Cost-sensitive Bayesian adaptive query stopping

Let `C` be the current posterior support cell and `h` the remaining query budget. Stopping incurs Bayesian terminal gap

\[
L(C)=\min\{P(f=0\mid C),P(f=1\mid C)\}.
\]

Querying coordinate `i` costs `c_i` and then branches on the observed bit. Exact dynamic programming solves

\[
\boxed{
J_h(C)=\min\left\{L(C),\min_i\left[c_i+\sum_bP(X_i=b\mid C)J_{h-1}(C_{i=b})\right]\right\}.
}
\]

This is the exact stop-versus-experiment tradeoff for the declared finite model.

## Nonmyopic option value

For the uniform three-bit multiplexer

\[
f(x)=x_1\;\text{if }x_0=0,\qquad f(x)=x_2\;\text{if }x_0=1,
\]

the selector `x_0` has zero immediate information value: observing it and then stopping leaves Bayes gap `1/2`, exactly the original gap. With a positive query cost `c`, the one-step action `query x_0 then stop` is strictly worse than stopping.

Yet with two queries remaining, `x_0` has option value because it determines which payload coordinate should be queried next. The policy `query x_0, then query x_1 or x_2 as appropriate` has total value

\[
2c.
\]

Stopping has value `1/2`. Therefore the dynamic threshold is

\[
\boxed{c<1/4.}
\]

For every `0<c<1/4`, the optimal first query is `x_0` even though its myopic net value is negative. At `c=1/4`, stopping and the two-query plan tie; the implementation uses stopping as the canonical tie-break.

This is a clean distinction between:

- **myopic value:** improvement if the experiment is followed immediately by stopping;
- **option value:** improvement because the observation changes which later experiment should be chosen.

## Parity boundary

For three-bit parity and a budget of only two queries, no possible adaptive policy reduces terminal Bayes gap below `1/2`. Consequently any strictly positive query cost makes immediate stopping optimal. The absence of option value is structural: no proper subset determines or biases parity under the uniform prior.

## Nonclaims

- Query costs are declared rational decision costs, not physical energy costs.
- The threshold `1/4` is specific to the three-bit multiplexer and this terminal loss.
- Myopic failure does not imply every optimal experiment problem needs deep lookahead.
- Exact finite dynamic programming is not evidence for simulation.
