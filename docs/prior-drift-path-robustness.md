# Bounded total-variation source drift and static robust coding

Static ambiguity and nonstationarity are not the same problem.  A TV ball says that one unknown source law lies near a nominal law.  A drift model instead constrains an entire path of source laws.

This lane studies

\[
q_0=p,
\qquad
\operatorname{TV}(q_t,q_{t-1})\le\eta,
\quad t=1,\ldots,T,
\]

while one deterministic zero-error binary prefix code is fixed before the path evolves and used at every future period.

The model is intentionally narrow.  It is the cleanest setting in which to isolate what changes once source uncertainty acquires a time axis.

## 1. Marginal radius growth follows from triangle inequality

For every feasible path,

\[
\operatorname{TV}(q_t,p)
\le
\sum_{s=1}^t
\operatorname{TV}(q_s,q_{s-1})
\le t\eta.
\]

Since TV is at most one,

\[
\boxed{
\operatorname{TV}(q_t,p)
\le
r_t:=\min\{t\eta,1\}.
}
\]

For a fixed state-cost vector `ell`, this immediately gives

\[
q_t^T\ell
\le
\sup_{\operatorname{TV}(q,p)\le r_t}q^T\ell.
\]

Summing gives the pathwise upper bound

\[
\sup_{(q_t)}\sum_{t=1}^Tq_t^T\ell
\le
\sum_{t=1}^T
\sup_{\operatorname{TV}(q,p)\le r_t}q^T\ell.
\]

The nontrivial question is whether the periodwise extremizers can all belong to one path.

## 2. A fixed linear objective admits nested TV extremizers

For one fixed value vector `ell`, the exact TV optimizer in the repository constructs a worst law by transporting probability mass from low-value donor states toward a maximum-value recipient.  As the radius grows, the construction continues the same ordered transport rather than undoing earlier transfers.

Consequently the extremal laws can be chosen as a nested family

\[
q^*(r),\qquad 0\le r\le1,
\]

with

\[
\operatorname{TV}(q^*(r),p)=\min\{r,r_{\rm sat}\}
\]

and, for `0 <= r <= s`,

\[
\operatorname{TV}(q^*(r),q^*(s))
\le s-r.
\]

Set

\[
q_t=q^*(r_t).
\]

Because

\[
r_t-r_{t-1}\le\eta,
\]

this is a feasible drift path.  Every period simultaneously attains its marginal TV-ball optimum.

Therefore the upper bound is exact:

\[
\boxed{
\sup_{\substack{q_0=p\\
TV(q_t,q_{t-1})\le\eta}}
\sum_{t=1}^Tq_t^T\ell
=
\sum_{t=1}^T
\sup_{TV(q,p)\le\min(t\eta,1)}q^T\ell.
}
\]

This identity is specific to a fixed linear objective whose TV-optimal transport ordering does not change over time.  It is not silently extended to changing cost vectors.

## 3. Exact path certificate

For each period, the implementation stores the existing exact rational TV transport certificate at radius

\[
r_t=\min(t\eta,1).
\]

It then stores the complete candidate extremal path and checks independently that

\[
TV(q_t,q_{t-1})\le\eta
\]

for every consecutive pair.  The cumulative cost is reconstructed exactly from the period certificates.

The certificate therefore proves both sides of the path theorem:

- the triangle-inequality converse;
- one simultaneously attaining explicit path.

No dynamic-programming approximation is required for the static-code/fixed-objective case.

## 4. Static robust code design

A deterministic zero-error code induces a state-length vector

\[
\ell_c=(\ell_{c,1},\ldots,\ell_{c,n}).
\]

The finite-horizon static robust objective is

\[
\boxed{
V_T^{\rm drift}(G,p,\eta)
=
\min_c
\sup_{(q_t)}
\sum_{t=1}^Tq_t^T\ell_c.
}
\]

By the fixed-objective path theorem,

\[
V_T^{\rm drift}
=
\min_c
\sum_{t=1}^T
\phi_c(\min(t\eta,1)),
\]

where

\[
\phi_c(r)
:=
\sup_{TV(q,p)\le r}q^T\ell_c.
\]

The outer search must preserve every code that can be optimal under some law.  The implementation therefore enumerates the deterministic code universe using the simplex-vertex priors.  Under a pure-state prior `e_i`, the scenario cost is exactly `ell_{c,i}`.  Pareto dominance across these scenarios is thus exactly componentwise length dominance.

If

\[
\ell_c\le\ell_d
\quad\text{coordinatewise},
\]

then for every probability law `q`,

\[
q^T\ell_c\le q^T\ell_d.
\]

So componentwise-dominated codes are safely discarded for every possible source-law path, not merely for one set of sampled scenarios.

## 5. Zero-drift endpoint

At

\[
\eta=0,
\]

the only feasible path is

\[
q_t=p
\quad\forall t.
\]

Therefore

