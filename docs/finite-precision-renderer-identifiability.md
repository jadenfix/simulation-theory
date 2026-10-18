# Finite-precision renderers: the dithering boundary, visibility-blind non-identifiability, and a Diophantine separation

Claims ST-T286 to ST-T289, ST-F57 and ST-O04
([manifest](../claims/finite-precision-renderer-claims.json)). Certificate:
`src/simtheory/finite_precision_renderers.py`, receipt
[`receipts/finite-precision-renderer-identifiability.txt`](../receipts/finite-precision-renderer-identifiability.txt),
tests in `tests/test_finite_precision_renderer_identifiability.py`.

Status: Theorems 0 to 3 are proved below; the binary-digit constants are a
finite check; three questions are recorded as open problems. One clause of the
original direction sketch is false and is recorded as a negative result
(Section 3.3). Section 6 is a remark and is not registered as a claim.

## 0. Summary

"The universe computes outcome probabilities to finite precision" is a
frequently proposed simulation artifact (compare Buniy, Hsu and Zee, Phys. Lett.
B 630 (2005) 68-72; Palmer, Proc. R. Soc. A 476 (2020) 20190350; and the
related lattice proposal of Beane, Davoudi and Savage, Eur. Phys. J. A 50
(2014) 148). Under a declared Bell model, with the precision D declared in
advance and the setting cosines known exactly, it gives the following map:

| regime | answer | rate |
|---|---|---|
| renderer may dither with unrestricted private randomness | untestable: every law is realized exactly, BF = 1 | none |
| unknown visibility, all setting cosines commensurable (includes canonical CHSH), for every D divisible by 4 with c(v_max - v_min) >= 4b/D (single cosine: for even D iff [c v_min, c v_max] meets L_D; see Section 3.3 for D below the threshold) | unidentifiable: H_D meets the Werner family exactly, BF = 1 at the meeting point | none |
| unknown visibility, two settings with quadratic-irrational cosine ratio | identifiable | separation Omega(1/D^2), trials O(D^4 log(1/eps)) |
| same, cosines in {0, +-1, +-1/sqrt2}, 4 \| D and D >= 4/(v_max - v_min), designs restricted to those cosines | identifiable | separation Theta(1/D^2), trials Theta(D^4 log(1/eps)) |
| visibility known exactly (v = 1) | identifiable | trials Theta(D log(1/eps)) with a D-adapted angle; for the fixed angle pi/4 between 4^k and 4^{k(1+e)}, governed by the binary digits of sqrt2 |

A universal converse (Theorem 3a) shows that no fixed-horizon design over any
angles, adaptive or not, can beat (D-1)/2 ln(1/(4 eps)) trials. For a 53-bit
fixed-point grid (D = 2^53, used only as an illustration; IEEE double precision
is not a uniform grid and is not modelled) any design needs at least about
7.2 x 10^15 trials (eps = 0.05), and the adapted design suffices with about
5.9 x 10^17. With the {0, pi/4} schedule (cosines in {0, +-1, +-1/sqrt2}) and v in
[1/2, 1], the count lies between about 3.2 x 10^58 trials (necessary for such
designs) and about 7.8 x 10^66 per setting (sufficient). With free angle choice
only Omega(D log(1/eps)), about 7 x 10^15, is proved.

## 1. Declared model

**Settings and base law.** A trial uses a setting pair s from a declared set S
with angle difference theta_s and c_s := cos(theta_s). Outcomes (a, b) lie in
{+1, -1}^2, ordered (++, +-, -+, --). The base (Werner/singlet, ST-T09) family
is

```text
P_v(a, b | s) = (1 - a b v c_s) / 4,     v in V = [v_min, v_max],  0 <= v_min < v_max <= 1.
```

Write x = v c_s and tau_s := -E[AB | s]. Under P_v, tau_s = v c_s. Visibility v
is a nuisance parameter unless stated otherwise. **The setting cosines c_s are
known exactly** under both hypotheses; Section 8 records how a cosine
calibration uncertainty voids the identifiability results.

**Design.** Settings are chosen by a rule (fixed counts, i.i.d. weights w_s, or
adaptive on past data and public randomness) that is the same under every
compared hypothesis. This is the repository's standing convention (ST-T09,
ST-T10).

**Restricted hypothesis H_D (stationary finite precision).** The precision D is
declared in advance. Trials are conditionally independent given the settings,
and for every s there is one fixed law q_s on {+1,-1}^2 with every q_s(a, b) in
(1/D)Z. Here q_s is the effective per-trial law after all renderer-internal
randomness is marginalized. Nothing else is assumed: q_s need not be
Werner-shaped or have uniform marginals. Write tau_s(Q) = m_s / D. Since
tau = (D - 2 n_+) / D with n_+ = D (q(++) + q(--)), m_s is an integer with
|m_s| <= D and m_s = D (mod 2).

