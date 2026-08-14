# Canonical CHSH disk geometry

## Exact norm identity

Represent a visibility-phase state by

\[
q=(x,y)=(v\cos\phi,v\sin\phi),\qquad \|q\|_2\le 1.
\]

For a setting difference \(\theta=\alpha-\beta\), the correlation is

\[
r_\theta(q)=x\cos\theta+y\sin\theta.
\]

For the canonical CHSH schedule the four setting differences are

\[
-\pi/4,\quad \pi/4,\quad \pi/4,\quad 3\pi/4
\]

with equal weight. For \(\Delta q=(\Delta x,\Delta y)\), the exact one-trial predictive TV is

\[
\frac18\sum_{j=1}^4 |s_j\cdot\Delta q|.
\]

Substituting the four directions gives

\[
\operatorname{TV}
=
\frac{1}{4\sqrt2}
\left(
|\Delta x+\Delta y|+|\Delta x-\Delta y|
\right).
\]

Using

\[
|a+b|+|a-b|=2\max(|a|,|b|)
\]

we obtain the closed form

\[
\boxed{
\operatorname{TV}(P_q,P_{q'})
=
\frac{\|q-q'\|_\infty}{2\sqrt2}.
}
\]

Thus the canonical Bell experiment equips the physical unit disk with an exactly known predictive metric.

## Constructive quadratic packing

The square

\[
Q=[-1/\sqrt2,1/\sqrt2]^2
\]

lies inside the physical unit disk. Two points are more than \(2\epsilon\) apart in predictive TV whenever

\[
\|q-q'\|_\infty>4\sqrt2\,\epsilon.
\]

Let

\[
m=\left\lceil\frac{1}{4\epsilon}\right\rceil,
\qquad 0<\epsilon<1/4.
\]

Place an \(m\times m\) Cartesian grid across the inscribed square. Its adjacent coordinate spacing is

\[
\Delta=\frac{\sqrt2}{m-1}.
\]

Because \(m-1<1/(4\epsilon)\),

\[
\Delta>4\sqrt2\epsilon.
\]

Therefore all distinct grid points are separated by more than \(2\epsilon\) in predictive TV and form a certified packing of size

\[
\boxed{
K_\epsilon\ge
\left\lceil\frac{1}{4\epsilon}\right\rceil^2.
}
\]

Applying the predictive-state packing theorem gives

\[
\boxed{
\text{memory bits}
\ge
\left\lceil
\log_2
\left(
\left\lceil\frac{1}{4\epsilon}\right\rceil^2
\right)
\right\rceil.
}
\]

As \(\epsilon\to0\), this constructive bound scales as

\[
2\log_2(1/\epsilon)-4+O(1).
\]

The important point is dimensional: the one-parameter visibility family had packing growth proportional to \(1/\epsilon\), whereas this physically explicit two-dimensional family has a constructive packing proportional to \(1/\epsilon^2\).

## Scope

This theorem concerns predictive states needed to approximate this bounded observable family under the canonical CHSH schedule. It does not imply that a parent simulator uses classical bits, and it does not establish a lower bound for arbitrary quantum field theories or the universe as a whole.
