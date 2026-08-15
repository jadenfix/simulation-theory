# Active-experiment menu expansion and moving regret benchmarks

## Scope

Adding an experiment to a menu cannot make the controller's absolute optimization problem worse: the old experiment menu is still available. Minimax regret is different because its benchmark is a model-informed oracle that receives the same enriched menu. If the oracle benefits more than the shared controller, own-oracle regret can increase even while robust cost weakly decreases.

This layer makes that benchmark motion explicit.

Let `B` be a baseline experiment menu and `E` an enriched menu with

\[
B\subseteq E.
\]

One globally fixed model remains responsible for the full horizon in both problems.

## 1. Oracle shift

Let

\[
O_m^B
\]

be the exact model-informed causal oracle value under baseline menu `B`, and

\[
O_m^E
\]

its value under enriched menu `E`.

Because an oracle with the enriched menu may ignore every new experiment,

\[
\boxed{O_m^E\le O_m^B.}
\]

Define the coordinatewise oracle improvement

\[
\boxed{\delta_m=O_m^B-O_m^E\ge0.}
\]

The vector `delta` measures movement of the regret benchmark itself.

## 2. Fixed-benchmark controller gain

Baseline own-oracle minimax regret is

\[
R_B
=
\min_{\pi\in P_B}
\max_m[C_m(\pi)-O_m^B].
\]

Enriched own-oracle regret is

\[
R_E
=
\min_{\pi\in P_E}
\max_m[C_m(\pi)-O_m^E].
\]

To isolate controller improvement from benchmark movement, evaluate baseline policies against the **enriched** oracle vector:

\[
D_B^E
=
\min_{\pi\in P_B}
\max_m[C_m(\pi)-O_m^E].
\]

Since `P_B` is contained in `P_E`,

\[
\boxed{
\Delta_{\rm ctrl}
=D_B^E-R_E
\ge0.
}
\]

This is the deterministic controller gain under a fixed benchmark.

The same construction can be applied after convexifying both policy frontiers with an independent public seed, producing an exact mixed fixed-benchmark gain.

## 3. Exact regret-shift bounds

For a baseline policy `pi`, define old regret coordinates

\[
r_m(\pi)=C_m(\pi)-O_m^B.
\]

Under the enriched benchmark the same policy has coordinates

\[
r_m(\pi)+\delta_m.
\]

For every vector `r`,

\[
\max_m r_m+\min_m\delta_m
\le
\max_m(r_m+\delta_m)
\le
\max_m r_m+\max_m\delta_m.
\]

Minimizing over baseline policies gives

\[
R_B+\min\delta
\le
D_B^E
\le
R_B+\max\delta.
\]

Substituting

\[
R_E=D_B^E-\Delta_{\rm ctrl}
\]

yields

\[
\boxed{
R_B+\min\delta-\Delta_{\rm ctrl}
\le
R_E
\le
R_B+\max\delta-\Delta_{\rm ctrl}.
}
\]

The same inequalities hold for the independently public-mixed policy classes.

## 4. Uniform oracle shift

If every model-informed oracle improves by one common amount `d`,

\[
\delta_m=d
\qquad\forall m,
\]

then the max operation commutes with that constant translation and the bounds collapse to equality:

\[
\boxed{
R_E
=R_B+d-\Delta_{\rm ctrl}.
}
\]

Thus own-oracle regret rises precisely when the benchmark improves more than the shared controller:

\[
\boxed{
R_E>R_B
\iff
d>\Delta_{\rm ctrl}.
}
\]

This is not a paradox. Regret is a relative quantity.

## 5. Exact K4 counterexample

Consider complete confusion `K4` and two globally fixed models.

- Model `L` has two static hidden states, emitting source symbols `0` and `1` equiprobably.
- Model `R` has two static hidden states, emitting source symbols `2` and `3` equiprobably.

The supports are disjoint.

### Baseline menu

The baseline contains only a one-symbol no-signal experiment.

A balanced four-message binary prefix code has lengths

\[
(2,2,2,2),
\]

so shared robust cost is

\[
\boxed{V_B=2.}
\]

A model-informed oracle knows which source pair is possible and can use an unbalanced complete tree with lengths `1` and `2` on that pair, giving

\[
\boxed{O^B=(3/2,3/2).}
\]

Hence

\[
\boxed{R_B=1/2.}
\]

### Enriched menu

Add two specialized experiments.

- Experiment `e_L` reveals the hidden state under model `L`, but emits a fair public coin independent of hidden state under model `R`.
- Experiment `e_R` does the symmetric operation.

A model-informed oracle chooses its own specialized experiment and learns the actual source symbol before coding, so

\[
\boxed{O^E=(1,1).}
\]

The oracle shift is uniform:

\[
\boxed{\delta=(1/2,1/2).}
\]

But no deterministic shared controller knows which specialized experiment is the relevant one before choosing it. Its robust cost remains

\[
\boxed{V_E=2.}
\]

and its fixed-benchmark controller gain is zero:

\[
\Delta_{\rm ctrl}=0.
\]

Therefore

\[
\boxed{
R_E
=R_B+1/2
=1.
}
\]

So a strictly richer experiment menu leaves absolute robust cost unchanged while **doubling minimax regret** from `1/2` to `1`.

This is an exact coding example, not a synthetic loss table.

### Public mixing

The same phenomenon survives convexification. The baseline public-mixed own regret is

\[
1/2,
\]

while the enriched menu permits a mixed fixed-benchmark controller gain of `1/4`. Since the oracle shift is `1/2`, mixed own regret becomes

\[
\boxed{3/4.}
\]

Thus public randomization softens but does not remove the moving-benchmark effect.

## 6. Zero oracle shift restores monotonic regret

If

\[
O^B=O^E,
\]

then `delta=0`, so

\[
\boxed{
R_E=R_B-\Delta_{\rm ctrl}\le R_B.
}
\]

For one-period point-mass `K3`, adding a source-independent public three-way coin does not improve the model-informed oracle, but lowers deterministic shared regret from `1` to `2/3`. The exact controller gain is `1/3`.

## 7. Why this matters for model comparison

A decreasing loss and an increasing regret can occur simultaneously because they answer different questions:

- **robust cost:** how well can the shared controller perform?
- **own-oracle regret:** how far is the shared controller from a model-informed benchmark with the same menu?

When the action or experiment set changes, comparing regret numbers without tracking the oracle shift can misdiagnose real improvement as deterioration—or vice versa.

The same issue appears in simulation arguments whenever a richer hypothesis class, observation interface, or intervention menu also changes the benchmark used to judge explanatory or predictive performance.

## Nonclaims

- The theorem does not say regret is a bad metric; it says its benchmark must be tracked.
- The K4 values are exact for the declared finite coding instance only.
- Experiment kernels and model probabilities are supplied rather than estimated.
- The public-mixed comparison treats shared randomness as an explicit assistance resource.
- The model-informed oracle does not know future hidden-state or signal realizations.
- None of these internal decision values is evidence for simulation.
