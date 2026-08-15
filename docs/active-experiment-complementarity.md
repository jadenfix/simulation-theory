# Complementarity and failure of diminishing returns in active experiment value

## Scope

This layer asks whether the value of adding an experiment necessarily has diminishing returns. It does not.

The setting remains finite active fixed-model coding. One model is chosen once and remains fixed for the horizon. The controller chooses experiments from a declared menu and then chooses zero-error prefix codes after public observations. The comparison uses one **fixed full-menu model-informed causal oracle vector** for every policy class, so moving regret benchmarks do not create the effect.

We also compute the same four policy classes after adding an independent public seed that mixes complete deterministic policy trees. Thus a strict complementarity result in the mixed problem cannot be blamed on unmatched coordination randomness.

## 1. Four policy classes

Let `B` be a baseline experiment menu and let `a,b` be two additional experiments. Define

\[
P_0=P(B),\qquad
P_a=P(B\cup\{a\}),\qquad
P_b=P(B\cup\{b\}),\qquad
P_{ab}=P(B\cup\{a,b\}).
\]

First solve the full menu `B+{a,b}` separately for every fixed model and obtain its model-informed causal oracle vector

\[
O=(O_m)_m.
\]

Every policy class is evaluated against this same vector.

For a deterministic class `P`, define

\[
V_D(P)
=
\min_{\pi\in P}
\max_m[C_m(\pi)-O_m].
\]

For the public-mixed class, an independent public seed selects one complete deterministic policy tree before the horizon:

\[
V_M(P)
=
\min_{\lambda\in\Delta(P)}
\max_m
\sum_{\pi}\lambda_\pi[C_m(\pi)-O_m].
\]

The mixed value is solved as an exact finite rational zero-sum game with matching primal and dual receipts.

## 2. Marginal experiment value

For either value function `V`, the gain from adding experiment `b` to menu `S` is

\[
\Delta_b(S)
=
V(S)-V(S\cup\{b\}).
\]

A diminishing-returns or submodularity condition would require

\[
\boxed{
\Delta_b(B)
\ge
\Delta_b(B\cup\{a\}).
}
\]

Complementarity is the reverse strict inequality:

\[
\boxed{
\Delta_b(B\cup\{a\})
>
\Delta_b(B).
}
\]

Equivalently, define the cost-form submodularity slack

\[
S
=
V(B\cup\{a\})+V(B\cup\{b\})-V(B)-V(B\cup\{a,b\}).
\]

Then

\[
\boxed{
S<0
}
\]

is strict complementarity.

## 3. Exact two-bit persistent-model construction

Use four globally fixed models corresponding to latent bits

\[
00,01,10,11.
\]

The source alphabet has three symbols and complete confusion `K3`.

Each model has two hidden temporal states. The initial state is known and emits the common source symbol `1`. A deterministic hidden transition then moves to the second state. The second-state source symbols are

\[
0,1,1,2
\]

for models

\[
00,01,10,11
\]

respectively.

The baseline experiment is one-symbol no signal.

Experiment `a` reveals the first latent model bit, independently of hidden temporal state. Experiment `b` reveals the second latent bit.

The model identity persists across periods, so a bit learned at period one remains known at period two.

### Full-menu oracle

A model-informed oracle knows both latent bits from the start. The first source is known to be symbol `1`, and the second source symbol is also known. It therefore assigns the short leaf to the known symbol in each period and has cost

\[
\boxed{
O=(2,2,2,2).
}
\]

This vector is held fixed for all four policy classes.

## 4. Deterministic complementarity

With no bit information, period one costs `1`, while in period two any of all three `K3` source symbols remains possible. A deterministic complete binary code must have worst relevant length `2`, so

\[
V_D(B)=1.
\]

Knowing only bit `a` leaves one of the source pairs

\[
\{0,1\}
\quad\text{or}\quad
\{1,2\}.
\]

Knowing only bit `b` has the same structure. A deterministic `K3` prefix code still has worst length `2` over either pair, so

\[
V_D(B+a)=V_D(B+b)=1.
\]

With both bits, the model and therefore the second source symbol are known before the second code action:

\[
V_D(B+a+b)=0.
\]

Thus

\[
\Delta_b(B)=0,
\]

while

\[
\Delta_b(B+a)=1.
\]

The exact complementarity margin is

\[
\boxed{1}
\]

and the cost-form submodularity slack is

\[
\boxed{-1}.
\]

The second bit is useless by itself under deterministic worst-case coding but decisive after the first bit has been learned.

## 5. Complementarity survives public-randomness matching

Now permit an independent public seed to mix complete deterministic policy trees.

With no bit information, the second-period `K3` minimax mixed length is

\[
\frac53.
\]

Since the first period costs `1` and the oracle costs `2`,

\[
\boxed{
V_M(B)=\frac23.
}
\]

With one bit known, only two final source symbols remain possible. Mixing equally between policies that give the short leaf to those two symbols gives second-period expected length

\[
\frac32,
\]

so

\[
\boxed{
V_M(B+a)=V_M(B+b)=\frac12.
}
\]

With both bits,

\[
V_M(B+a+b)=0.
\]

Therefore

\[
\Delta_b^M(B)
=
\frac23-\frac12
=
\frac16,
\]

while

\[
\Delta_b^M(B+a)
=
\frac12-0
=
\frac12.
\]

The resource-matched complementarity margin is

\[
\boxed{
\frac13
}
\]

and the mixed cost-form submodularity slack is

\[
\boxed{-\frac13}.
\]

Thus the failure of diminishing returns is not caused by deterministic coordination restrictions.

## 6. Structural interpretation

The experiments reveal **composable partial facts**. Neither bit determines the future source law alone, but the pair jointly determines it. This creates increasing returns because the value of one fact depends on which other facts have already been learned.

The phenomenon is distinct from:

- public-randomness value, because it survives explicit public-seed convexification;
- moving-regret-benchmark effects, because one full-menu oracle vector is fixed throughout;
- changing model identity, because one model remains globally fixed;
- post-hoc experiment selection, because the controller follows a causal public policy.

This means generic greedy guarantees that require monotone submodularity of experiment value cannot simply be imported into this class.

It does **not** imply that greedy experiment selection is always bad. Some restricted model families may possess submodularity or approximate-submodularity structure. Such structure must be proved from additional assumptions rather than presumed from the word "information."

## 7. A more abstract view

Let the latent model contain attributes

\[
Z=(Z_1,\ldots,Z_k).
\]

An experiment may reveal one attribute or one function of several attributes, while the eventual decision depends on another function

\[
f(Z).
\]

If the decision-relevant function has interaction terms, the value of revealing attributes can also have interactions. In Boolean language, parity is the extreme example: every strict subset of bits can leave the parity unresolved while the final bit determines it.

This suggests a general research direction: characterize experiment-value curvature from the functional decomposition of the decision-relevant sufficient statistic rather than assuming entropy-like diminishing returns.

## Nonclaims

- The result does not claim all active-experiment values are supermodular.
- It does not show greedy policies are always suboptimal.
- The public seed is an explicit assistance resource.
- The fixed oracle is model-informed but not future-path clairvoyant.
- All model probabilities, transitions, experiment kernels, and costs are supplied exact inputs.
- The exact construction is finite and bounded rather than a scalability theorem.
- None of these internal experiment values is evidence for simulation.
