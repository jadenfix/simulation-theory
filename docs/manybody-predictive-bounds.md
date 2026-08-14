# Many-body predictive-state lower bounds

## Why move beyond two parameters?

The visibility+phase Bell family showed that a two-dimensional physical state can force a predictive packing that grows quadratically in inverse error tolerance. The next first-principles question is whether predictive complexity also grows with the number of physical subsystems.

This note gives two explicit bounded constructions. Neither is a claim about parent hardware or evidence for simulation.

## 1. Exact n-qubit computational-basis family

Consider the physical states

\[
|z\rangle,\qquad z\in\{0,1\}^n,
\]

and allow a future query to measure any coordinate qubit in the computational \(Z\) basis.

If \(z\neq z'\), there exists a coordinate \(i\) on which they differ. Querying \(i\) gives disjoint deterministic outcome laws. Hence the worst-query predictive total variation is

\[
\boxed{d(z,z')=1\quad\text{for every }z\neq z'.}
\]

Therefore all \(2^n\) basis states are mutually predictively distinct. Any renderer that must answer every allowed future coordinate query **exactly** needs at least

\[
\boxed{|\mathcal Z|\ge 2^n}
\]

predictive states, or

\[
\boxed{\text{internal predictive memory}\ge n\text{ bits}.}
\]

This lower bound is elementary but useful: exponential growth in the number of predictive states appears without invoking an external stabilizer-counting theorem.

## 2. Continuous product-qubit polarization family

Let

\[
q=(q_1,\ldots,q_d)\in[-r,r]^d,\qquad 0<r\le1,
\]

where qubit \(i\) has \(Z\)-polarization \(q_i\). Choose query coordinate \(i\) uniformly and observe \(s\in\{-1,+1\}\) with

\[
P(s\mid i,q)=\frac{1+s q_i}{2}.
\]

The joint law over the randomized query and response is

\[
P_q(i,s)=\frac1d\frac{1+s q_i}{2}.
\]

For two states \(q,u\), direct summation gives

\[
\begin{aligned}
\operatorname{TV}(P_q,P_u)
&=\frac12\sum_{i,s}\left|\frac{s(q_i-u_i)}{2d}\right|\\
&=\boxed{\frac{\|q-u\|_1}{2d}}.
\end{aligned}
\]

Thus an explicit many-body observable family produces a normalized \(L_1\) predictive geometry.

## Binary cube packing

Restrict to the \(2^d\) vertices

\[
q\in\{-r,+r\}^d.
\]

For distinct vertices, the minimum Hamming distance is one, so the minimum predictive TV is

\[
\frac{r}{d}.
\]

Consequently, whenever

\[
\epsilon<\frac{r}{2d},
\]

all \(2^d\) vertices are more than \(2\epsilon\) apart and form a certified packing. Hence

\[
\boxed{\text{memory bits}\ge d.}
\]

## q-ary grid packing

Use \(L\ge2\) equally spaced polarization levels in \([-r,r]\). There are

\[
L^d
\]

product states. The coordinate spacing is

\[
\Delta=\frac{2r}{L-1}.
\]

Two distinct grid points may differ in only one coordinate, giving minimum predictive TV

\[
\frac{\Delta}{2d}=\frac{r}{d(L-1)}.
\]

Therefore the entire grid is a \(2\epsilon\)-packing whenever

\[
\epsilon<\frac{r}{2d(L-1)}.
\]

The predictive memory bound is then

\[
\boxed{
\text{bits}\ge
\left\lceil d\log_2 L\right\rceil.
}
\]

This cleanly separates two sources of predictive complexity:

- **system dimension** \(d\), which contributes linearly;
- **per-coordinate resolution** \(L\), which contributes logarithmically.

Equivalently, within the regime where a full Cartesian grid remains separated, predictive memory behaves like

\[
\Theta\!\left(d\log\frac1\epsilon\right)
\]

up to the explicit dependence of admissible \(L\) on \(d\) and \(r\).

## A first-principles lesson

A renderer does not need to store "the entire universe" in a naive microscopic encoding. It needs enough predictive state to preserve all distinctions that future admissible queries can reveal. The lower bound therefore comes from the geometry of the **future query family**, not from counting atoms or equating internal mass with parent memory.

This also exposes a frequently omitted limitation: if the query family touches only a low-dimensional projection, hidden microscopic degrees of freedom can be compressed away without observational consequence. Conversely, when admissible queries independently probe many physical coordinates, the predictive-state count necessarily grows with that accessible dimension.

## Nonclaims

- These are product-state toy families, not a full many-body quantum field theory.
- The bounds concern internal distinguishable predictive states, not physical RAM in a parent universe.
- Entanglement is not yet used here; stronger families may increase predictive complexity.
- The uniform-coordinate query model is explicitly part of the continuous-family TV theorem.
- No result here is evidence that reality is simulated.

## Next target

The next high-value extension is an entangled/stabilizer family in which local or Pauli queries reveal relational information not reducible to independent per-qubit coordinates. A clean route is to construct an explicit graph-state subfamily and prove lower bounds directly from its measurement signatures rather than importing a global stabilizer-state counting formula.
