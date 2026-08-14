# Abstract notes: temporal compatibility, optionality, and predictive control

This note records the broader structure exposed by the coupled-drift program.
It is intentionally separate from the theorem derivation so that conceptual
extensions do not silently inherit theorem status.

## 1. Marginal feasibility is weaker than path feasibility

Let \(\mathcal X_t\) be the set of states that are individually admissible at
time \(t\), and let \(\mathcal T_t(x_{t-1})\) be the states reachable from
\(x_{t-1}\). A path must satisfy

\[
x_t\in\mathcal X_t\cap\mathcal T_t(x_{t-1}).
\]

Replacing this with the marginal statement

\[
x_t\in\mathcal X_t
\]

for each \(t\) removes temporal compatibility. This relaxation appears in many
forms:

- independent confidence regions at several dates;
- independent resource envelopes at several causal cuts;
- per-time physical feasibility without one dynamical trajectory;
- separately optimized counterfactual histories;
- benchmark scores that cannot all be attained by one policy;
- collections of local marginals without a compatible global joint law.

The mathematical error is always similar: existential quantifiers are moved
outside a conjunction.

The path statement is

\[
\exists (x_1,\ldots,x_T)
\quad
\forall t:
\Phi_t(x_{t-1},x_t).
\]

The marginal relaxation effectively checks

\[
\forall t\ \exists x_t:
\widetilde\Phi_t(x_t).
\]

Those logical forms are not equivalent.

## 2. Optionality is a state variable

A present state is not characterized only by its current payoff. It also
determines the set of future states that remain reachable.

For a feasible-state correspondence \(\mathcal R_t(x)\), define the continuation
value

\[
V_t(x)
=
\sup_{x_{t+1}\in\mathcal R_{t+1}(x)}
\left[r_{t+1}(x_{t+1})+V_{t+1}(x_{t+1})\right].
\]

Two states with equal immediate reward can have different continuation values
because they preserve different future options. Any compression that merges
those states is valid only when their entire future value functions agree for
every allowed continuation policy.

This is the dynamic analogue of predictive equivalence:

\[
x\sim_t y
\iff
\text{every admissible future decision/query protocol has the same law and value from }x\text{ and }y.
\]

Static sufficient statistics can therefore cease to be sufficient when a
movement budget, switching state, remaining horizon, or information pattern is
introduced.

## 3. Dual variables price constraints, not ontology

In the coupled LP, dual multipliers price event-level transition constraints.
A positive multiplier identifies a speed limit whose relaxation would improve
the declared objective locally.

This can reveal which distinctions matter operationally:

- which event probability is costly to move;
- which time step is the binding bottleneck;
- whether nonnegativity or transition geometry limits the path;
- where additional drift budget has marginal value.

But a shadow price is relative to the selected objective and units. It is not a
fundamental physical quantity. Changing the loss function can change the dual
support without changing the underlying feasible paths.

## 4. Reconfiguration creates hysteresis-like behavior

When changing representations costs \(\kappa\), the optimal action can depend on
which representation is currently active. Even if two codebooks have the same
current expected length, switching away and later switching back may be too
expensive.

This produces path dependence in the controller:

\[
\text{control state}
=(\text{belief or source state},\text{current codebook},\text{remaining horizon}).
\]

Such path dependence can resemble hysteresis, but the term should be used
carefully. Here it is a decision-theoretic consequence of switching costs, not
a claim about a thermodynamic material.

## 5. The order of moves defines the problem

Several distinct games are easily conflated:

1. **Open-loop commitment**: the encoder declares all codebooks, then the source
   path is selected.
2. **Causal feedback**: the encoder receives declared observations and then
   selects the next codebook.
3. **Seed-observing adversary**: the source sees realized random code choices.
4. **Oblivious adversary**: the source knows the policy but not independent
   future random seeds.
5. **Clairvoyant control**: the encoder directly observes the hidden current law.
6. **Learning control**: the encoder only sees samples generated from that law.

Their values can differ. A theorem for one order of moves cannot be transferred
to another merely because the same sets and costs appear.

## 6. Belief state is not always the whole state

Under a hidden Markov mode and conditionally independent observations, a
posterior belief can be sufficient for future prediction. With switching costs,
the current codebook must also be retained. With a nonrectangular uncertainty
set, one may additionally need the set of still-plausible models or an
adversarial commitment state.

A candidate dynamic sufficient state is therefore

\[
S_t=(\beta_t,c_{t-1},b_t,T-t),
\]

where:

- \(\beta_t\) is a posterior or robust belief object;
- \(c_{t-1}\) is the current codebook;
- \(b_t\) is any remaining movement, query, or intervention budget;
- \(T-t\) is remaining horizon.

Proving sufficiency requires showing that the conditional law of every future
observable and feasible action depends on history only through \(S_t\).

## 7. Dynamic consistency depends on rectangularity

A multistage ambiguity model is rectangular when conditional uncertainty can be
chosen independently at each history subject to local constraints. Rectangular
sets support Bellman recursion because nature's future choices can be separated
history by history.

A globally coupled ambiguity set can violate this property. Then a plan that is
optimal before observing history may no longer be optimal when re-solved later,
because the earlier optimization encoded commitments about how uncertainty is
correlated across histories.

The current TV path set is coupled across time but is represented directly as
one finite path polytope for open-loop optimization. Before introducing adaptive
policies, the project must state whether nature commits to a full model/path,
chooses transitions online, or uses a rectangular set of kernels.

## 8. The abstraction beyond coding

The same machinery applies whenever:

- the hidden or uncertain environment moves under a metric constraint;
- an agent selects a time-varying representation or action;
- current movement affects future reachability;
- changing the agent's representation has a cost.

Examples include cache placement, model routing, sensor scheduling, dynamic
quantization, distributed replicas, adaptive experiment design, and approximate
rendering policies. The specific code-length results do not transfer
unchanged, but the separation of path geometry, information pattern, action
sequence, and switching cost does.

## 9. Relevance to restricted simulation hypotheses

A restricted renderer architecture may claim that only the currently observed
region or queried variables need to be maintained. The dynamic analysis asks a
stronger question:

> Does the retained state preserve every future world law that remains jointly
> reachable under all allowed interventions and cross-checks?

Independent local consistency at each time is insufficient if no single hidden
history can connect those local snapshots. Conversely, a renderer need not
store arbitrary detail that has no effect on the reachable distribution of any
future allowed transcript.

This points to a dynamic predictive quotient: histories should be merged only
when they induce the same set or law of future reachable transcripts under the
declared intervention policy.

## 10. Next exact target

The next bounded theorem program should use a finite hidden-mode model with:

- rational prior over modes;
- rational mode-dependent categorical source laws;
- a rational observation channel;
- a finite zero-error codebook action set;
- rational switching and observation costs;
- finite horizon;
- exact posterior updates.

It should compute and compare:

\[
V_{\mathrm{open}},
\qquad
V_{\mathrm{causal}},
\qquad
V_{\mathrm{clairvoyant}}.
\]

The differences

\[
V_{\mathrm{open}}-V_{\mathrm{causal}}
\]

and

\[
V_{\mathrm{causal}}-V_{\mathrm{clairvoyant}}
\]

would separate the value of the declared observation channel from the remaining
value of hidden information. Exact policy trees and posterior receipts should
be returned, and any policy-tree cap must fail closed.
