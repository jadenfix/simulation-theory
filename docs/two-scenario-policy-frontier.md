# Exact two-scenario Pareto frontiers for policy trees

## Scope

The generic repeated-observation policy solver supports any finite number of
source-law scenarios. After enumerating distinct policy cost vectors, it checks
pairwise componentwise dominance. For `N` distinct vectors this requires up to

\[
N(N-1)
\]

ordered comparisons.

When there are exactly two source-law scenarios, the nondominated frontier has
a simpler exact construction.

This optimization changes only the dominance algorithm. It does not change:

- the complete policy-tree enumeration;
- exact scenario-cost calculations;
- the deterministic minimax objective;
- the shared-randomness zero-sum game;
- the certificate type or validity checks.

---

## 1. Two-dimensional dominance order

Each deterministic policy has a distinct cost pair

\[
(a_i,b_i)\in\mathbb Q^2.
\]

Policy `j` dominates policy `i` when

\[
a_j\le a_i,
\qquad
b_j\le b_i,
\]

with at least one strict inequality.

Sort the distinct pairs lexicographically:

\[
(a_1,b_1),
(a_2,b_2),
\ldots,
(a_N,b_N),
\]

where

\[
a_1\le a_2\le\cdots\le a_N,
\]

and ties in `a` are ordered by increasing `b`.

Scan from left to right while maintaining

\[
b_{\min}(i)
=
\min_{j<i}b_j.
\]

Pair `i` is nondominated exactly when

\[
\boxed{b_i<b_{\min}(i).}
\]

### Proof

If

\[
b_i\ge b_{\min}(i),
\]

some earlier pair `j` has

\[
a_j\le a_i,
\qquad
b_j\le b_i.
\]

Because the cost pairs are distinct, at least one inequality is strict, so `j`
dominates `i`.

Conversely, if

\[
b_i<b_j
\qquad\forall j<i,
\]

no earlier point dominates `i`. Every later point has

\[
a_j\ge a_i.
\]

A later point with equal `a` would have appeared earlier if its `b` were smaller,
by the tie ordering. A later point with larger `a` cannot dominate `i`.
Therefore `i` is nondominated.

---

## 2. Complexity

Sorting costs

\[
O(N\log N)
\]

comparisons. The scan is linear:

\[
O(N).
\]

Thus the exact two-scenario frontier is obtained in

\[
\boxed{O(N\log N)}
\]

comparisons rather than `O(N^2)` pairwise checks.

The policy enumeration itself remains exponential in the number of signal
history nodes. If there are `C` codebooks, `m` signal outcomes, and horizon `T`,
the raw deterministic policy count is

\[
C^{\sum_{t=1}^{T}m^t}.
\]

The frontier algorithm therefore removes a secondary quadratic bottleneck; it
does not make arbitrary long-horizon policy enumeration scalable.

---

## 3. Exact integration

The specialized solver:

1. enumerates every complete bounded policy tree;
2. computes exact source-cost, expected-switch, and total-cost pairs;
3. deduplicates equal pairs, retaining a canonical policy witness;
4. applies the sorted exact frontier construction;
5. populates the same `SequentialPolicyEnumeration` certificate used by the
   generic solver;
6. solves the same exact rational shared-randomness game.

The certificate validator independently recomputes every retained policy cost
and checks that no retained pair dominates another.

For a smaller two-period repeated-observation instance, the repository runs both
algorithms and requires identical:

- distinct cost counts;
- nondominated cost pairs;
- deterministic minimax value;
- shared-randomness minimax value.

The three-period switching-cost example then uses the specialized frontier to
audit thousands of distinct rational policy costs without raising the generic
quadratic comparison cap.

---

## Nonclaims

- The `O(N log N)` result applies only after distinct two-coordinate policy
  costs have been enumerated.
- More than two scenarios require a different multidimensional frontier
  algorithm or bounded pairwise audit.
- The result does not reduce the exponential number of complete policy trees.
- Exact rational sorting and comparison are not a large-instance performance
  benchmark.
- Policy-tree source-coding costs are not parent-substrate resources or evidence
  that reality is simulated.

---

## Next research targets

1. Add exact skyline algorithms for three and more scenarios.
2. Exploit sufficient-statistic policy states before policy enumeration.
3. Use branch-and-bound lower envelopes to avoid generating dominated policies.
4. Construct dynamic programs directly over likelihood states and installed
   codebooks.
5. Preserve exact rational witnesses while replacing exhaustive tree
   enumeration with certified pruning.
