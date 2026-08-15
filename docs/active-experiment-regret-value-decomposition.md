# Resource-matched value decomposition for active-experiment minimax regret

## Scope

A public experiment can improve a deterministic minimax controller for more than one reason. Its observation may carry information about the globally fixed model or hidden state, but the same public observation may also act as a coordination random variable. Calling the entire performance improvement "information value" therefore overstates what was learned.

This layer separates those resources using two operations:

1. **convexification:** add an independent public seed that chooses one complete deterministic policy tree before the horizon;
2. **information erasure:** replace every experiment observation kernel by a one-symbol constant channel while preserving the experiment name and acquisition cost.

Both actual and information-erased controllers are evaluated against the **same model-informed causal oracle vector from the actual experiment problem**. Holding the benchmark fixed is necessary for a meaningful decomposition.

## 1. Fixed benchmark

Let the actual experiment menu be `E`. For fixed model `m`, let

\[
O_m(E)
\]

be the exact singleton-model oracle value under the actual menu. The oracle knows the globally fixed model identity before the horizon but does not know future hidden-state or observation realizations and pays the same acquisition costs.

For the rest of the decomposition write simply

\[
O=(O_m(E))_m.
\]

Importantly, `O` is **not recomputed** after information is erased. If the erased problem used its own weaker oracle, part of the value of information could disappear into the changed benchmark.

## 2. Deterministic and mixed benchmark gaps

For a deterministic complete public policy tree `pi`, let

\[
C(\pi)=(C_m(\pi))_m.
\]

Relative to the fixed actual oracle, its gap vector is

\[
G(\pi)=C(\pi)-O.
\]

The deterministic value for a policy class `P` is

\[
D(P)=\min_{\pi\in P}\max_m G_m(\pi).
\]

Now admit an independent public seed selecting complete deterministic policies with probabilities `lambda`. Expected modelwise costs are linear in `lambda`, so

\[
M(P)
=
\min_{\lambda\in\Delta(P)}
\max_m
\sum_{\pi}\lambda_\pi G_m(\pi).
\]

This is a finite rational zero-sum game. The implementation calls the repository's exact primal/dual support-enumeration solver and requires a zero rational duality gap.

A componentwise dominated pure policy is never needed in a mixture: replacing it by its dominator weakly decreases every model coordinate. Therefore the already Pareto-pruned root frontier is complete for this convexified problem.

## 3. Information erasure

For experiment `e`, define `erase(e)` by replacing every model-specific observation kernel with a one-symbol channel

\[
P(Y=0\mid M=m,S=s,e)=1
\]

for every model and hidden state, while preserving its acquisition cost.

The erased experiment carries no model information, no hidden-state information, and no endogenous random outcome. An independent public seed is added separately when computing `M`, so coordination resources can be matched without inventing a model-independent marginal distribution for the original signal.

Let

\[
P_A=P(E),
\qquad
P_0=P(\operatorname{erase}(E)).
\]

Because an actual controller can always ignore its observations and emulate an erased deterministic policy, and the same exogenous mixtures are available on both sides,

\[
\boxed{M(P_A)\le M(P_0).}
\]

Likewise,

\[
D(P_A)\le D(P_0).
\]

## 4. Exact decomposition identity

Define

\[
D_A=D(P_A),\quad M_A=M(P_A),\quad D_0=D(P_0),\quad M_0=M(P_0).
\]

Then algebra gives

\[
\boxed{
D_0-D_A
=
(D_0-M_0)
+
(M_0-M_A)
-
(D_A-M_A).
}
\]

The terms have distinct meanings:

\[
\boxed{
G_{\rm coord}=D_0-M_0\ge0
}
\]

is the coordination value of adding a public seed to the information-erased problem;

\[
\boxed{
G_{\rm info}=M_0-M_A\ge0
}
\]

is the information value after coordination resources are matched;

\[
\boxed{
G_{\rm residual}=D_A-M_A\ge0
}
\]

is the remaining value of an additional independent public seed in the actual experiment problem.

Thus total deterministic improvement is

\[
\boxed{
G_{\rm total}
=G_{\rm coord}+G_{\rm info}-G_{\rm residual}.
}
\]

The subtraction is important. Public randomness may already be supplied by the actual signal, so adding an external seed can be less valuable after information is restored.

## 5. Exact K3 boundaries

Consider three globally fixed one-state point-mass models with complete confusion `K3`. The actual model-informed oracle vector is

\[
O=(1,1,1).
\]

### Perfect revelation

For a free perfectly model-revealing experiment:

\[
D_0=1,
\qquad
M_0=\frac23,
\qquad
M_A=0,
\qquad
D_A=0.
\]

Therefore

\[
G_{\rm coord}=\frac13,
\qquad
G_{\rm info}=\frac23,
\qquad
G_{\rm residual}=0,
\]

and

\[
G_{\rm total}=1.
\]

### Source-independent public coin

For a uniform three-way public signal independent of model and source:

\[
D_0=1,
\qquad
M_0=\frac23,
\qquad
M_A=\frac23,
\qquad
D_A=\frac23.
\]

Hence

\[
G_{\rm coord}=\frac13,
\qquad
\boxed{G_{\rm info}=0},
\qquad
G_{\rm residual}=0.
\]

The improvement is coordination, not learning.

### No signal

For a one-symbol no-signal experiment:

\[
D_0=D_A=1,
\qquad
M_0=M_A=\frac23.
\]

The coordination and residual-randomization terms are both `1/3` and cancel exactly, leaving zero total experiment gain.

## 6. Why a fixed oracle matters

Suppose an experiment also reveals hidden-state information useful even when the model identity is already known. Erasing the signal may then worsen the singleton-model oracle. If the erased problem were compared with that newly weakened oracle, some genuine observation value would vanish from measured regret.

This module instead fixes `O(E)` from the actual problem and asks how much worse a less-informed policy class performs relative to that same causal benchmark.

This is a choice of estimand, not the only possible notion of experiment value. The repository records it explicitly so different benchmarks are not silently mixed.

## Nonclaims

- The decomposition does not claim that coordination and information are physical substances; they are operational differences between declared policy classes.
- The public-seed mixture is an explicit assistance resource.
- The oracle is model-informed but not path-clairvoyant.
- Experiment kernels and costs are supplied exactly rather than estimated from data.
- Information erasure preserves acquisition cost but not observation alphabet size.
- The finite exact zero-sum solver is bounded by explicit support-enumeration caps.
- None of these internal decision values is evidence for simulation or a parent-substrate resource bound.
