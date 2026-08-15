# Blackwell information order versus public-randomness resources

## Statement

Blackwell comparison orders statistical experiments by what information one can
simulate from another **when stochastic post-processing is allowed**. A
minimax decision problem that restricts the controller to deterministic public
policies but does not separately supply randomization can therefore assign
different values to two Blackwell-equivalent experiments.

This is not a contradiction. The stochastic kernel used in a Blackwell
simulation is itself a randomization resource.

## Exact K3 witness

Use three fixed one-state source models and complete confusion \(K_3\). Every
binary zero-error prefix code has a length vector that is a permutation of

\[
(1,2,2).
\]

Consider two experiments.

### Experiment A: constant signal

Every model emits one deterministic public symbol. No random public event occurs
before the code choice. A deterministic controller must choose one code, so

\[
V_A=2.
\]

### Experiment B: source-independent public coin

Every model emits one of three public labels uniformly:

\[
P_B(Y=j\mid M=m)=\frac13
\qquad\forall m,j.
\]

The signal is independent of the model. A deterministic policy can nevertheless
rotate which source symbol gets the short leaf across the three labels, giving

\[
V_B=\frac53.
\]

Thus

\[
\boxed{V_B<V_A}
\]

even though B contains no more information about the model.

## Blackwell equivalence

A can simulate B by applying the stochastic garbling kernel

\[
G_{A\to B}=(1/3,1/3,1/3)
\]

to its single output.

B can simulate A by deterministically mapping each of its three labels to the
same symbol:

\[
G_{B\to A}
=
\begin{pmatrix}1\\1\\1\end{pmatrix}.
\]

Therefore A and B are Blackwell-equivalent statistical experiments.

The different deterministic minimax values arise because the A-to-B simulation
uses fresh randomness. If that same source-independent public randomness is
already admitted to the controller, the value discrepancy is removed: the
constant experiment can generate the public coin before acting.

## Consequence

A scalar called “value of information” is ill-defined unless the admissible
randomization resources are held fixed. In particular,

\[
\boxed{
\text{Blackwell-equivalent information}
\not\Rightarrow
\text{equal deterministic minimax decision value}
}
\]

when one experiment physically supplies random public outcomes and the other
does not.

For simulation-theory arguments this prevents a subtle category error: improved
decision performance after observing a noisy or random signal need not mean the
signal supplied evidence about a simulator hypothesis. Part of the gain can be
pure coordination randomness.

## Boundary

The repository's earlier one-shot observation-channel lane proves Blackwell
monotonicity for the **shared-randomness** value. The present counterexample is
precisely why that resource qualifier is necessary. This note does not dispute
Blackwell's statistical ordering; it distinguishes information from the
randomization needed to implement stochastic garblings.
