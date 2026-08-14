# Formal Results

This document separates theorem, model assumption, finite computation, and open problem. Every probability below concerns an **observable law available to an internal investigator**. No theorem assumes that a simulator exists.

## Unrestricted indistinguishability

Let `(X,F)` be the observable measurable space, let `P_B` be a base-model law, and let the simulator class contain a member `S*` whose induced observable law is exactly `P_B`.

A randomized test is a measurable `phi:X->[0,1]`. Since `P_S*=P_B`,

```text
E_S*[phi] = integral phi dP_S* = integral phi dP_B = E_B[phi].
```

Therefore a level-`alpha` test has power at most `alpha` against `S*`. No test can uniformly distinguish the unrestricted simulator class from base reality when the class contains an observationally identical member.

For Bayesian comparison,

```text
BF_S*:B(x) = p(x|S*) / p(x|B) = 1
```

whenever the ratio is defined. Posterior odds equal prior odds.

**Boundary.** This proves underidentification of the generic class, not untestability of restricted architectures.

## Evidence ceiling and robust posterior bounds

Suppose `P_S` and `P_B` are mutually absolutely continuous and

```text
exp(-epsilon) <= dP_S/dP_B <= exp(epsilon)
```

almost surely. Bayes' rule gives

```text
posterior_odds = prior_odds * dP_S/dP_B.
```

Taking logarithms,

```text
|log posterior_odds - log prior_odds| <= epsilon.
```

Near-observational equivalence therefore imposes a hard ceiling on evidence.

If the prior belongs to `[pi_low,pi_high]` and the Bayes factor belongs to `[b_low,b_high]`, posterior probability is monotone in both quantities, so the sharp rectangular uncertainty interval is obtained at the two corners:

```text
[ posterior(pi_low,b_low), posterior(pi_high,b_high) ].
```

The code implements both results in `simtheory.inference`.

## Total variation and two-point minimax limits

For finite laws `P,Q`,

```text
TV(P,Q) = 1/2 sum_x |P(x)-Q(x)|.
```

Every randomized test satisfies

```text
|E_P[phi]-E_Q[phi]| <= TV(P,Q).
```

With equal priors, the optimal model-classification accuracy is

```text
A* = (1 + TV(P,Q))/2.
```

Consequently, if `TV=0.01`, no classifier using that observation space can exceed `50.5%` equal-prior accuracy.

For two parameter values separated by distance `Delta`, any estimator under absolute loss has worst-case risk at least

```text
Delta * (1-TV(P,Q)) / 4.
```

Proof: convert the estimator into a nearest-parameter classifier. On a classification error, absolute estimation loss is at least `Delta/2`; the optimal equal-prior classification error is `(1-TV)/2`.

## Observer measure and the Jensen gap

A simulated-observer measure can be factored as

```text
M_S = sum_i r_i d_i s_i n_i c_i q_i tau_i,
```

where the factors may represent capability, deployment, simulation count, observer measure, consciousness weight, compatibility with the investigator's full evidence, and observer-moment weighting.

This is bookkeeping. It does not prove that the chosen measure is correct.

Let fixed base measure be `B>0` and uncertain simulated measure be `X>=0`. Under this convention,

```text
f(X) = X/(B+X).
```

Since

```text
f''(x) = -2B/(B+x)^3 < 0,
```

Jensen's inequality yields

```text
E[X/(B+X)] <= E[X]/(B+E[X]).
```

The inequality is strict for nondegenerate `X` with finite expectation. Plugging an expected observer count into the ratio therefore overstates the model-averaged fraction.

## Hierarchical Bayesian model uncertainty

Let scenario index `Z` encode explicit branches such as technical infeasibility, technical feasibility with low deployment, or feasibility with large simulated measure. Each scenario has prior `pi_z`, ordinary data likelihood `L_z`, base measure `B_z`, and simulated measure `S_z`.

The posterior scenario weight is

