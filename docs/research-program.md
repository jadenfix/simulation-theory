# Research Program

## Goal

Turn simulation-theory discussion into explicit mathematical models whose assumptions, observable implications, and failure modes can be checked independently.

The project is not trying to assign a dramatic single-number probability to “simulation.” It is building a hierarchy of restricted questions:

1. Is the model identifiable from internal observations?
2. What observer measure converts world populations into credences?
3. What computational or physical constraints follow from the specified architecture?
4. What experiment distinguishes that architecture from serious alternatives?
5. What exact evidence remains after selection, intervention, and optional stopping are modeled?

## Completed mathematical lanes

### Identification before estimation

- Generic simulator classes containing the base observable law are underidentified.
- Bounded likelihood ratios impose exact Bayesian evidence ceilings.
- Total variation, Le Cam, and Fano quantify finite two-model and multi-model limits.
- Hierarchical Bayesian scenarios preserve technical-feasibility uncertainty instead of hiding it inside an expected observer count.

### Observer measure

- Civilization and observer factors remain separate instead of collapsing into one count.
- The Jensen gap prevents plug-in expected counts from masquerading as model-averaged probabilities.
- Finite SSA/SIA/FNC-presence conventions expose duplication and saturation behavior.

### Adaptive consistency and rendering

- Exact conditional lazy generation is transcript-equivalent to full pre-generation.
- Per-step total-variation and conditional-KL errors now have transcript-level bounds.
- Exact and approximate predictive-state lower bounds are implemented.

### Causal selection

- Outcome-dependent retention has an exact log-odds sensitivity identity.
- Arbitrary finite reweighting is constructively demonstrated.
- Unrestricted latent interventions have explicit minimum mixture mass.

### Sequential inference

- Fixed and mixture Bernoulli e-processes are implemented in log space.
- Simple and one-sided composite-null validity is proved.
- Finite-horizon optional-stopping error is audited by exact dynamic programming.

### Physics and representation

- Local Landauer, Margolus-Levitin, Bekenstein, mass-energy, and Schwarzschild expressions are implemented with explicit SI inputs.
- Cross-level cost remains an input assumption rather than an inferred consequence.
- Program multiplicity and Kraft diagnostics expose coding-language sensitivity.

## Next research campaigns

### Campaign A: physically meaningful predictive-state lower bounds

The present packing theorem accepts an arbitrary finite family of future laws. The next step is to derive those families from explicit physical experiments.

Candidate bounded programs:

- finite Bell-type measurement schedules with adaptive basis selection;
- reversible cellular-automaton or lattice-field toy worlds with delayed measurements;
- distributed observers comparing authenticated historical records;
- finite quantum-circuit families where future outcome laws depend on hidden stabilizer or phase state;
- relativistic causal networks where spacelike-separated query choices constrain transcript consistency.

Deliverables:

1. A typed finite experiment definition.
2. Exact future-law enumeration or certified approximation.
3. Packing/covering numbers as a function of error tolerance.
4. State, random-bit, and update-time lower bounds with bounded claim scope.

### Campaign B: restricted physical signatures

Select one architecture at a time—lattice, finite precision, constrained pseudorandomness, or approximation policy. For each:

1. State the null and alternative observable laws.
2. Identify nuisance parameters and ordinary-physics alternatives.
3. Build a leakage-safe data pipeline.
4. Pre-register a likelihood, e-process, or confidence sequence.
5. Report power and calibration before interpreting data.

No “anomaly score” is evidence without a null sampling model.

### Campaign C: causal simulator-policy models

Build structural causal models with nodes for:

- internal physical state;
- external intervention;
- retention/continuation;
- observer existence;
- measurement choice;
- recorded observation.

Research targets:

- graphical sufficient conditions for recoverability;
- sensitivity regions when retention odds ratios are bounded;
- negative identifiability results when policy is unrestricted;
- multi-environment designs that can separate law change from selection.

### Campaign D: observer-measure robustness

Replace one toy scalar count with explicit distributions over:

- civilization survival and capability;
- deployment and ethical prohibition;
- simulation multiplicity;
- observer lifetime and observer moments;
- consciousness uncertainty;
- full-evidence rarity;
- duplicate dependence and copy correlations.

Compute posterior surfaces under several conditioning rules, robust prior sets, and dependence structures. Keep the output as a sensitivity map rather than a single unsupported percentage.

### Campaign E: algorithmic-prior sensitivity

The next algorithmic lane should compare:

- alternative prefix languages;
- compiler-equivalent implementations;
- observational-law aggregation;
- shortest-description and aggregate-program semimeasures;
- finite universal-machine perturbations.

The target is not a representation-free prior—which may be impossible—but a quantitative account of how conclusions move under admissible coding choices.

## Quality gates

A research result is ready for the main branch only when:

1. The claim has an explicit finite, universal, asymptotic, or empirical scope.
2. Assumptions and nonclaims are written next to the result.
3. The derivation has a test, exact checker, or independently reproducible calculation where applicable.
4. Numerical demonstrations use fixed seeds and are labeled illustrative when priors are invented.
5. Sequential claims state their sampling model and stopping guarantee.
6. Physical claims state which laws apply and avoid cross-level leakage.
7. A finite experiment is never promoted into a generic simulation conclusion.

## Tempera Math integration

The repository's claim manifest is the source of truth. Tempera Math can later provide content-addressed claim registration, proof graphs, exact finite certificates, and external checker receipts. The adapter must preserve:

- theorem versus model-result versus finite-check status;
- all assumptions and nonclaims;
- exact source revision and checker command;
- the boundary between structural validation and mathematical execution.

See [`tempera-math-bridge.md`](tempera-math-bridge.md).

## Nonclaims

This project does not claim that quantum mechanics, Planck scales, cosmic-ray cutoffs, entropy bounds, mathematical elegance, coincidences, observer effects, or finite signal speed are evidence of simulation by themselves. It does not assume digital physics, substrate-independent consciousness, finite parent resources, or a parent universe obeying our constants.

Rejecting one restricted implementation does not reject every possible simulator. Finding an anomaly does not favor simulation until the anomaly is more likely under a specified simulator model than under serious ordinary-physics and measurement alternatives.