**Dithered hypothesis.** A renderer holds a table of D-grid laws q_{s,j} and,
on every trial, draws a fresh private index J ~ lambda_s, independent of
everything else. Its effective law is sum_j lambda_{s,j} q_{s,j}.

Notation: TV is half the l1 distance, BC(p, q) = sum sqrt(p_i q_i),
H^2 = sum (sqrt p_i - sqrt q_i)^2 = 2 - 2 BC, and ||y|| is the distance from y
to the nearest integer.

### Lemma A (optimal grid rounding)

For any law p on K points and any D >= 1, min over D-grid laws q of
||q - p||_1 is attained by largest-remainder rounding: write D p_i = n_i + f_i
with n_i integer and f_i in [0, 1), let r = sum f_i (an integer), and round up
the r coordinates with the largest f_i. The minimum is at most
2 r (K - r) / (K D) <= K / (2D).

*Proof.* We minimize sum phi_i(k_i), with phi_i(k) = |k - D p_i| convex, over
integers k_i >= 0 with sum k_i = D. Suppose k_i > ceil(D p_i). Since
sum k = sum D p, some j has k_j < D p_j. Moving one unit from i to j lowers
phi_i by 1 and raises phi_j by at most 1 - 2 f_j <= 1, or lowers it by 1 when
k_j + 1 <= D p_j. The total does not increase. The case k_i < floor(D p_i) is
symmetric. So we may take k_i in {n_i, n_i + 1} with exactly r round-ups, and
the cost is sum_i f_i + sum_{up} (1 - 2 f_i), which is minimized by the r
largest f_i. For the bound, the K - r smallest f's sum to at most
(K - r) r / K, and sum over the r largest of (1 - f) is at most r - r^2 / K.
QED.

This is the standard l1 optimality of largest-remainder (Hamilton)
apportionment (Balinski and Young, Fair Representation, Yale University Press
1982); optimal M-type approximation of a distribution is also treated by
Boecherer and Geiger, "Optimal quantization for distribution synthesis",
arXiv:1307.6843. The proof is kept for self-containment.

## 2. Theorem 0 (dithering boundary)

**(a) Unrestricted private randomness.** For every law p on {+1,-1}^2 and every
D >= 1, there are at most 4 D-grid laws q^(1..4) and probability weights
lambda_j >= 0 with sum_j lambda_j = 1 and sum lambda_j q^(j) = p, and
||q^(j) - p||_inf < 1/D for each j. Consequently, if the dithering weights are
unrestricted, then for every v and every design there is a dithered D-renderer
whose transcript law equals the law under P_v exactly, for every number of
trials. For that pair BF_sim:base = 1 by ST-T01. In this regime finite precision
is not testable at all.

Existence alone is immediate, since point masses are D-grid laws for every D;
the content is locality (every component within 1/D of p).

**(b) Finite-precision private randomness.** If every lambda_{s,j} lies in
(1/M)Z, the set of effective laws is exactly H_{DM}. Precision is therefore a
property of the pair (probability table, private randomness), and only the
product DM is observable.

*Proof of (a)* (systematic dithering). Let D p = n + f as in Lemma A, with
r = sum f_i. Partition [0, r) into consecutive intervals I_i of lengths f_i. For
U uniform on [0, 1), let S(U) be the set of i whose interval contains one of
U, U + 1, ..., U + r - 1. Every point lies in exactly one interval, and an
interval of length < 1 contains at most one point, so |S(U)| = r and
q_{S(U)} := (n + 1_{S(U)}) / D is a D-grid law. Also P(i in S(U)) = f_i, so
E[q_{S(U)}] = p. The map U -> S(U) is piecewise constant, with breakpoints at
the fractional parts of the interval endpoints, so there are at most K = 4
distinct components and their weights are the lengths of the pieces. Finally
|q_{S,i} - p_i| = |1_S(i) - f_i| / D < 1/D. Because the index is drawn fresh and
independently on each trial, the transcript is i.i.d. with per-trial law p,
which is identical to the base model's. QED.

The construction is Madow's systematic sampling with unequal probabilities
(Ann. Math. Statist. 20 (1949) 333-354), equivalently dependent rounding; it is
standard and not claimed as new.

*Proof of (b).* If lambda_j = a_j / M and q^(j) in (1/D)Z^4, then
sum lambda_j q^(j) lies in (1/(DM))Z^4. Conversely, a DM-grid law with integer
count vector m (sum m = DM) splits into M nonnegative integer vectors each
summing to D: list the DM units and cut the list into M blocks of D. The uniform
average of the M resulting D-grid laws is the target. QED.