\[
\boxed{
V_T^{\rm drift}(G,p,0)
=T L^*(G,p),
}
\]

where `L*(G,p)` is the nominal one-shot prior-weighted optimum.

This provides an exact endpoint consistency check between the new time-dependent lane and the existing nominal source-coding lane.

## 6. Skew K4 admits a closed finite-horizon phase boundary

Take

\[
p=(7/10,1/10,1/10,1/10)
\]

on the complete graph `K4`.

The nominally optimal unbalanced tree assigns state zero the short codeword and has state lengths

\[
(1,2,3,3).
\]

Its nominal mean is

\[
\frac32.
\]

For TV radius `r <= 7/10`, the adversary moves mass from the length-one high-probability state to a length-three state.  The gain is two bits per unit transported mass, so

\[
\phi_{\rm unbal}(r)
=
\frac32+2r.
\]

As long as

\[
T\eta\le\frac7{10},
\]

the cumulative unbalanced cost is

\[
\begin{aligned}
C_{\rm unbal}(T,\eta)
&=
\sum_{t=1}^T
\left(\frac32+2t\eta\right)\\
&=
\boxed{
\frac{3T}{2}+\eta T(T+1)
}.
\end{aligned}
\]

The balanced tree has state lengths

\[
(2,2,2,2),
\]

so its cost is independent of the source path:

\[
\boxed{C_{\rm bal}(T)=2T.}
\]

Equating the two gives

\[
\frac{3T}{2}+\eta T(T+1)=2T,
\]

hence

\[
\boxed{
\eta_c(T)=\frac{1}{2(T+1)}.
}
\]

At this threshold,

\[
T\eta_c(T)
=
\frac{T}{2(T+1)}
<\frac12<\frac7{10},
\]

so the linear TV profile used in the derivation is self-consistent for every positive horizon.

Thus:

- below `eta_c(T)`, the skew source is predictable enough that exploiting its dominant state remains optimal;
- above `eta_c(T)`, the balanced two-bit tree is minimax for the whole path;
- the per-step drift needed to justify the balanced tree falls like `1/T` as the commitment horizon grows.

For `T=2`,

\[
\boxed{\eta_c=1/6.}
\]

For `eta=1/7`, a two-period commitment still selects the unbalanced tree, while a three-period commitment selects the balanced tree.

This is a temporal robustness effect: the same instantaneous drift budget can imply a different optimal architecture solely because the code must remain fixed for longer.

## 7. Drift compounds differently from a repeated static ball

It would be incorrect to replace the path model by the same radius-`eta` TV ball independently at every period.

The path constraint permits the law to walk progressively farther from the original nominal law:

\[
r_t=\min(t\eta,1).
\]

Before saturation, uncertainty therefore grows with time even though the one-step drift budget is fixed.

Conversely, the path constraint couples the laws between periods.  When the cost vector changes with time, independently maximizing every marginal TV ball can become impossible.  That coupled time-varying-cost problem is intentionally left for the next lane rather than being hidden inside this static-code theorem.

## 8. Combining estimation uncertainty and declared drift

Suppose a training sample produces empirical law

\[
\hat p
\]

and a statistical confidence certificate gives, on an event of probability at least `1-delta`,

\[
TV(\hat p,p_{\rm train})\le r_{\rm stat}.
\]

Now separately assume the current source law satisfies a declared drift bound

\[
TV(p_{\rm current},p_{\rm train})\le D.
\]

Then triangle inequality gives

\[
TV(p_{\rm current},\hat p)
\le
r_{\rm stat}+D.
\]

Thus the correct conservative radius is

\[
\boxed{
r_{\rm current}
=
\min\{1,r_{\rm stat}+D\}.
}
\]

The implementation records the statistical and drift components separately rather than presenting the sum as though both came from sampling theory.

This distinction matters:

- `r_stat` is justified by the declared sampling model and confidence level;
- `D` is an external drift assumption or independently established bound;
- robust optimization only consumes the resulting geometry.

## 9. What changes when the code itself can adapt

This lane fixes one codebook before the drift path evolves.  Several harder games are different problems:

- a predeclared sequence of different codebooks;
- code switching based on time;
- adaptation to observed source symbols;
- adaptation to estimated source-law changes;
- source laws that react to the realized codebook;
- switching costs or codebook-distribution costs.

Once the period cost vector changes, the nested-transport construction need not optimize every period simultaneously.  The correct object becomes one coupled finite-horizon transport polytope rather than a sum of independent radial profiles.

That is the next mathematical layer, not an unspoken extension of the current theorem.

## Boundaries

These results establish exact finite-horizon expected prefix-length guarantees for a static deterministic code under a declared per-step TV drift model.  They do not establish:

- that empirical source drift actually satisfies the chosen `eta`;
- confidence under arbitrary nonstationary sampling without a separate statistical procedure;
- optimal adaptive code switching;
- queueing or latency guarantees;
- physical parent-substrate resource costs;
- evidence for simulation.
