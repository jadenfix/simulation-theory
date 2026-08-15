# Observation lattices and higher-order experiment interactions

## Scope

Pairwise complementarity is only the first nontrivial interaction order. This layer builds the complete finite set function over deterministic experiment subsets and computes its exact Boolean-lattice Möbius transform. The coefficients identify which combinations of experiments contribute value that cannot be represented by lower-order terms.

The model is a static exact subcase of the active fixed-model program:

- one model `m` is fixed;
- model `m` has one declared categorical source law `p_m` on a zero-error confusion graph;
- deterministic experiment `j` reveals a finite label `z_j(m)`;
- observing a subset `S` partitions models according to the joint signature `(z_j(m))_{j in S}`;
- after observing the signature, the controller chooses a zero-error prefix code;
- every experiment subset is evaluated against one fixed model-informed oracle vector.

The controller is solved both deterministically and after an independent public seed convexifies code choices within each observation cell.

## 1. Observation partitions

For experiment subset `S`, models `m,m'` are observationally equivalent when

\[
z_j(m)=z_j(m')
\qquad\forall j\in S.
\]

This equivalence relation partitions the model family into cells

\[
\Pi_S.
\]

If `S` is contained in `T`, then `Pi_T` refines `Pi_S`. More experiments can split cells but cannot merge previously distinguishable models.

For each model, define its model-informed oracle code value

\[
O_m
=
\min_c E_{p_m}[\ell_c].
\]

This vector is independent of `S` and therefore removes moving-benchmark effects.

## 2. Cell values

Inside observation cell `C`, deterministic benchmark gap is

\[
D(C)
=
\min_c
\max_{m\in C}
\left(E_{p_m}[\ell_c]-O_m\right).
\]

With an independent public seed mixing complete codebooks,

\[
M(C)
=
\min_{\lambda}
\max_{m\in C}
\sum_c\lambda_c
\left(E_{p_m}[\ell_c]-O_m\right).
\]

The mixed problem is an exact finite rational zero-sum game.

Because the public observation identifies the cell before code choice, the whole-subset values are

\[
\boxed{
D(S)=\max_{C\in\Pi_S}D(C)
}
\]

and

\[
\boxed{
M(S)=\max_{C\in\Pi_S}M(C).
}
\]

Partition refinement immediately gives monotonicity:

\[
S\subseteq T
\implies
D(T)\le D(S),
\quad
M(T)\le M(S).
\]

Monotonicity alone places no sign restriction on higher-order interactions.

## 3. Boolean-lattice Möbius transform

For any experiment-subset value function `V`, define coefficients

\[
\mu(S)
=
\sum_{T\subseteq S}
(-1)^{|S|-|T|}V(T).
\]

Then Möbius inversion gives

\[
\boxed{
V(S)=\sum_{T\subseteq S}\mu(T).
}
\]

Interpretation is operational:

- `mu(empty)` is the baseline value;
- singleton coefficients are first-order contributions;
- pair coefficients capture pairwise interactions not explained by singleton terms;
- order-`k` coefficients capture residual `k`-way interactions after every lower-order contribution has been removed algebraically.

The coefficient signs are not universally constrained. In the present cost convention, negative coefficients can encode complementarity because adding the complete interacting set causes a larger cost drop than lower-order terms predict.

## 4. Exact k-bit parity family

Let the fixed models be all bit strings

\[
x\in\{0,1\}^k.
\]

Experiment `j` reveals bit `x_j`. The downstream source law is a point mass at the parity

\[
y(x)=x_1\oplus\cdots\oplus x_k,
\]

embedded as source symbol `0` or `1` of complete confusion `K3`.

The third K3 symbol is retained in the zero-error code universe even though no model assigns it positive mass.

### Model-informed oracle

Knowing model `x` means knowing parity, so the oracle assigns the depth-one leaf to the realized source symbol:

\[
\boxed{O_x=1.}
\]

### Every proper experiment subset

If `S` omits at least one bit, every observation cell contains models of both parities: flip one unobserved bit and parity changes without changing the observed signature.

Therefore the deterministic controller must protect both source symbols `0` and `1`. In a complete binary prefix code for K3, at most one symbol has length one, so the minimum worst relevant length is two:

\[
\boxed{D(S)=1\qquad S\subsetneq[k].}
\]

After an independent public seed mixes the short leaf equally between symbols `0` and `1`, both receive expected length `3/2`, so

\[
\boxed{M(S)=\frac12\qquad S\subsetneq[k].}
\]

### Full experiment set

All bits determine parity, hence every observation cell contains one model and one known source symbol:

\[
\boxed{D([k])=M([k])=0.}
\]

## 5. Pure top-order interaction theorem

The parity value function is constant on every strict subset and drops only at the full set. Its Möbius transform therefore has

\[
\mu_D(\varnothing)=1,
\]

\[
\boxed{
\mu_D(S)=0
\quad
\forall\varnothing\ne S\subsetneq[k],
}
\]

and

\[
\boxed{
\mu_D([k])=-1.
}
\]

Likewise for the public-mixed value:

\[
\mu_M(\varnothing)=\frac12,
\]

\[
\boxed{
\mu_M(S)=0
\quad
\forall\varnothing\ne S\subsetneq[k],
}
\]

and

\[
\boxed{
\mu_M([k])=-\frac12.
}
\]

Thus all nonconstant experiment value can live at one arbitrarily high interaction order, even after coordination randomness is matched.

The repository independently checks the formulas for `k=2,3,4` using exact code enumeration, observation partitions, rational zero-sum games, and the Möbius transform.

## 6. Why this matters

Many experimental-design heuristics implicitly assume that useful evidence arrives as approximately additive or diminishing-return contributions. The parity family gives the opposite extreme: every proper collection of facts leaves the decision-relevant quantity unresolved, and only the final missing fact unlocks the value.

This parallels other repository results in which information is invisible to all proper local marginals yet appears in one global parity relation. Here the object is not a quantum state but the decision value induced by observations of latent model attributes.

A more general lesson is:

\[
\boxed{
\text{interaction order of observations}
\text{ is controlled by the functional structure of the decision-relevant sufficient statistic.}
}
\]

If the sufficient statistic is additive/separable in observed attributes, low-order value structure may be possible. If it contains parity, threshold, conjunction, or other interactions, high-order experiment value can appear naturally.

## 7. Research frontier

The next questions are structural rather than computational:

1. Which classes of decision-relevant functions guarantee submodular experiment value?
2. Can approximate low-degree representations of the sufficient statistic bound high-order Möbius mass?
3. How do noise and approximate observations attenuate high-order coefficients?
4. Can Fourier analysis on the Boolean cube connect functional degree to experiment-value interaction degree?
5. Which adaptive policies recover value efficiently when static greedy selection has no generic submodular guarantee?

These questions create a bridge between experiment design, communication complexity, Boolean function analysis, and predictive-state geometry.

## Nonclaims

- Möbius coefficients are operational interaction coefficients, not physical interaction energies.
- The parity formulas use the declared K3 zero-error coding objective.
- The theorem does not claim every high-degree Boolean function induces the same value geometry.
- Public mixing is an explicit assistance resource.
- Exact finite enumeration is not a polynomial-time scalability theorem.
- None of these interaction coefficients is evidence for simulation.