```text
w_z = pi_z L_z / sum_j pi_j L_j.
```

Under the declared observer-measure convention, the posterior probability of being simulated is

```text
P(simulated | data) = sum_z w_z S_z/(B_z+S_z).
```

This is an **average of scenario-conditional ratios**. In general it is not equal to

```text
[sum_z w_z S_z] / [sum_z w_z(B_z+S_z)].
```

The distinction is another nonlinear model-averaging boundary. In particular, if a scenario in which relevant simulations are impossible retains substantial posterior mass, an arbitrarily large simulated population in the feasible branch does not erase that model uncertainty: with matched data likelihoods and feasible-branch ratio tending to infinity, the posterior simulated probability tends to the posterior probability of the feasible branch, not automatically to one.

The repository implements this decomposition in `simtheory.bayesian`. It is a generic hierarchical model, not a reproduction of one uniquely correct anthropic prior.

## Finite anthropic-conditioning divergence

For world `i`, write prior `pi_i`, total relevant observer count `N_i`, matching count `M_i`, and full-evidence-presence probability `F_i`.

Three explicit finite rules in the repository are

```text
SSA-style weight: pi_i * M_i/N_i
SIA-style weight: pi_i * M_i
FNC-presence-style weight: pi_i * F_i.
```

They are normalized across worlds after weighting.

If one world's counts are duplicated by factor `k>0` while its matching fraction remains fixed:

```text
(k M_i)/(k N_i) = M_i/N_i,
```

so its unnormalized SSA-style weight is unchanged. Its SIA-style weight is multiplied by `k`.

Under a Poisson copy model with expected matching count `lambda_i`,

```text
F_i = 1-exp(-lambda_i).
```

After duplication, `F_i(k)=1-exp(-k lambda_i)`, which increases but saturates at one. Thus the three rules have qualitatively different duplication behavior.

**Boundary.** These are finite model conventions, not a resolution of the philosophical SSA/SIA/FNC dispute.

## Selection-policy reweighting

Let `Q(x)` be a raw generated-history law and `w(x) in [0,1]` the probability that history `x` is retained, continued, sampled, or otherwise appears in the investigator's data. Conditioning on retention gives

```text
Q_retained(x) = Q(x) w(x) / E_Q[w(X)].
```

For any target `P` absolutely continuous with respect to `Q`, choose

```text
C >= sup_x P(x)/Q(x),
w(x) = P(x)/(C Q(x)).
```

Then `w(x)<=1` and normalization gives `Q_retained=P`. An unrestricted observation-dependent retention policy can therefore reproduce any target law supported by the raw law.

This is an identifiability warning, not a claim that any real simulator uses such a policy.

## Resource-bounded nesting

Let `B_0` be a parent level's budget in a resource relevant to the chosen observer measure. Suppose all children of level `k` receive aggregate budget at most `rho B_k`, where `0<=rho<1`. Then

```text
B_k <= B_0 rho^k
```

and

```text
sum_{k>=1} B_k <= B_0 rho/(1-rho).
```

Recursive depth alone does not imply infinite simulated observer measure. Divergence requires failure of contraction, a different cross-level measure, or an assumption of effectively unbounded compression.

## Exact lazy-rendering equivalence

Consider an adaptive query policy. A full generator samples a hidden world and answers all queries from it. A lazy generator samples answer `A_t` from the exact target conditional law given the full prior transcript `H_t` and current query `Q_t`:

```text
P(A_t | H_t,Q_t).
```

By the probability chain rule, both induce

```text
P(A_1,...,A_T | policy)
  = product_t P(A_t | H_t,Q_t).
```

Therefore exact conditional lazy generation and full pre-generation have the same finite observable transcript law. “Rendering on demand” is not itself a detectable signature.

The scientific question is the memory and computation required to represent and sample the relevant conditionals.

## Adaptive approximate-rendering transcript bound

