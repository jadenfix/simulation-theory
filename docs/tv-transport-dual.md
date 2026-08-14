# Exact primal-dual certificates for total-variation mass transport

## Scope

The distributionally robust coding lane solves

\[
\sup_{q:\operatorname{TV}(q,p)\le\rho}E_q[f]
\]

and its minimum analogue by exact probability-mass transport. This note gives a
second, independently replayable optimality route: a rational primal-dual
certificate with complementary slackness and zero gap.

The result is finite-dimensional and linear. It applies to a fixed value vector
\(f\), including a fixed codeword-length vector. It does not by itself solve
nonlinear risk functionals, allowed-error decoding, or uncertainty in the value
vector.

---

## 1. Reduction to donor selection

Let

\[
M=\max_i f_i.
\]

For maximization, any removed probability mass can be placed on a state whose
value is \(M\). A single maximum-valued state has enough capacity to absorb all
nonmaximum mass: its unused simplex capacity is at least the total nominal mass
outside the maximum face.

Let

\[
a_i\in[0,p_i]
\]

be the mass removed from state \(i\). Removing mass from a maximum-valued state
has zero gain and is never necessary before the objective saturates. The total
moved mass satisfies

\[
\sum_i a_i\le\rho.
\]

Define nonnegative gains

\[
g_i=M-f_i.
\]

The robust expectation is

\[
E_p[f]
+
\max_a
\sum_i g_i a_i
\]

subject to

\[
0\le a_i\le p_i,
\qquad
\sum_i a_i\le\rho.
\]

Thus the inner TV problem is an exact bounded fractional knapsack. Donor states
with the largest gains are precisely the shortest-valued states.

For minimization, let

\[
m=\min_i f_i,
\qquad
g_i=f_i-m,
\]

and solve the same donor problem. The optimal expectation is then

\[
E_p[f]-\max_a\sum_i g_i a_i.
\]

---

## 2. Linear-program dual

Consider the gain maximization

\[
\begin{aligned}
\text{maximize }&\sum_i g_i a_i\\
\text{subject to }&\sum_i a_i\le\rho,\\
&a_i\le p_i\quad\forall i,\\
&a_i\ge0\quad\forall i.
\end{aligned}
\]

Associate dual variable

\[
\lambda\ge0
\]

with the TV-budget constraint and

\[
\mu_i\ge0
\]

with the donor-capacity constraints. The dual is

\[
\begin{aligned}
\text{minimize }&ho\lambda+\sum_ip_i\mu_i\\
\text{subject to }&\lambda+\mu_i\ge g_i
\quad\forall i,\\
&\lambda\ge0,\quad\mu_i\ge0.
\end{aligned}
\]

Weak duality follows term by term. For every feasible primal and dual pair,

\[
\begin{aligned}
\sum_i g_i a_i
&\le
\sum_i(\lambda+\mu_i)a_i\\
&=
\lambda\sum_ia_i+\sum_i\mu_i a_i\\
&\le
\rho\lambda+\sum_i p_i\mu_i.
\end{aligned}
\]

---

## 3. One-dimensional threshold dual

For fixed \(\lambda\), the least feasible upper-bound dual is

\[
\mu_i=(g_i-\lambda)_+.
\]

The dual reduces to the convex piecewise-linear function

\[
\boxed{
D(\lambda)
=
\rho\lambda
+
\sum_i p_i(g_i-\lambda)_+,
\qquad
\lambda\ge0.
}
\]

Therefore the exact robust gain is

\[
\boxed{
G^*(p,g,\rho)
=
\min_{\lambda\ge0}
\left[
\rho\lambda
+
\sum_i p_i(g_i-\lambda)_+
\right].
}
\]

The scalar \(\lambda\) is the shadow price of one additional unit of TV radius.
Away from a breakpoint it is also the marginal slope of the robust expectation
profile.

---

## 4. Threshold from the greedy transport

Let \(a_i^*\) be the donor masses produced by the exact greedy transport.

### Radius zero

If

\[
\rho=0,
\]

choose

\[
\lambda^*=\max_i g_i.
\]

Then every \(\mu_i^*=0\), and both primal and dual gains are zero.

### Saturated objective with slack radius

If the transport has moved all positive-gain donor mass but

\[
\sum_i a_i^*<\rho,
\]

choose

\[
\lambda^*=0.
\]

The budget constraint is slack. Every positive-gain donor is exhausted, and