**Boundary remarks.** (i) Reusing one draw of J for all trials gives an
exchangeable, non-i.i.d. transcript, which is a different model. (ii) A
deterministic, time-varying sequence of grid laws with no private randomness
is also not equivalent; with D = 1, for example, every outcome is
deterministic. Deterministic time-varying schedules such as sigma-delta or
error-diffusion rendering may nevertheless be statistically very close to the
base law; no detectability is claimed for them. Testing finite precision
therefore requires declaring the stationarity (no-dithering) restriction H_D,
or a bound M on private randomness, which by (b) reduces to H_{DM}.

**Finite check.** Exact Fraction decompositions for five rational targets,
including D = 1024 and the Pell target x = 99/140. Exact set equality
avg_M(H_D) = H_{DM} for (K, D, M) in {(3,2,3), (3,3,2), (4,2,2), (2,5,3)}.

## 3. Theorem 1 (visibility-blind schedules are non-identifying)

### 3.1 Werner lattice

P_x is a D-grid law if and only if D is even and x lies in
L_D := {(4j - D)/D : j = 0, ..., D/2}. In particular, for odd D no Werner law
is a D-grid law.

*Proof.* The law has two entries equal to (1 - x)/4 and two equal to
(1 + x)/4. If D(1 - x)/4 = k and D(1 + x)/4 = l are integers, then 2k + 2l = D,
so D is even and x = (4l - D)/D. The converse is immediate. QED. (Exact brute
force agrees for D = 1..40.)

### 3.2 Theorem 1 (commensurable schedules)

Suppose every setting cosine is a rational multiple of one number:
c_s = (a_s / b) c with integers a_s, a common b >= 1, c > 0, and |c_s| <= 1. Let
D be divisible by 4. Then P_v lies in H_D whenever v c lies in (4b/D)Z. Such a v
exists in V whenever c (v_max - v_min) >= 4b / D. For any such v* the
stationary renderer Q := P_{v*} lies in H_D, and its transcript law equals the
base law at v* for every design and every n. Hence H_D and the Werner family W
are not disjoint. Every level-alpha test of the composite W has power at most
alpha at Q, and the point Bayes factor BF_{Q : P_{v*}} = 1 (ST-T01).

*Proof.* With v c = 4 b m / D, x_s = v c_s = 4 a_s m / D lies in (4/D)Z. Since
4 | D, (4/D)Z intersected with [-1, 1] equals L_D, and |x_s| <= 1, so every
setting law is a D-grid law by 3.1. An interval of length
c (v_max - v_min) >= 4b/D contains a point of (4b/D)Z. QED. (An earlier version
assumed 4b | D; only 4 | D is needed.)

For odd D, or D below the threshold, H_D and W can be disjoint (Section 3.1 and
Section 3.3); no separation rate is claimed in that case.

**Single cosine (b = 1, all |c_s| = c).** The membership statement is an
equivalence: for even D, P_v is in H_D if and only if v c is in L_D. The set
{v in V : P_v in H_D} is nonempty iff [c v_min, c v_max] meets L_D, which is
guaranteed when D is divisible by 4 and c (v_max - v_min) >= 4/D.

**Corollary 1 (canonical CHSH).** Every CHSH setting pair has |c_s| = 1/sqrt2.
For every D divisible by 4 with D (v_max - v_min) >= 4 sqrt2, no CHSH dataset of
any size can separate H_D from the Werner family with unknown visibility.
Example: D = 32 (5 bits) and x = 5/8 give v = 5 sqrt2 / 8, about 0.884. The law
(3/32, 13/32, 13/32, 3/32) is a 32-grid law with |S| = 4x = 5/2, which lies
inside the Delft 2015 interval S = 2.42 +/- 0.20 (ST-F50). The Delft fit lies in
the visibility-phase family (ST-F51), where Section 6 shows that
non-identifiability is, if anything, easier. This is a statement about the
declared Werner model, not about the Delft apparatus.

### 3.3 Negative result (correction to the sketch)

The sketch claimed that for every D divisible by 4 there is a v in [v_min, 1]
with P_v in H_D. This is false. Counterexample: c = 1/sqrt2 (CHSH),
v in [9/10, 1], D = 4. Here L_4 = {-1, 0, 1} does not meet [0.636, 0.708]. For
v in [9/10, 1], among D = 0 mod 4 in [4, 400], exactly D in
{4, 8, 16, 20, 28, 32, 44} fail; for v in [1/2, 1] only D = 4 fails. The correct
statement is the interval criterion above, which always holds once
D >= 4 / (c (v_max - v_min)) with 4 | D.

## 4. Theorem 2 (identification through a v-free invariant)