Suppose target and approximate renderer transcript prefixes are coupled. Conditional on their prefixes agreeing through time `t-1`, assume the next-answer laws have

```text
TV(P_t(.|H_t), Q_t(.|H_t)) <= epsilon_t.
```

At every matched prefix, choose a maximal coupling. The probability of matching at step `t`, conditional on all previous matches, is at least `1-epsilon_t`. Hence

```text
P(all T answers match) >= product_t (1-epsilon_t).
```

The coupling inequality gives

```text
TV(P_transcript,Q_transcript)
  <= P(transcripts differ)
  <= 1 - product_t (1-epsilon_t)
  <= min(1, sum_t epsilon_t).
```

This remains valid for adaptive queries because a deterministic policy selects the same next query whenever coupled prefixes match. Randomized policies can include their shared random seed in the coupling.

## Conditional KL accumulation

For absolutely continuous transcript laws, the KL chain rule gives

```text
KL(P_1:T || Q_1:T)
 = sum_t E_P[ KL(P_t(.|H_t) || Q_t(.|H_t)) ].
```

If the expected conditional terms are bounded by `kappa_t`, then

```text
KL(P_1:T || Q_1:T) <= sum_t kappa_t.
```

Pinsker's inequality gives

```text
TV(P_1:T,Q_1:T) <= sqrt( (sum_t kappa_t)/2 ).
```

No independence assumption is needed. The correctness of the conditional models and absolute-continuity assumptions remains external.

## Exact predictive-state lower bound

Two histories are predictively equivalent when every admissible future query strategy induces the same future observable law after either history.

Suppose an exact online renderer's future behavior depends only on its internal state. If two histories map to one state, they induce the same future law. Therefore histories with different future laws require different states.

With `K` predictive-equivalence classes, the renderer requires at least `K` states and at least

```text
ceil(log2 K)
```

bits merely to identify the class.

## Approximate predictive-state packing

Suppose one renderer state emits approximation `R_s`, and every target future law `P_h` assigned to that state satisfies

```text
TV(P_h,R_s) <= epsilon.
```

If two histories `h,g` share the state, the triangle inequality gives

```text
TV(P_h,P_g) <= TV(P_h,R_s)+TV(R_s,P_g) <= 2 epsilon.
```

Therefore every family of target future laws separated pairwise by more than `2 epsilon` requires distinct renderer states. The maximum size of such a separated subset—the `2 epsilon` packing number—is a state-count lower bound.

The repository computes the exact packing number for finite studies as a maximum-clique problem, capped at 60 laws. A bounded packing computation is not an asymptotic physical theorem.

## Multi-architecture Fano bound

Let model index `Theta` be uniform over `M>=2` restricted observable laws `P_1,...,P_M`. For any architecture identifier `hat Theta`, Fano's inequality gives

```text
P(hat Theta != Theta)
  >= 1 - ( I(Theta;X) + log 2 ) / log M.
```

For one observation,

```text
I(Theta;X) = (1/M) sum_i KL(P_i || P_bar),
P_bar = (1/M) sum_i P_i.
```

For conditionally IID observations,

```text
I(Theta;X_1:n) <= n I(Theta;X_1),
```

which yields a computable, potentially loose sample-size lower bound. If all candidate observable laws are identical, `I=0` and no number of such observations identifies the architecture.

## Selection and intervention identifiability

### Binary retention identity

Let raw anomaly probability be `p`, retention probabilities be `r_1` after an anomaly and `r_0` after no anomaly. The retained anomaly probability is

```text
q = p r_1 / (p r_1 + (1-p) r_0).
```

Therefore

```text
q/(1-q) = [p/(1-p)] [r_1/r_0]
```

and

```text
logit(q) = logit(p) + log(r_1/r_0).
```

If `1/Gamma <= r_1/r_0 <= Gamma`, the sharp raw-probability interval is

```text
logistic(logit(q)-log Gamma)
  <= p <=
logistic(logit(q)+log Gamma).
```

