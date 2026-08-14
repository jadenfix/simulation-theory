# Path-oracle maximin geometry

## Scope

For a finite comparator family \(\mathcal B\), each comparator has affine path
cost

\[
C_b(q)=k_b+\sum_t q_t^\top g_{b,t}.
\]

The path-specific oracle cost is

\[
O(q)=\min_{b\in\mathcal B}C_b(q).
\]

This note explains why the maximum oracle cost over a path polytope cannot in
general be found by inspecting only the path vertices, even though the maximum
of pathwise regret can.

---

## 1. Oracle cost is concave, not convex

A pointwise minimum of affine functions is concave and piecewise linear. For
feasible paths \(q,q'\) and \(\theta\in[0,1]\),

\[
\begin{aligned}
O(\theta q+(1-\theta)q')
&=
\min_b\left[
\theta C_b(q)+(1-\theta)C_b(q')
\right]\\
&\ge
\theta\min_b C_b(q)
+(1-\theta)\min_b C_b(q')\\
&=
\theta O(q)+(1-\theta)O(q').
\end{aligned}
\]

Therefore

\[
\boxed{O\text{ is concave piecewise linear}.}
\]

A concave function may attain its maximum in the interior of a polytope. Vertex
reduction applies to the **minimum** of \(O\), but not automatically to its
maximum.

By contrast, regret of a fixed decision is

\[
C_a(q)-O(q)
=
\max_b[C_a(q)-C_b(q)],
\]

which is convex piecewise linear and therefore does attain its maximum at a
path vertex.

---

## 2. Exact finite-game reduction of the oracle maximum

Let the path polytope have vertices \(v_1,\ldots,v_M\). Every feasible path can
be written as

\[
q=\sum_{j=1}^{M}\lambda_jv_j,
\qquad
\lambda\in\Delta_{M-1}.
\]

Because each comparator cost is affine,

\[
C_b(q)
=
\sum_j\lambda_j C_b(v_j).
\]

Hence

\[
\boxed{
\max_{q}O(q)
=
\max_{\lambda\in\Delta_{M-1}}
\min_{b\in\mathcal B}
\sum_j\lambda_jC_b(v_j).
}
\]

If

\[
A_{jb}=C_b(v_j),
\]

this is the dual side of the finite zero-sum game

\[
\min_{x\in\Delta_{|\mathcal B|-1}}
\max_j\sum_bx_bA_{jb}.
\]

Exact finite minimax therefore gives both:

- a comparator mixture upper certificate;
- a path-vertex mixture lower certificate;
- one rational common value.

The path-vertex mixture represents an actual feasible barycenter path because
the path set is convex.

---

## 3. Strict interior example

Take one period, two source states, and full-simplex uncertainty. Let the two
comparators have costs

\[
C_0(q)=q_2,
\qquad
C_1(q)=q_1.
\]

At either simplex vertex, one comparator costs zero, so

\[
\max_{v\text{ vertex}}O(v)=0.
\]

At the uniform interior law,

\[
q=(1/2,1/2),
\]

both comparators cost \(1/2\), giving

\[
O(q)=1/2.
\]

Thus

\[
\boxed{
\max_qO(q)=\frac12
>
0=\max_{v\text{ vertex}}O(v).
}
\]

Over \(T\) independent full-drift periods with all binary action sequences as
comparators, the same argument tensorizes periodwise:

\[
\boxed{
\max_qO(q)=\frac T2,
}
\]

while every pure path vertex has a clairvoyant comparator of cost zero.

---

## 4. Consequence for regret bounds

Let

\[
V_{\rm abs}=\min_x\max_qC_x(q),
\]

and

\[
O_{\min}=\min_qO(q),
\qquad
O_{\max}=\max_qO(q).
\]

Then

\[
V_{\rm abs}-O_{\max}
\le
\min_x\max_q[C_x(q)-O(q)]
\le
V_{\rm abs}-O_{\min}.
\]

Using only vertex oracle costs can overestimate the lower bound because

\[
\max_{v\text{ vertex}}O(v)
\le O_{\max},
\]

with strict inequality in the example above.

The repository therefore computes \(O_{\max}\) through the exact finite game,
not by taking the maximum oracle value among path vertices.

---

## Nonclaims

- The path-vertex mixture is a proof representation of one feasible barycenter
  path; it is not a claim that the source physically randomizes among vertices.
- Exact game support enumeration is bounded and is not a polynomial-time
  scalability theorem.
- The comparator mixture is a dual certificate, not necessarily a causal
  implementable oracle.
- Concavity of the oracle does not imply that every maximum is strictly
  interior.
- These internal finite-game identities are not evidence for simulation and do
  not identify parent-substrate resources.
