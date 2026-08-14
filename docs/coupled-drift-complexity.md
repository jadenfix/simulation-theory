# Coupled-drift bounded-search complexity

The current implementation prioritizes exact finite certificates over large-
instance scalability.

For alphabet size \(n\) and horizon \(T\), the path has

\[
d=T(n-1)
\]

free coordinates. The exact TV representation uses

\[
m=T\left[n+2(2^{n-1}-1)\right]
\]

halfspaces. Naive active-basis enumeration examines

\[
\binom{m}{d}
\]

candidate primal bases.

The exact dual has one nonnegative variable per path halfspace and \(d\)
equality constraints. Its bounded support enumeration also considers at most

\[
\binom{m}{d}
\]

basic supports.

If the undominated deterministic code universe contains \(K\) candidates, an
unrestricted horizon-\(T\) precommitted sequence search contains

\[
K^T
\]

sequences before switch restrictions.

These counts explain the repository's fail-closed caps. They are not claimed to
be optimal algorithms.

Promising scalable replacements include:

- exact rational simplex with replayable bases;
- separation-oracle and column-generation methods;
- dynamic programming over a finite path-state discretization with certified
  bounds;
- exploiting network-flow structure in finite-TV transport;
- code-sequence shortest paths once adversarial continuation values are
  available;
- branch-and-bound using componentwise and continuation-value dominance;
- symmetry reduction for exchangeable source states and codebooks.

Any scalable replacement must preserve independently checkable receipts rather
than returning only a floating solver status.