### Latent intervention mixture

Let baseline anomaly probability be `b`, intervention law probability be `u`, and intervention rate be `pi`:

```text
q = (1-pi)b + pi u,
0 <= u <= 1.
```

The minimum unrestricted intervention rate compatible with `q` is

```text
(q-b)/(1-b), if q>b,
(b-q)/b,     if q<b,
0,           if q=b.
```

The extremizing intervention has `u=1` for upward shifts and `u=0` for downward shifts. Without restrictions on intervention law or rate, altered internal physics and external intervention are not separately identified from one marginal anomaly rate.

## Anytime-valid restricted-signature tests

Let `X_t` be IID Bernoulli with null boundary `p_0` and fixed alternative `p_1`. Define

```text
E_t = product_{i<=t}
      (p_1/p_0)^{X_i}
      ((1-p_1)/(1-p_0))^{1-X_i}.
```

Under the simple null `p=p_0`, `E_t` is a nonnegative martingale with expectation one.

For an upper-tail null `p<=p_0` and `p_1>p_0`, the one-step conditional multiplier has expectation

```text
1 + (p-p_0)(p_1-p_0)/(p_0(1-p_0)) <= 1.
```

Thus `E_t` is a nonnegative supermartingale for the composite null. The lower-tail case is symmetric.

Ville's inequality gives

```text
P_null( sup_t E_t >= 1/alpha ) <= alpha.
```

Convex mixtures of valid e-processes are valid e-processes. The repository exactly dynamic-programs finite-horizon crossing probabilities to audit the implementation.

**Boundary.** Validity requires the declared sampling model. A hand-designed “glitch” indicator is not generic simulation evidence.

## Algorithmic representation multiplicity

For binary prefix-program lengths `ell(p)`, Kraft admissibility requires

```text
sum_p 2^{-ell(p)} <= 1.
```

If multiple programs implement the same observable law `L`, raw aggregate program mass is

```text
m(L) = sum_{p:P_p=L} 2^{-ell(p)}.
```

This may be a legitimate semimeasure under a fixed universal machine, but it depends on the coding language and the number/length of alternative implementations. Treating each implementation as a separate observable world can obscure this dependence. The repository reports both aggregate mass and shortest-description diagnostics; it does not claim a unique representation-independent algorithmic prior.

## Local physics versus parent physics

The code evaluates the following local-physics expressions:

```text
Landauer erasure energy:       E >= n k_B T ln 2
Margolus-Levitin rate:         rate <= 2E/(pi hbar)
Bekenstein information form:  bits <= 2 pi E R/(hbar c ln 2)
Mass-energy:                   E = m c^2
Schwarzschild radius:          r_s = 2 G m/c^2.
```

These formulas constrain systems satisfying the assumptions under which they were derived. They can bound simulators constructed in our universe when their local energy, temperature, size, and implementation are specified.

They do **not** imply a parent-substrate cost from internal simulated mass. Formally, let implementation map `I` send internal states to parent states and let `C` be parent cost. Internal semantics alone imposes no monotonic relation between internal mass `m` and `C(I(m))`. A transfer bound requires an additional assumption such as

```text
C(I(m)) >= a m
```

for an externally justified `a>0`. The code makes this coefficient an explicit input rather than inferring it.

## Current open problems

The proof-complete results above do not establish whether reality is simulated. The highest-value open targets are:

1. Predictive-state and sampling lower bounds for physically meaningful quantum and relativistic adaptive-query families.
2. Approximate-rendering lower bounds that combine memory, update time, randomness, and communication rather than state count alone.
3. Identifiability conditions when simulator intervention and retention policies are restricted by causal structure.
4. Sequential tests tied to concrete lattice, precision, or random-source architectures and real external data.
5. Robust observer-measure analysis under uncertain consciousness, reference-class, and copy-generation models.
6. Algorithmic priors with an explicit universal-machine sensitivity analysis and observational-law aggregation.
