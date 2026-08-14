# Coupled drift in one page

A changing source law is a path, not a list of unrelated distributions.

The exact finite model is

\[
q_0=p,
\qquad
TV(q_t,q_{t-1})\le\eta_t,
\qquad
q_t\in\Delta_{n-1}.
\]

For time-varying costs \(g_t\), solve

\[
\max_{q_{1:T}}\sum_t q_t^Tg_t.
\]

Finite TV has an exact event-halfspace representation, so after eliminating one
simplex coordinate per period this is a bounded rational LP. The repository
returns every bounded path vertex, an exact maximizing path, and an independent
nonnegative dual multiplier with zero rational gap.

Optimizing each time marginal independently gives only

\[
V_{\rm coupled}
\le
\sum_t\sup_{TV(q,p)\le R_t}q^Tg_t.
\]

The inequality can be strict because separately worst distributions may not be
reachable in one path. For a binary reversing-cost example, the exact values are

\[
V_{\rm coupled}=5/4,
\qquad
V_{\rm marginal}=7/4.
\]

The outer coding problem selects a full codebook sequence before nature chooses
the source path:

\[
\min_{c_{1:T}}
\left[
\sup_{q_{1:T}}\sum_tq_t^T\ell^{(c_t)}
+
\kappa N_{\rm switch}
\right].
\]

For uniform complete-confusion K3 over two TV steps of \(1/6\), rotating the
one-bit codeword has worst communication \(11/3\); the best static tree costs
\(23/6\). The gain and switching threshold are both \(1/6\).

The result is open-loop predictive control. Adaptation requires a separately
declared observation kernel and policy information pattern.
