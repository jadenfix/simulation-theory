# Bayesian adaptive Boolean queries

## Scope

A hidden model is a Boolean vector `X`. Querying coordinate `i` reveals `X_i` exactly. The decision-relevant future source symbol is `f(X)`, and terminal loss is the exact Bayesian K3 excess prefix length from the preceding lane.

For an observation cell `C` and remaining query budget `h`, the sufficient state is `(C,h)`. Query order is irrelevant once the current posterior support cell is known.

## Bellman recursion

Let

\[
L(C)=\min\{P(f=0\mid C),P(f=1\mid C)\}
\]

be the Bayes stopping loss. Then

\[
\boxed{
V_h(C)=\min\left\{L(C),\min_i\sum_{b\in\{0,1\}}P(X_i=b\mid C)V_{h-1}(C_{i=b})\right\}.
}
\]

Only coordinates that strictly split the current cell need be considered. Exact rational dynamic programming returns the optimal value and one optimal query at every reachable state.

Because a nonadaptive subset is a special adaptive policy that ignores outcomes when scheduling later queries,

\[
\boxed{V_h^{\rm adaptive}\le V_h^{\rm nonadaptive}.}
\]

Increasing the query budget cannot increase optimal Bayes loss.

## Multiplexer adaptivity gap

For three uniform bits define

\[
f(x)=\begin{cases}x_1,&x_0=0,\\x_2,&x_0=1.\end{cases}
\]

The selector query `x_0` has zero one-step value:

\[
V(\varnothing)=V(\{0\})=\frac12.
\]

Yet with two adaptive queries, observing `x_0` first tells the controller which payload bit matters. The second query is `x_1` when `x_0=0` and `x_2` when `x_0=1`, so

\[
\boxed{V_2^{\rm adaptive}=0.}
\]

Every fixed two-coordinate subset leaves residual error `1/4`, giving

\[
\boxed{V_2^{\rm nonadaptive}=\frac14}
\]

and strict adaptivity gain `1/4`.

The important point is not merely that adaptivity helps. The optimal first query has **zero myopic gain** and is valuable only because it changes which future query will be useful. This is an exact finite form of experiment option value.

## Parity boundary

For three-bit parity, every proper coordinate subset leaves the output perfectly balanced. Adaptive scheduling cannot help before all three bits are known:

\[
V_h^{\rm adaptive}=V_h^{\rm nonadaptive}=\frac12,\qquad h<3.
\]

At `h=3`, both values become zero. Adaptivity therefore depends on the conditional structure of the decision-relevant function, not merely on the existence of hidden variables.

## Nonclaims

- Queries are exact deterministic coordinate observations.
- The supplied prior is a model input.
- Free query budgets are not physical resource statements; adding query costs is a separate extension.
- The multiplexer example demonstrates strict option value but does not claim all experiment problems benefit from adaptivity.
- None of these results is evidence for simulation.