Let the schedule contain s1 with c = 1 (theta = 0) and s2 with c = 1/sqrt2
(theta = pi/4), and let v_min > 0. Write Delta_1 = tau_1(Q) - v and
Delta_2 = tau_2(Q) - v/sqrt2. The ratio tau_2 / tau_1 = 1/sqrt2 is free of v and
irrational.

**(a) Correlator separation.** For every D >= 1, every Q in H_D and every v in
[v_min, v_max]:

```text
|Delta_1| + |Delta_2|          >= min( v_min, 1 / ((2 + sqrt2) D^2) ),
max(|Delta_1|, |Delta_2|)      >= g_*(D) := min( v_min, 1 / ((3 + 2 sqrt2) D^2) ).
```

**(b) TV separation.** If the settings are drawn with weights w (identical
under both hypotheses), then

```text
TV(Q, P_v) >= (min(w_1, w_2) / 2) * min( v_min, 1/((2 + sqrt2) D^2) ).
```

*Proof.* Write tau_i(Q) = m_i / D with |m_i| <= D. If m_1 = m_2 = 0, then
|Delta_1| = v >= v_min. Otherwise m_1^2 - 2 m_2^2 is a nonzero integer, because
sqrt2 is irrational, so

```text
|m_1 - sqrt2 m_2| = |m_1^2 - 2 m_2^2| / |m_1 + sqrt2 m_2| >= 1 / ((1 + sqrt2) D).
```

The identity tau_1/sqrt2 - tau_2 = Delta_1/sqrt2 - Delta_2 holds because
v/sqrt2 - v/sqrt2 = 0. It gives
|Delta_1|/sqrt2 + |Delta_2| >= |m_1 - sqrt2 m_2| / (sqrt2 D) >= 1/((2 + sqrt2) D^2),
which yields the l1 form because |Delta_1| >= |Delta_1|/sqrt2. For the max form,
(1 + 1/sqrt2) max(|Delta_1|, |Delta_2|) >= |Delta_1|/sqrt2 + |Delta_2| >=
1/((2 + sqrt2) D^2), and (2 + sqrt2)(1 + 1/sqrt2) = 3 + 2 sqrt2. For (b),
|E_q f - E_p f| <= 2 TV for f = AB in [-1, 1], so
TV(Q, P_v) = sum_s w_s TV_s >= (1/2) sum_s w_s |tau_s(Q) - v c_s| >=
(min w / 2)(|Delta_1| + |Delta_2|). QED.

