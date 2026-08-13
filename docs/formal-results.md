# Formal Results

This note separates proved mathematical statements from model assumptions.

## Unrestricted indistinguishability

Let `P_B` be the observable law of a base model. If a simulator class contains `S*` with `P_S*=P_B`, then for every randomized test `phi:X->[0,1]`,

`E_S*[phi]=E_B[phi]`.

So a level-alpha test has power at most alpha against that matched member. The corresponding Bayes factor is exactly one. Generic simulation is therefore statistically underidentified until the simulator class is restricted.

## Evidence ceiling

If `exp(-eps) <= dP_S/dP_B <= exp(eps)`, Bayes' rule gives

`|log posterior_odds - log prior_odds| <= eps`.

Near observational equivalence limits how much any observation can move belief.

## Total variation ceiling

For simple observable laws `P,Q`, every test obeys

`|E_P[phi]-E_Q[phi]| <= TV(P,Q)`.

With equal priors, optimal classification accuracy is `(1+TV(P,Q))/2`. Better algorithms cannot recover information absent from the observation law.

## Observer-measure factorization

A population count is not a probability until an observer measure is chosen. A useful factorization is

`M_S=sum_i r_i d_i s_i n_i c_i q_i tau_i`,

where factors encode survival/capability, deployment, simulation count, observer measure, consciousness weight, evidence compatibility, and observer-moment weighting. The familiar `M_S/(M_S+M_B)` follows only after this measure convention is adopted.

## Jensen expectation trap

With `M_B=1` and uncertain `X=M_S`, define `f(x)=x/(1+x)`. Since `f''(x)<0`,

`E[X/(1+X)] <= E[X]/(1+E[X])`.

Thus plugging an expected simulated count into the ratio generally overstates the model-averaged fraction.

## Selection-policy confounding

If `Q(x)` is a raw history law and `w(x)` is the probability a history is retained or continued, observers condition on

`Q_retained(x)=Q(x)w(x)/E_Q[w(X)]`.

Observed anomaly rates therefore depend on selection policy as well as raw generation.

## Resource-bounded nesting

If each descendant level receives at most fraction `rho<1` of its parent's relevant budget, then

`sum_{k>=1} B_k <= B_0 rho/(1-rho)`.

Infinite nesting alone does not imply infinite simulated observer measure.

## Parent-resource non-transfer

Internal mass, energy, or information variables do not automatically lower-bound parent-substrate resources. Such a bound requires an implementation map or law-transfer assumption. Physical computation bounds derived under our physics therefore cannot be projected to an unknown parent reality for free.

## Exact lazy-rendering equivalence

A full generator samples a hidden world and answers adaptive queries from it. A lazy generator instead samples each next answer from the exact target conditional law given the full query/answer history. By the chain rule, both induce the same finite transcript distribution. Exact lazy generation is therefore not itself detectable.

The meaningful question is computational: how hard is it to maintain and sample the required conditional law?

## Predictive-state lower bound

Two histories are predictively equivalent if all admissible future queries have identical conditional laws after them. If an exact renderer's future behavior depends only on internal state, histories with different future laws cannot share that state. With `K` predictive-equivalence classes, an exact state representation requires at least `K` states and at least `ceil(log2 K)` bits to identify the class.

## Program multiplicity

Many programs can implement the same observable law. Raw program counting can therefore create representation-dependent prior mass. Algorithmic-prior arguments must state their coding/universal-machine convention or aggregate at an observational-equivalence level.

## Open mathematical targets

The next targets are minimax lower bounds for approximate rendering, SSA/SIA/FNC-style measure comparisons, sequential tests for restricted physical signatures, latent-intervention identifiability, and information/computation lower bounds for reproducing specified quantum or relativistic correlation families.
