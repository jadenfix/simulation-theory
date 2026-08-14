# Mathematical summary

For exact rational inputs, the coupled-drift lane solves

\[
\max_{q_{1:T}}
\sum_{t=1}^T q_t^\top g_t
\]

subject to

\[
q_0=p,
\qquad q_t\in\Delta_{n-1},
\qquad TV(q_t,q_{t-1})\le\eta_t.
\]

The path is encoded as a rational polytope in \(T(n-1)\) free variables using
the exact event identity for total variation. Vertex enumeration gives a primal
optimum. The dual

\[
\min_{y\ge0} c_0+b^Ty
\quad\text{s.t.}\quad A^Ty=c
\]

provides an independent zero-gap receipt.

The expanding-ball calculation

\[
\sum_t\sup_{TV(q,p)\le R_t}q^Tg_t,
\qquad
R_t=\min\left(1,\sum_{s\le t}\eta_s\right),
\]

is an upper bound and can be strict. It is attained by one canonical nested path
when all cost vectors have a common weak ordering.

For precommitted zero-error prefix codebooks \(c_{1:T}\), the exact outer problem
is

\[
\min_{c_{1:T}}
\left[
\sup_{q_{1:T}}\sum_tq_t^T\ell^{(c_t)}
+
\kappa\sum_{t=2}^T\mathbf1\{c_t\ne c_{t-1}\}
\right].
\]

The bounded implementation exhausts all sequences from the componentwise-
undominated deterministic code universe and returns both the globally selected
sequence and the best static commitment.

Exact benchmark identities:

\[
V_{\rm coupled}^{\rm binary}=5/4,
\qquad
V_{\rm marginal}^{\rm binary}=7/4,
\]

and for uniform \(K_3\) with two TV steps \(1/6\),

\[
V_{\rm rotate}=11/3,
\qquad
V_{\rm static}=23/6,
\qquad
\kappa_c=1/6.
\]
