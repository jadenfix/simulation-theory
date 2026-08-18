# Round 11 — two-view theorem boundary audit

**Paper:** *Identifiability Before Anthropic Bayes*  
**Author:** Jaden Fix, Tempera — `Jaden@Tempera.dev`  
**Status:** synthetic internal mathematical review, not independent peer review.

## Objective

Round 11 tried to break the theorem **Two repeated-view rigidity inside the row-stochastic gauge** by removing its assumptions one at a time. The purpose was not to prove the theorem by computation; the manuscript already contains an analytic proof. The purpose was to verify that the assumptions are substantive and that the paper does not accidentally suggest a stronger result.

The theorem assumes:

1. `K` has full row rank;
2. both views use the same channel and are conditionally independent given one persistent latent;
3. `A` is invertible, nonnegative, and row-stochastic;
4. `K' = A K`;
5. `pi' = pi A^{-1}` is strictly positive;
6. the repeated shared-latent two-view law is preserved.

Under these assumptions the manuscript proves that `A` is a permutation matrix.

## R11.1 — full row rank is necessary for this conclusion

Take a two-state latent model with a one-symbol observation alphabet,

```text
K = [[1],
     [1]].
```

Then `K` has row rank one rather than two. Let

```text
pi = pi' = (1/2, 1/2)
A  = [[3/4, 1/4],
      [1/4, 3/4]].
```

`A` is invertible, nonnegative, row-stochastic, and not a permutation. Because every row of `K` is identical,

```text
A K = K.
```

The one-view law is unchanged. The repeated shared-latent two-view law is the scalar `1` under both factorizations. Therefore a non-permutation gauge survives when full row rank is removed.

**Disposition:** assumption is substantive and must remain explicit.

## R11.2 — strict positivity of the transformed prior is necessary for the monomiality step

Take

```text
K   = I_2
pi  = (1, 0)
pi' = (1, 0)
A   = [[1,   0],
       [1/2, 1/2]].
```

`K` has full row rank. `A` is invertible, nonnegative, row-stochastic, and non-permutation. Since `pi = pi' A`, equivalently `pi' = pi A^{-1}`, the one-view law is preserved. Moreover,

```text
A^T diag(pi') A = diag(1,0) = diag(pi),
```

so the repeated two-view law is preserved as well.

The manuscript proof fails exactly where expected: from

```text
0 = sum_i pi'_i A_ij A_ik
```

one cannot infer `A_ij A_ik = 0` in rows whose `pi'_i` is zero.

**Disposition:** strict positivity is substantive and must not be weakened to mere nonnegativity without a different statement.

## R11.3 — nonnegativity is part of both the proof and channel semantics

The off-diagonal argument uses nonnegativity of every summand. If signed `A` were permitted, cancellation could occur. More fundamentally, nonnegativity is what makes each row of `A K` a convex combination of channel rows, preserving its interpretation as a stochastic observation law. The theorem is intentionally a nonnegative row-stochastic gauge theorem, not a theorem about arbitrary invertible linear changes of basis.

**Disposition:** retain the assumption and the gauge-specific theorem title.

## R11.4 — identity-channel finite searches are not enough as a falsification aid

Earlier bounded searches used `K = I`, because the analytic cancellation reduces the theorem to the weighted-orthogonality condition in that coordinate system. That is mathematically legitimate, but a stronger implementation audit should also exercise a non-identity full-row-rank stochastic channel.

A new exact-rational regression test therefore uses a nontrivial two-state, three-outcome channel and enumerates bounded two-by-two row-stochastic gauges. Among admissible positive-transformed-prior candidates preserving both one-view and repeated two-view laws, only the two label permutations survive.

**Disposition:** applied as a test-level strengthening, not as a new theorem.

## R11.5 — repeated versus redrawn latent structure remains essential

If the latent is redrawn independently between views, the joint law is `q \otimes q`, which contains no more factorization information than the one-view marginal `q`. The theorem instead uses

```text
T = K^T D_pi K,
```

which encodes persistence of the same latent state across the two conditionally independent observations.

**Disposition:** already explicit in the manuscript and retained.

## Decision

**Pass.** The theorem survived re-derivation, and the attempted assumption removals produced counterexamples exactly where the proof indicates they should. No theorem broadening is justified. The strongest improvement is evidential: rank and positivity are now backed by constructive negative witnesses, and the bounded implementation audit includes a non-identity channel.
