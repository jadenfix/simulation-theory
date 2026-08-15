# Active experiment design under exact fixed-model minimax regret

## Scope

This layer keeps the active-experiment model fixed and changes only the decision criterion. Nature chooses one model once for the entire horizon. The public controller does not know that model identity. A benchmark oracle is told the fixed model identity before period one, but otherwise receives **no extra causal resources**: it uses the same experiment menu, pays the same acquisition costs, sees observations at the same times, faces the same hidden-state dynamics, and uses the same zero-error code universe.

This distinguishes model-identity regret from clairvoyant-path regret.

## 1. Model-informed causal oracle

For model `m`, let

\[
O_m
=
\min_{\pi_m}
E_m[C(\pi_m)]
\]

where `pi_m` may depend on the known model label and on subsequently observed public signals, but not on future hidden states or future signals.

The implementation computes `O_m` independently by solving the existing exact active-experiment problem on the singleton family `{m}` with the same experiment costs.

## 2. Shared-policy regret vector

Every deterministic public policy represented at the root frontier has a fixed-model expected-cost vector

\[
C(\pi)=(C_1(\pi),\ldots,C_M(\pi)).
\]

Define coordinate regret

\[
R_m(\pi)=C_m(\pi)-O_m.
\]

Because the singleton oracle can emulate any shared policy after being told `m`,

\[
\boxed{R_m(\pi)\ge0.}
\]

The exact minimax-regret criterion is

\[
\boxed{
R^*
=
\min_{\pi}
\max_m [C_m(\pi)-O_m].
}
\]

## 3. Why the existing Pareto frontier is sufficient

The oracle vector `O=(O_m)_m` is fixed across candidate shared policies. If cost vector `a` componentwise dominates `b`, then

\[
a_m\le b_m\quad\forall m
\]

implies

\[
a_m-O_m\le b_m-O_m\quad\forall m.
\]

Therefore subtracting the oracle vector preserves componentwise dominance. A policy removed by the exact robust-cost Pareto pruning cannot become minimax-regret optimal.

This is the main structural reuse theorem of the layer: no second dynamic-program recursion is required. Exact regret is a translated optimization over the already certified root frontier.

## 4. Robust cost and minimax regret are different objectives

The robust-cost policy solves

\[
\min_\pi \max_m C_m(\pi),
\]

while the regret policy solves

\[
\min_\pi \max_m(C_m(\pi)-O_m).
\]

The implementation returns both the minimax-regret optimum and the regret attained by the robust-cost optimum and certifies

\[
\boxed{
R^*\le R(\pi_{\rm robust}).
}
\]

Equality can occur; the theorem does not claim the optimizers must differ.

## 5. Exact K3 boundaries

Use three globally fixed one-state point-mass models on complete confusion `K3`.

With no signal, every deterministic code gives one model length one and two models length two. The model-informed oracle always assigns the short leaf to the known model, so

\[
O=(1,1,1),
\qquad
V_{\rm robust}=2,
\qquad
\boxed{R^*=1.}
\]

With a source-independent public three-way coin, a deterministic signal-contingent policy can rotate the short leaf uniformly. No model information is learned, yet

\[
C=(5/3,5/3,5/3),
\]

hence

\[
\boxed{R^*=2/3.}
\]

With a free perfectly model-revealing experiment,

\[
C=O=(1,1,1),
\qquad
\boxed{R^*=0.}
\]

Thus regret can fall for two logically distinct reasons: public coordination randomness and genuine model discrimination.

## 6. Cost accounting must be symmetric

If an experiment is compulsory and costs `kappa`, both the shared controller and the model-informed oracle pay `kappa`. For a compulsory fully revealing one-period K3 experiment with cost `2/3`, both have value `5/3`, so regret is zero.

Charging the experiment only to the shared controller would create an artificial regret term unrelated to model uncertainty.

If the menu contains multiple experiments, acquisition costs do not generally cancel because the oracle and shared controller may choose different experiments. The exact singleton solves handle this correctly.

## Nonclaims

- The oracle does not know future hidden-state or observation realizations.
- The oracle is not a parent-universe or simulator oracle; it is an internal decision benchmark.
- Model probabilities, transition matrices, experiment kernels, and costs remain supplied exact inputs rather than estimated quantities.
- Minimax regret is not Bayesian regret and is not obtained by subtracting two unrelated maxima.
- Public-randomness regret reduction is not epistemic information gain.
- Exact bounded finite computation is not evidence that reality is simulated.