**Theorem 2' (any quadratic-irrational ratio; lower bound only).** Let
rho = c_2 / c_1 be a root of a primitive integer quadratic A t^2 + B t + C with
irrational roots rho, rho' (|A| >= 1). Since tau_2 - rho tau_1 =
Delta_2 - rho Delta_1, and the form f(m_2, m_1) = A m_2^2 + B m_1 m_2 + C m_1^2 =
A (m_2 - rho m_1)(m_2 - rho' m_1) is a nonzero integer for (m_1, m_2) != 0, we get,
for (m_1, m_2) != 0,

```text
|Delta_2| + |rho| |Delta_1| >= |m_2 - rho m_1| / D >= 1 / (|A| (1 + |rho'|) D^2),
```

hence

```text
|Delta_1| + |Delta_2| >= min( v_min |c_1|, 1 / (|A| (1 + |rho'|) max(1, |rho|) D^2) ),
```

where the first branch covers m_1 = m_2 = 0, for which |Delta_1| = v |c_1|.
Example: theta in {0, pi/6}, rho = sqrt3/2, A = 4, rho' = -sqrt3/2, giving
1/((4 + 2 sqrt3) D^2). No attainment or upper bound is proved for a general
ratio.

**(c) Attainment (sharp order for every D = 0 mod 4 with D >= 4/(v_max - v_min),
schedules with cosines in {0, +-1, +-1/sqrt2}).** Suppose every c_s lies in
{0, +-1, +-1/sqrt2}, 4 | D, N = D/4 and (v_max - v_min) N >= 1. Take the largest
Pell numerator P <= (v_max - v_min) N, where P^2 - 2Q^2 = +-1 for (P, Q) in
(1,1), (3,2), (7,5), (17,12), ... Consecutive numerators satisfy
P_{j+1} = 2 P_j + P_{j-1} <= 3 P_j, so P > (v_max - v_min) N / 3. Set
k = floor(v_max N / P), p = kP, q = kQ and v = p/N, which lies in
(v_min, v_max]. Let Q have Werner-shaped laws with x = +-p/N on the +-1
settings, which matches exactly, x = 0 on the cosine-0 settings, which matches
exactly, and x' = +-q/N on the +-1/sqrt2 settings. All of these are D-grid laws
by 3.1. On a 1/sqrt2 setting,

```text
Delta = |p/(sqrt2 N) - q/N| = k / (sqrt2 N (P + sqrt2 Q)) <= v_max / (sqrt2 P^2)
      < 144 v_max / (sqrt2 (v_max - v_min)^2 D^2).
```

For Werner-shaped laws, TV_s = Delta/2 and chi^2(Q_s || P_s) = Delta^2 / (1 - x^2)
<= 2 Delta^2, since x <= 1/sqrt2. Along the Pell subsequence D = 4P with v = 1
(x' = Q/P), the receipt gives D^2 TV_s -> 2 sqrt2, D^4 KL_s -> 32 and
D^4 chi^2_s -> 64. Hence for fixed weights, v_min > 0 and v_max - v_min > 0, the
separation inf over (Q, v) of TV is Theta(1/D^2) along every D = 0 (mod 4)
beyond an explicit threshold. The Pell attainment is classical continued-fraction
theory for sqrt2.

**(d) Sample complexity: Theta(D^4 log(1/eps)).**

*Achievability (fixed-count design).* Take a design with n trials at each of s1
and s2 (fixed counts; adaptive allocation is not covered by this bound). Accept
W if and only if the l_inf distance from the empirical pair
(tau_1_hat, tau_2_hat) to the segment {v (1, 1/sqrt2) : v in V} is below g_*/2.
Under any P_v the true pair lies on the segment. Under any Q in H_D it is at
least g_* away by (a). Hoeffding for {+-1} variables then bounds both error
probabilities by 4 exp(-n g_*^2 / 8). Once D^2 v_min >= 1/(3 + 2 sqrt2), the
condition

```text
n >= 8 (3 + 2 sqrt2)^2 D^4 ln(4/eps)  (about 271.8 D^4 ln(4/eps))
```

makes both errors at most eps, uniformly over the composite W and the composite
H_D.

*Converse.* Take any design, adaptive allowed, over settings with c_s in
{0, +-1, +-1/sqrt2}, and use the renderer from (c). By the chain rule,
KL(Q^(n) || P_v^(n)) = E_Q[n_irr] * KL_irr, where n_irr counts trials at
+-1/sqrt2 settings and KL_irr <= chi^2 <= 2 Delta^2. By Bretagnolle-Huber
(Z. Wahrsch. verw. Gebiete 47 (1979) 119-137), alpha + beta >= (1/2) exp(-KL).
So alpha, beta <= eps forces

```text
E_Q[n_irr] >= ln(1/(4 eps)) / (2 Delta^2) >= ((v_max - v_min) D / 12)^4 ln(1/(4 eps)) / v_max^2.
```

Along D = 4P_j with v_max = 1 the constant improves to roughly
D^4 ln(1/(4 eps)) / 32. The upper and lower constants differ by a large factor
(receipt: about 2.5 x 10^8 for v in [1/2, 1]); only the order D^4 log(1/eps) is
claimed to be sharp, and only for designs restricted to cosines in
{0, +-1, +-1/sqrt2}. Designs that use other angles are not covered by the
converse.

**Proof status.** (a), (b), (c) and (d) are complete proofs. The receipt checks
them on a declared grid of 110 values of D up to 10^4, and checks the converse
construction exactly for every D = 0 (mod 4) in [8, 2000]. On that grid the
empirical min of D^2 g_D over D >= 8 is 0.8368 (at D = 200), against the
analytic constant 0.1716.

## 5. Theorem 3 (known visibility, binary grids)

**(a) Universal converse (any family, any angles, any adaptivity, fixed
horizon).** For every base law, setting set and adaptive design with K-outcome
trials and D > K/4, there is a renderer Q in H_D (per-setting largest-remainder
rounding) with BC(q_s, p_s) >= 1 - K/(4D) for every s. Hence any test with a
fixed horizon n (or an almost surely bounded stopping time N <= n) and both
errors at most eps < 1/4 needs

```text
n >= ln(1/(4 eps)) / (2 ln(1/(1 - K/(4D)))) >= (4D/K - 1) ln(1/(4 eps)) / 2,
```

which is (D - 1) ln(1/(4 eps)) / 2 for Bell trials (K = 4).

*Proof.* By Lemma A, ||q_s - p_s||_1 <= K/(2D). Since
(sqrt a - sqrt b)^2 <= |a - b|, H^2 <= K/(2D), so BC >= 1 - K/(4D). The setting
kernel is the same under both hypotheses, so the transcript BC is at least
(inf_s BC_s)^n by induction on n. Finally alpha + beta >= 1 - TV >= BC^2 / 2,
because BC^2 <= (1 - TV)(1 + TV) (Le Cam). QED. The argument assembles standard
inequalities (rounding, H^2 <= l1, Bhattacharyya tensorization, Le Cam's
1 - TV >= BC^2/2); no novelty is claimed for the Hellinger converse. It does
not bound the expected sample size of unbounded sequential tests.

**(b) Known v = 1 with a D-adapted angle: Theta(D log(1/eps)).** Choose
cos(theta_D) = 1 - 2/D. Then P_1 gives each rare outcome (++) and (--)
probability 1/(2D). For even D (in particular D = 2^K, K >= 1), every Q in H_D
satisfies TV(Q, P_1) >= 1/D, with equality: all fractional parts of D p equal
1/2, so Lemma A gives l1 = 2/D. (For odd D, D p = (1/2, (D-1)/2, (D-1)/2, 1/2),
r = 1 and the minimum TV is 1/(2D); this is checked exactly for
D = 3, 5, 7, 9, 15, 33.) The test "accept P_1 iff N_{++} >= 1, N_{--} >= 1 and
N_{++} + N_{--} <= 1.5 n/D" has both errors at most 3 exp(-n/(16 D)) for every
D. Under Q, accepting requires q(++) and q(--) both nonzero, hence each at least
1/D, so the rare rate is at least 2/D, and the Chernoff lower tail with
delta = 1/4 applies. Under P_1, there are two zero-count events of probability
at most exp(-n/(2D)) each, plus the upper tail exp(-n/(10D)). So
n = 16 D ln(3/eps) suffices. Since H_{D'} is contained in H_D for D' | D, one
design at D = 2^K covers every coarser binary grid. With (a), the trial count
is Theta(D log(1/eps)).

The adapted angle gives per-setting TV 2^{-k} (not just order 2^{-(k+1)}),
and, more importantly, the relevant metric is Hellinger rather than TV.
Because the rare outcomes have probability of order 1/D, H^2 is of order 1/D
rather than TV^2 = 1/D^2, so the cost is D trials, not D^2.

**(c) Known v = 1 at the fixed angle pi/4: the binary digits of sqrt2.** For
D = 2^k with k >= 3,

```text
TV_k := min over Q in H_D of TV(Q, P_1 at pi/4) = 2^{1-k} || 2^{k-3} sqrt2 ||.
```

*Proof.* D p = 2^{k-2} -+ 2^{k-3} sqrt2. The fractional parts are
(1 - phi, phi, phi, 1 - phi) with phi = frac(2^{k-3} sqrt2) and r = 2. Lemma A
gives l1 = 4 min(phi, 1 - phi) / D. QED.

Let n_k(eps) be the least fixed n such that some test using only the setting
pi/4, with v = 1 known, has type I error at most eps under P_1 and type II
error at most eps uniformly over H_{2^k}; take eps < 1/4. All probabilities are
at least (2 - sqrt2)/8, so chi^2 <= l1^2 / p_min = 32 TV^2 / (2 - sqrt2). Then

```text
(2 - sqrt2) ln(1/(4 eps)) / (32 TV_k^2) <= n_k <= 8 ln(8/eps) / TV_k^2,
```

with achievability from Hoeffding on the four empirical frequencies.
Consequences:

- n_k >= c 4^k ln(1/(4 eps)) for every k, since ||.|| <= 1/2.
- An effective Liouville bound, |2 * 4^m - a^2| >= 1, gives
  ||2^m sqrt2|| >= 1/(2^{m+1} sqrt2 + 1/2), and hence n_k = O(16^k log(1/eps)).
- Ridout's theorem (D. Ridout, "Rational approximations to algebraic numbers",
  Mathematika 4 (1957) 125-131), a p-adic Thue-Siegel-Roth result that applies
  with denominators that are powers of 2, gives ||2^m sqrt2|| >= 2^{-e m} for
  m >= m_0(e). Hence n_k <= C_e 4^{(1+e)k} log(1/eps). This bound is
  ineffective.
- n_k = O(4^k log(1/eps)) for all k holds if and only if
  inf_m ||2^m sqrt2|| > 0, that is, iff the binary expansion of sqrt2 has
  bounded runs of equal digits. This is open (Section 7). Base-2 normality of
  sqrt2 (also open) would imply unbounded runs, hence a negative answer. Under a
  random-digit heuristic, runs of length about log_2 k recur and n_k / 4^k grows
  roughly like k^2.

**Finite check (ST-F57).** Exact branch decisions (math.isqrt on 2 * 4^m) with
80-digit Decimal values for k = 3..64: min_k 2^k TV_k = 0.01198 (at k = 32) and
max = 0.994. Brute force over all grid laws confirms the formula for k <= 5.

**53-bit fixed-point grid (illustration only).** For D = 2^53, the universal
lower bound is about 7.2 x 10^15 trials (eps = 0.05) and the adapted design
needs about 5.9 x 10^17. With the {0, pi/4} schedule (cosines in
{0, +-1, +-1/sqrt2}) and v in [1/2, 1], between 3.2 x 10^58 trials (necessary for
such designs) and 7.8 x 10^66 per setting (sufficient). IEEE-754 binary64
renderers are not H_D for any D: their spacing is relative (reaching 2^-1074
near 0), the rare-outcome probability 2^-54 used by (b) is exactly
representable, and their probabilities need not sum to one exactly. Theorem 3(b)
does not apply to them, and their analysis is open.

## 6. Remark (not claimed): a phase nuisance (ST-T11 family) re-opens non-identifiability

In the visibility-phase family tau_s = v cos(theta_s - phi), two settings with
theta_1 != theta_2 mod pi, a phase range with nonempty interior and
v_min < v_max do not identify for all sufficiently large D = 0 mod 4: the map
(v, phi) -> (tau_1, tau_2) has open image, which then contains points of L_D^2.
Three settings satisfy one linear relation tau_3 = a tau_1 + b tau_2.

- For {0, pi/4, pi/2} the relation is sqrt2 tau_2 = tau_1 + tau_3, which has the
  rational solutions tau_2 = 0, tau_1 = -tau_3. At phi = -pi/4,
  tau = v (1/sqrt2, 0, -1/sqrt2), and with v/sqrt2 in (4/D)Z every law is a
  D-grid law. This is non-identifiable (exact check at D = 32; hits at
  x = 3/8, 1/2, 5/8 for v in [1/2, 1], and also x = 1/8, 1/4 for v < 1/2).
- For {0, pi/4, pi/3}, (1, a, b) = (1, (1 - sqrt3)/2, sqrt6/2) is Q-linearly
  independent, because 1, sqrt3 and sqrt6 are. The plane therefore contains no
  nonzero rational point, and since v_min > 0 the separation is positive for
  every D. The rate is not established.

This remark is not registered as a claim.

## 7. Open problems (ST-O04)

1. Fixed angle pi/4, known v = 1: is n_k = O(4^k log(1/eps))? This is
   equivalent to inf_m ||2^m sqrt2|| > 0, a classical open question on the
   binary digits of sqrt2. Borel's normality conjecture (E. Borel, C. R. Acad.
   Sci. Paris 230 (1950) 591-593) would imply a negative answer; see Bugeaud,
   Distribution Modulo One and Diophantine Approximation, Cambridge Tracts in
   Math. 193 (2012). Proving either direction is beyond current methods.
2. Unknown v with free (adaptive) angle choice: the minimax trial count lies
   between Omega(D log(1/eps)) (Theorem 3a) and O(D^4 log(1/eps)) (Theorem 2).
   With v_max < 1 there are no rare outcomes, and Theta(D^2 log(1/eps)) is
   plausible but unproved.
3. J-setting schedules. Expected (sketch, not proved): if the vector
   (rho_2, ..., rho_J) is simultaneously badly approximable, an argument like
   Theorem 2 should give a separation of at least c D^{-1 - 1/(J-1)}. An example
   is a basis of a real number field of degree J, such as the cosines of
   {0, 2pi/7, 4pi/7} (Perron, Math. Ann. 83 (1921); Cassels, An Introduction to
   Diophantine Approximation (1957), Ch. V). The matching upper bound, which
   needs Dirichlet approximations landing in [v_min, v_max], and the
   phase-nuisance rates are not established.

## 8. Nonclaims

- No claim that physical probabilities are or are not rational, or that any
  simulator exists. Every statement concerns observable laws in the declared
  Werner model.
- **D must be declared.** All rates are for a declared D (or a declared finite
  set of D). With D undeclared, the union of H_D over all D contains every
  rational law and is dense, so no test is uniformly consistent; only
  non-uniform, eventually-correct procedures exist in the sense of Cover
  (Ann. Statist. 1 (1973) 862-871) and Dembo and Peres (Ann. Statist. 22 (1994)
  106-117).
- **Setting cosines are known exactly.** A cosine calibration uncertainty eta
  voids the identifiability results: the Pell renderer of Theorem 2(c) is
  exactly a Werner law at cosine Q/P, within 1/(sqrt2 P^2) of 1/sqrt2, so
  eta >= 144/(sqrt2 (v_max - v_min)^2 D^2) puts it inside the family; and every
  correlator is within 2/D of L_D, so eta >= 2/D voids Theorems 3(b) and 3(c).
  Renderers that also discretise measurement angles (for example Palmer 2020,
  which requires rational cos theta) are outside scope; for them the
  irrationality mechanism does not apply.
- Not covered: renderers allowed real-valued probabilities, exact algebraic
  arithmetic, floating-point non-associativity or rounding of intermediate
  quantities, IEEE-754 floating-point renderers (non-uniform grids, not H_D for
  any D), precision in anything other than per-trial outcome probabilities
  (angles, timing, detector efficiencies), non-stationary or memoryful
  renderers, and deterministic time-varying (for example sigma-delta) grid
  schedules, which may be nearly indistinguishable from the base law.
- Theorem 1 is a frequentist and point-Bayes-factor non-identifiability. With a
  continuous prior on v, a composite Bayes factor of H_D against W can drift by
  about (1/2) ln n at a grid point (Occam/Lindley, the same -(1/2) ln n term as
  ST-T271). This is prior-driven and is not evidence of precision.
- Theorem 3(b) assumes v = 1 exactly and the angle set exactly. Robustness to
  small visibility loss (of order 1/D) is not claimed. With v_max < 1 the
  rare-outcome mechanism disappears.
- Constants in Theorem 2(d) are explicit but loose. Only the order
  D^4 log(1/eps) is sharp, and only for designs restricted to cosines in
  {0, +-1, +-1/sqrt2}.
- Corollary 1 does not say the Delft data were produced by a 5-bit renderer. It
  says the CHSH schedule cannot rule one out under this model.
- Ridout's bound is ineffective, and no explicit m_0(e) is claimed.

## 9. Prior art

- Systematic dithering (Theorem 0a): Madow (1949); dependent rounding.
- Lemma A: Hamilton (largest-remainder) apportionment, Balinski and Young
  (1982); Boecherer and Geiger, arXiv:1307.6843.
- Finite-bit Born probabilities with rational-cosine constraints, using Niven's
  theorem against irrational cosines, is the same number-theoretic mechanism as
  Theorem 2: Palmer, Proc. R. Soc. A 476 (2020) 20190350; proposed experimental
  tests: Hance, Palmer and Rarity, Phys. Scr. 100 (2025) 065123
  (arXiv:2102.07795); Palmer, "Rational Quantum Mechanics", arXiv:2510.02877.
  Discrete Hilbert space: Buniy, Hsu and Zee (2005).
- Finite-precision measurement directions: Meyer, Phys. Rev. Lett. 83, 3751
  (1999); Kent, Phys. Rev. Lett. 83, 3755 (1999); Clifton and Kent, Proc. R. Soc.
  A 456 (2000) 2101.
- Rational versus irrational testing with undeclared precision: Cover (1973);
  Dembo and Peres (1994).
- Diophantine inputs: Pell equation and continued fractions for sqrt2 (classical);
  Ridout (1957); Perron (1921); Cassels (1957); Borel (1950); Bugeaud (2012).
- Standard inequalities: Hoeffding (1963); Bretagnolle and Huber (1979); Le Cam
  (1973, 1986) for 1 - TV >= BC^2/2.

Theorem 0(a), Lemma A and the Diophantine inputs are standard. The novelty is
the application to H_D versus the Werner family under a visibility nuisance
(Theorems 1 and 2) and the rate analysis (Theorems 2(c,d) and 3(b,c)).

## 10. Relation to existing claim IDs

- **ST-T01**: Theorems 0(a) and 1 exhibit H_D members with P_sim = P_base, so
  BF = 1 by ST-T01.
- **ST-T09**: Werner-shaped TV per setting, |x - x'|/2, and the TV aggregation by
  setting weights.
- **ST-T10**: the converses use the same KL and Bretagnolle-Huber machinery
  under adaptive designs.
- **ST-M03**: memory bounds on finite visibility grids; by Section 3.1, H_D
  intersected with the Werner family is a finite visibility grid L_D/c.
- **ST-F50 and ST-F51**: the source of S = 2.42 +/- 0.20 used in Corollary 1, and
  the visibility-phase reading of the Delft data (a CHSH schedule shifted by pi,
  which leaves |c_s| = 1/sqrt2 unchanged).
- **ST-T271**: the composite Bayes-factor -(1/2) ln n Occam term mentioned in the
  nonclaims.
- **ST-T11, ST-T15, ST-M04**: Section 6 shows that adding the phase nuisance can
  destroy identifiability. Fisher-rank identifiability of (v, phi) (ST-M04) does
  not imply identifiability of H_D, which is a discrete, non-smooth subclass.
- **Formal-results open problem 4** (precision architectures) and
  research-program Campaign L items 1, 2 and 7: this note declares the null and
  alternative, the nuisance, the boundary (dithering), and which classes remain
  untouched.
- Related but distinct: ST-T306 to ST-T309 (Le Cam deficiency of a noisy Bell
  simulator, equal-magnitude schedules).
