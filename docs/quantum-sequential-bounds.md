# Adaptive phase-drift transcript model

## Process

Let a hidden state begin at

\[
(v,\phi_0)
\]

with deterministic phase drift \(\omega\). At trial \(t\),

\[
\phi_t=\phi_0+t\omega\pmod{2\pi}.
\]

A deterministic policy may choose the next Bell setting pair as a function of the complete observed outcome history. The outcome law at trial \(t\) is then the visibility-phase law evaluated at \(\phi_t\).

The implementation in `src/simtheory/quantum_sequence.py` recursively enumerates the exact finite transcript distribution, including adaptive setting choices.

## Transcript refinement monotonicity

Fix two hidden processes and one deterministic adaptive policy. Let \(P_T,Q_T\) denote their length-\(T\) outcome transcript laws. The length-\(T\) transcript is a measurable projection of the length-\(T+1\) transcript. Total variation contracts under measurable maps, hence

\[
\boxed{
\operatorname{TV}(P_T,Q_T)
\le
\operatorname{TV}(P_{T+1},Q_{T+1}).
}
\]

So accumulated observations cannot reduce distinguishability when the full historical transcript is retained. The test suite checks this finite property for explicit process pairs.

## Adaptive predictive-state packing

For a finite hypothesis family \(\mathcal H\) of hidden phase processes, horizon \(T\), policy \(\pi\), and approximation tolerance \(\epsilon\), any subset satisfying

\[
\operatorname{TV}
\bigl(P_{h,T}^{\pi},P_{h',T}^{\pi}\bigr)
>2\epsilon
\]

for all distinct \(h,h'\) is a certified horizon-\(T\) predictive packing. Therefore an \(\epsilon\)-accurate renderer for every member of this bounded family requires at least as many predictive states as the packing cardinality.

The implementation constructs such packings directly from exact transcript laws and reports

\[
\text{memory bits}\ge\lceil\log_2 K_T\rceil.
\]

This is the first repository model where the lower-bound object is an **adaptive multi-step physical transcript**, rather than a one-shot arbitrary probability vector.

## Why this matters for lazy rendering

A lazy renderer is not challenged merely by producing the correct one-step marginal. It must preserve the joint law of every retained historical answer under future adaptive measurement choices. The phase-drift model makes that obligation concrete: the renderer must maintain enough predictive state to answer later measurements consistently with all previous outcomes and with the allowed dynamics.

## Nonclaims

- The phase drift is a bounded toy dynamics, not a model of universal time evolution.
- Transcript memory bounds are internal predictive-state bounds, not parent-hardware bounds.
- A chosen adaptive policy need not be globally optimal for distinguishing every process pair.
- Finite horizon growth does not by itself establish asymptotic state growth for realistic many-body quantum systems.