\[
\mu_i^*=g_i.
\]

### Active radius

Otherwise the TV budget is fully used. Choose

\[
\boxed{
\lambda^*
=
\min\{g_i:a_i^*>0\}.
}
\]

All donors with gain strictly above the threshold are exhausted. Donors with
gain strictly below the threshold are unused. Any partially used donor lies at
the threshold. Ties at the threshold may be split arbitrarily without changing
objective value.

Set

\[
\mu_i^*=(g_i-\lambda^*)_+.
\]

---

## 5. Complementary slackness

The returned certificate checks three exact identities.

### TV budget

\[
\boxed{
\lambda^*
\left(
\rho-\sum_i a_i^*
\right)=0.
}
\]

A positive threshold means the radius is fully used. Unused radius is possible
only after the objective has saturated and the threshold has fallen to zero.

### Donor upper bounds

\[
\boxed{
\mu_i^*(p_i-a_i^*)=0
\quad\forall i.
}
\]

If a donor has gain above the threshold, its upper-bound dual is positive and
all of its nominal mass is removed.

### Primal nonnegativity

\[
\boxed{
a_i^*(\lambda^*+\mu_i^*-g_i)=0
\quad\forall i.
}
\]

Any donor receiving positive allocation has zero reduced cost. States below the
threshold remain unused.

These identities imply equality throughout the weak-duality chain.

---

## 6. Zero rational duality gap

The primal gain is

\[
P^*
=
\sum_i g_i a_i^*.
\]

The dual gain is

\[
D^*
=
\rho\lambda^*+\sum_i p_i\mu_i^*.
\]

Using complementary slackness,

\[
\begin{aligned}
D^*-P^*
&=
\lambda^*
\left(
\rho-\sum_i a_i^*
\right)
+
\sum_i\mu_i^*(p_i-a_i^*)\\
&\quad+
\sum_i a_i^*(\lambda^*+\mu_i^*-g_i)\\
&=0.
\end{aligned}
\]

Hence

\[
\boxed{P^*=D^*.}
\]

The implementation stores the rational primal and dual objectives and requires

\[
\boxed{D^*-P^*=0}
\]

exactly. No numerical tolerance is used.

---

## 7. Relation to the radius profile

Sort gains in decreasing order. The primal selects donor capacity in that order.
The robust gain is piecewise linear in \(\rho\), with slope equal to the active
gain threshold.

For maximization,

\[
g_i=M-f_i,
\]

so the slope is the gap between the maximum value and the active donor value.
As radius increases, donor values rise, gains fall, and the slope weakly
decreases. This is the concavity of the fixed-code worst-expectation profile.

At a breakpoint, several gains can tie. The subgradient interval consists of
the tied threshold values; any one produces an optimal dual certificate.

After saturation, the threshold is zero and the profile is flat.

---

## 8. Skew K4 thresholds

For nominal prior

\[
\left(
\frac7{10},
\frac1{10},
\frac1{10},
\frac1{10}
\right)
\]

and values

\[
(1,2,3,3),
\]

the maximizing gains are

\[
(2,1,0,0).
\]

At radius \(1/10\), only the gain-two donor is partially used:

\[
\lambda^*=2,
\qquad
\mu=(0,0,0,0),
\]

and

\[
P^*=D^*=\frac15.
\]

At radius \(3/4\), the gain-two donor is exhausted and the gain-one donor is
active:

\[
\lambda^*=1,
\qquad
\mu=(1,0,0,0).
\]

At radius one, the expectation has already saturated after moving \(4/5\)
mass:

\[
\lambda^*=0,
\]

with budget slack \(1/5\).

The tests also cover radius zero, constant value vectors, minimization, ties,
and seeded rational instances.

---

## 9. Certificate contents and boundaries

The exact dual receipt contains:

- nominal law and value vector;
- transport receipt and donor mass by state;
- gain vector;
- rational threshold \(\lambda\);
- rational upper-bound duals \(\mu_i\);
- TV-budget slack;
- every complementary-slackness product;
- primal gain, dual gain, and zero gap.

The certificate proves optimality for the declared finite TV-ball expectation
problem. It does not prove:

- that a TV ball is the correct empirical uncertainty set;
- a nonlinear distributionally robust objective;
- a KL- or Wasserstein-ball result;
- a dynamic or time-uniform uncertainty guarantee;
- a parent-hardware or simulation conclusion.
