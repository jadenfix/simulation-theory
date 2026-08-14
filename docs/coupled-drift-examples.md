# Coupled-drift worked examples

This file isolates small exact instances that can be checked by hand before
reading the general implementation.

## Example 1: reversing binary objectives

Let

\[
p=(1/2,1/2),
\qquad
\eta_1=\eta_2=1/4.
\]

Write \(x_t=q_t(2)\). Then

\[
|x_1-1/2|\le1/4,
\qquad
|x_2-x_1|\le1/4.
\]

For costs

\[
g_1=(0,1),
\qquad
g_2=(1,0),
\]

the cumulative objective is

\[
x_1+1-x_2.
\]

The transition bound gives \(x_1-x_2\le1/4\), hence the value is at most
\(5/4\). The path \((x_1,x_2)=(3/4,1/2)\) attains it.

Independently optimizing the first and second marginals gives \(x_1=3/4\) and
\(x_2=0\), which are separated by TV \(3/4\) and cannot be one admissible
transition. The independent value \(7/4\) is therefore a strict relaxation.

## Example 2: aligned binary objectives

Keep the same initial law and drift limits, but use

\[
g_1=g_2=(0,1).
\]

The canonical path moves toward state two at maximum speed:

\[
x_1=3/4,
\qquad
x_2=1.
\]

The value is

\[
3/4+1=7/4.
\]

Here the independent marginal optima are jointly reachable because both
periods prefer the same movement direction.

## Example 3: uniform K3 and a rotating short leaf

Every full binary prefix code for three distinct messages has one length-one
leaf and two length-two leaves. Start from

\[
p=(1/3,1/3,1/3),
\qquad
\eta_1=\eta_2=1/6.
\]

Use

\[
\ell_1=(1,2,2),
\qquad
\ell_2=(2,1,2).
\]

The cost is

\[
4-q_{1,1}-q_{2,2}.
\]

An admissible worst path is

\[
q_1=(1/4,1/4,1/2),
\qquad
q_2=(1/4,1/12,2/3).
\]

Both transitions have TV \(1/6\), and the cost is

\[
4-1/4-1/12=11/3.
\]

No path can do worse because \(q_{1,1}+q_{1,2}\ge1/2\) and
\(q_{2,2}\ge q_{1,2}-1/6\), so \(q_{1,1}+q_{2,2}\ge1/3\).

A static tree allows the adversary to reduce its short-leaf probability from
\(1/3\) to \(1/6\) and then to zero, giving

\[
(2-1/6)+2=23/6.
\]

Thus rotation saves \(1/6\) before switching cost.

## Example 4: switching threshold

With one switch and penalty \(\kappa\), the rotating total is

\[
11/3+\kappa.
\]

The static total is \(23/6\). Therefore:

\[
\kappa<1/6
\quad\Rightarrow\quad
\text{rotate},
\]

\[
\kappa>1/6
\quad\Rightarrow\quad
\text{remain static}.
\]

At equality, the repository's deterministic tie-break chooses fewer switches.

## Example 5: constant shifts do not alter coupling gaps

Add a constant \(a_t\) to every state cost at period \(t\):

\[
g'_t=g_t+a_t\mathbf 1.
\]

Every source law sums to one, so

\[
q_t^\top g'_t=q_t^\top g_t+a_t.
\]

Both the exact coupled value and the independent marginal relaxation increase
by \(\sum_ta_t\). Their difference is unchanged. This is checked exactly in
the property suite.
