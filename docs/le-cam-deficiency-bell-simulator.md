# Le Cam deficiency of a visibility-contracted Bell simulator

Claims ST-T306 to ST-T309, ST-F60 and ST-O08
([manifest](../claims/le-cam-deficiency-claims.json)). Certificate:
`src/simtheory/le_cam_deficiency.py`, receipt
[`receipts/le-cam-deficiency-bell-simulator.txt`](../receipts/le-cam-deficiency-bell-simulator.txt),
tests in `tests/test_le_cam_deficiency_bell_simulator.py`.

Status: **Theorem** (the randomized value, ST-T306; the worst-setting value for
unequal magnitudes, ST-T307), **standard theorem** (risk transfer, ST-T308),
**Theorem with an exact computer-assisted step** (deterministic setting-wise
relabelings, ST-T309: the dominating set of error pairs is established by exact
rational evaluation at every arrangement vertex, a piecewise-linear
certificate), **Finite check** (exact averaged deterministic values on two
declared schedules, ST-F60), **Open problem** (closed form for schedules with
unequal correlation magnitudes under schedule averaging, ST-O08).

The deficiency framework is classical: deficiency, the Le Cam distance and the
randomization criterion are due to Le Cam (Ann. Math. Statist. 35 (1964)
1419-1455; Asymptotic Methods in Statistical Decision Theory, Springer 1986;
Le Cam and Yang 2000), and after the endpoint and sufficiency reductions below,
the value is a deficiency between Bernoulli dichotomies, governed by Torgersen's
dichotomy theory (Torgersen, Z. Wahrsch. verw. Geb. 16 (1970) 219-249;
Comparison of Statistical Experiments, Cambridge University Press 1991;
Strasser 1985). The new content is the closed form for this Bell family and the
deterministic gap.

The proposed statement is true as sketched, with these precisions:

1. "Strictly beats the naive two-point bound": the exact value is strictly
   larger than that lower bound iff `C lam > 0` and `lam < 1`; the two coincide
   when `C lam = 0` or `lam = 1`.
2. The deterministic-versus-randomized gap for setting-preserving kernels is
   strict for every `0 <= lam < 1` when `0 < C < 1`, under both aggregations
   below. At `C = 1` the worst-setting gap is strict exactly for `0 < lam < 1`;
   the averaged lower bound collapses to the randomized value, so no gap is
   claimed there.
3. When settings are drawn at random and TV is taken on the joint (setting,
   outcome) record, setting-preserving deterministic relabelings can be varied
   across settings and so partially randomize. For `0 < C < 1` and
   `0 <= lam < 1` this shrinks the gap but never closes it: averaging error
   pairs across settings is strictly weaker than averaging distributions inside
   one setting before taking TV. Deterministic maps that may also relabel the
   setting are not covered and can do better (Section 6).

## 1. Interface and definitions

One trial. A setting pair `i` is drawn from a public schedule `pi` (finite,
full support) and announced. Outcomes `a, b in {+1, -1}`. The declared family
(the ST-T11 family at fixed phase, with `c_i = -cos(alpha_x - beta_y)`):

    P_v(a, b | i) = (1 + v a b c_i) / 4,     v in [0, 1].

Assumption (equal magnitudes): `|c_i| = C in [0, 1]` for every `i`; write
`sigma_i = sign(c_i)`. Canonical CHSH has `C = 1/sqrt2` with three `-` signs and
one `+` sign (ST-T12 schedule).

- Physics experiment `E = {P_v : v in [0, 1]}`.
- Simulator experiment `F = {P_{lam v} : v in [0, 1]}`, fixed `lam in [0, 1]`.
- A setting-preserving kernel is a family `K = (K_i)` of 4x4 row-stochastic
  matrices acting on `(a, b)` given the public setting `i`. A joint kernel is a
  Markov kernel on the whole (setting, outcome) record.
- `TV` is half the L1 distance.
- Per-setting error `e_i(K, v) = TV(P_{lam v}(.|i) K_i, P_v(.|i))`.

Two aggregations of the deficiency `delta(F, E) = inf_K sup_v err(K, v)`:

- `avg`: `err = sum_i pi_i e_i(K, v)`, the TV of the joint (setting, outcome)
  law, as in ST-T12;
- `max`: `err = max_i e_i(K, v)`, the worst setting pair.

`delta_det` denotes the same infimum restricted to deterministic
setting-preserving kernels (each `K_i` a 0/1 matrix, i.e. a function
`g_i : {+-1}^2 -> {+-1}^2`).

**Locality.** The kernels here are central post-processings: the optimal one
sees both settings and both outcomes and writes `b := sigma_i a`, which is a
signalling operation, not a Bell-local (LOSR) one.

## 2. Preliminary lemmas

**Lemma 0 (Blackwell direction).** `delta(E, F) = 0`. The setting-blind
depolarizing kernel `lam I + (1 - lam) J/4` maps `P_v` to `P_{lam v}` exactly,
since `lam (1 + v ab c)/4 + (1 - lam)/4 = (1 + lam v ab c)/4`. Hence the Le Cam
distance is `Delta(E, F) = delta(F, E)`, and everything below concerns the hard
direction. This is a randomized garbling in the sense of Blackwell
(Proc. Second Berkeley Symp. 1951, 93-102). (Checked exactly.)

**Lemma 1 (endpoint reduction).** For any fixed kernel, `v -> e_i(K, v)` is
convex on `[0, 1]`, so `sup_v err(K, v) = max(err(K, 0), err(K, 1))` under both
aggregations.

*Proof.* `P_{lam v} K_i - P_v` is affine in `v` (both laws are affine in `v`
and `K_i` is linear), and a norm of an affine map is convex. Sums with
nonnegative weights and maxima of convex functions are convex, and a convex
function on an interval attains its sup at an endpoint. QED

Write `U = P_0` (uniform), `Q = P_lam`, `P_1` for the per-setting laws, and
`A_i = {(a, b) : ab = sigma_i}` (the "agreeing" class, two outcomes).

## 3. Theorem ST-T306 (exact randomized deficiency)

Under the equal-magnitude assumption, for every full-support schedule and
under both aggregations,

    delta(F, E) = C (1 - lam) / (2 (2 - C lam)).

Under `avg` aggregation the value is unchanged if kernels may act on the whole
(setting, outcome) record, so it is the Le Cam deficiency of the joint-record
experiments in the standard sense; the restriction to setting-preserving
kernels matters only for ST-T309 and ST-O08. Under `max` aggregation it is the
deficiency with parameter (v, i).

For canonical CHSH this is `(1 - lam) / (2 (2 sqrt2 - lam))`; at `lam = 1/2` it
equals `1/62 + (2/31) sqrt2 = 0.1073688...`.

**Optimal kernel.** With `s = C (1 - lam) / (2 - C lam) in [0, 1]`,

    K_i = (1 - s) I + s M_i,   M_i : (a, b) -> (a, sigma_i a),

i.e. keep the data with probability `1 - s`, otherwise overwrite `b` by the
setting-aware perfectly (anti)correlated value.

*Upper bound.* `M_i` sends any law with uniform `a`-marginal to `D_i`, the
uniform law on `A_i`. At `v = 0`: `U K_i = (1 - s) U + s D_i`, so
`e_i(0) = s TV(D_i, U) = s/2`. At `v = 1`: `Q K_i = (1 - s) Q + s D_i`. On each
of the two outcomes outside `A_i`,

    Q K_i - P_1 = [(1 - s)(1 - lam C) - (1 - C)]/4 = [C(1 - lam) - s(1 - lam C)]/4 = s/4 >= 0

(using `s (2 - C lam) = C (1 - lam)`), and the positive part of `Q K_i - P_1`
lives only there, so `e_i(1) = s/2`. Thus `e_i(0) = e_i(1) = s/2` for every
`i`, both aggregations equal `s/2`, and Lemma 1 gives `sup_v err = s/2`. QED

*Lower bound (explicit dual).* Fix any kernel and a setting `i`. Put
`f = 1_{A_i}` and `w = (1 - lam C)/(2 - lam C) in [0, 1]`, so
`w = (1 - w)(1 - lam C)`. Since TV dominates the mass difference on any event,

    e_i(0) >= <f, U K_i - U>,     e_i(1) >= <f, P_1 - Q K_i>.

Hence

    w e_i(0) + (1 - w) e_i(1)
      >= sum_z sum_z' K_i(z, z') f(z') [w U(z) - (1 - w) Q(z)]  -  w U(A_i) + (1 - w) P_1(A_i).

The bracket is `(1 - w)[(1 - lam C) - (1 + lam C)]/4 = -(1 - w) lam C / 2` for
`z in A_i` and `0` for `z` outside `A_i`. Since `sum_z' K_i(z, z') f(z') <= 1`,
the double sum is at least `-(1 - w) lam C`. With `U(A_i) = 1/2` and
`P_1(A_i) = (1 + C)/2`,

    w e_i(0) + (1 - w) e_i(1) >= (1 - w)[-lam C - (1 - lam C)/2 + (1 + C)/2]
                              = (1 - w) C (1 - lam) / 2
                              = C (1 - lam) / (2 (2 - C lam)).

For `avg`: `sup_v err >= max(E_0, E_1) >= w E_0 + (1 - w) E_1`, where
`E_v = sum_i pi_i e_i(v)`, and the right side is the `pi`-average of the
per-setting bounds. For `max`: any single setting already gives the bound.
QED

*Joint kernels.* The same certificate applies to every Markov kernel K on the
joint record under `avg`: take f to be the indicator of the joint agreeing set
`{(i, (a, b)) : ab = sigma_i}` and repeat the computation with joint laws; the
bracket is `-pi_i (1 - w) lam C / 2` on the agreeing cells of setting i and 0
elsewhere, `sum_z' K(z, z') f(z') <= 1`, and the constants are unchanged. The
check minimizes this linear objective row-wise over all kernels on the 16-cell
joint record exactly and finds equality with the formula on both schedules and
every grid point.

*Decision reading of the dual.* The certificate is a two-point Bayes problem:
prior weight `w` on `v = 0` and `1 - w` on `v = 1`, with the setting-aware test
"report correlated-with-sign-`sigma_i`". The check evaluates this bound as an
exact minimum over all kernels (the objective is linear in `K`, so the minimum
is a row-wise vertex choice) and finds equality with the primal value on every
grid point.

**Comparisons.** The identity kernel gives `C (1 - lam)/2`. Data processing
(ST-T58 style) with the triangle inequality gives the naive bound
`C/2 = TV(P_0, P_1) <= 2 delta + TV(P_0 K, P_lam K) <= 2 delta + lam C/2`, i.e.
`delta >= C (1 - lam)/4`. The exact value is `2/(2 - C lam)` times the naive
bound and `1/(2 - C lam)` times the identity value, so for `0 < lam < 1` and
`0 < C <= 1`:

    C (1 - lam)/4  <  delta  <  C (1 - lam)/2.

The value is strictly decreasing in `lam` for `C > 0`
(`d/dlam = C(C - 2)/(2(2 - C lam)^2)`) and strictly increasing in `C` for
`lam < 1` (`d/dC = (1 - lam)/(2 - C lam)^2`).

## 4. Theorem ST-T307 (worst-setting value for unequal magnitudes)

For an arbitrary finite schedule with magnitudes `C_i = |c_i|`, under `max`
aggregation, `delta = V(max_i C_i)` where `V(C) = C(1 - lam)/(2(2 - C lam))`.
Proof: use the ST-T306 kernel with `C_i` in each setting (errors
`V(C_i) <= V(C_max)`, as `V` is increasing in `C`), and apply the dual at a
setting attaining `C_max`. The check verifies this exactly for
`c = (1/2, -1/10, 3/5)` on the `lam` grid. The result is elementary given
ST-T306.

## 5. Theorem ST-T308 (risk transfer; standard)

Assume equal magnitudes and let `delta` be the ST-T306 value (any schedule; a
decision may depend on the setting). Let `L(v, d)` be any bounded loss and
`rho` any (possibly randomized) decision rule on the declared interface.
Running `rho` on the simulator's record after the optimal kernel gives, for
every `v in [0, 1]`,

    |R_F(v, rho o K) - R_E(v, rho)| <= 2 delta ||L||_inf,

and `<= M delta` when `L` takes values in `[0, M]`.

Proof: the risk difference is `<h_v, P_{lam v} K - P_v>` with
`h_v(z) = sum_d rho(d|z) L(v, d)`, `|h_v| <= ||L||_inf`, and
`|<h, p - q>| <= 2 ||h||_inf TV(p, q)`. Tightness: for every kernel `K` there is
`v in {0, 1}` with error at least `delta`, and the loss `L(v, d) = +1` if `d` is
in the TV-witnessing event, `-1` otherwise, with `rho` = report the outcome,
attains `2 TV >= 2 delta`. So `inf_K sup_{L, rho, v} |risk gap| = 2 delta` for
`||L||_inf <= 1`. (For the optimal kernel the gap `2 delta` is attained at
`v = 0` by `h = +1` on `A_i`, `-1` off it; tested, also with setting-dependent
losses on the joint record.)

This is the easy direction of Le Cam's randomization criterion (Le Cam 1964;
Torgersen 1991) and is not new. With unequal magnitudes under `max`
aggregation, the bound `2 V(C_max) ||L||` still holds, but tightness is not
claimed: joint-record decisions see only the averaged TV, which can be strictly
smaller.

## 6. Theorem ST-T309 (deterministic setting-wise relabelings and the randomization gap)

Throughout this section kernels are setting-preserving. Label the three
per-setting error pairs `(e(0), e(1))`:

    A = (0,   C(1 - lam)/2)      identity (or any class-preserving bijection)
    B = (1/4, (1 - lam C)/4)     one disagreeing outcome merged into an agreeing one
    D = (1/2, (1 - C)/2)         (a, b) -> (a, sigma a)

**(a) Dominating set (exact computer-assisted proof).** For every
`C in [0, 1]`, `lam in [0, 1]`, every one of the 256 deterministic relabelings
of a setting has error pair dominated coordinatewise by one of `A, B, D`, and
all three are attained. The Pareto frontier is contained in `{A, B, D}`; it
need not equal it (B is dominated by A whenever `1 + lam C >= 2C`, for example
for every `lam` at `C = 1/2`, and D by B whenever `(2 - lam) C <= 1`).

*Proof.* `e(0)` depends only on the fiber sizes `n_j` of `g`:
`e(0) = sum_j |n_j - 1|/8 in {0, 1/4, 1/2, 3/4}`. With `t = lam C`,
`e(1) = (1/8) sum_j |(n_j - 1) + m_j t - s_j C|` with integers `m_j` and
`s_j = +-1`. The claim says `e(1) >= T(e(0))` where `T(0) = (C - t)/2`,
`T(1/4) = (1 - t)/4`, `T(1/2) = T(3/4) = (1 - C)/2`, on the triangle
`{0 <= t <= C <= 1}`. For fixed `g`, `e(1) - T` is linear on each cell of the
arrangement formed by `g`'s (at most four) break lines and the triangle's
edges, so it is nonnegative on the triangle iff it is nonnegative at every
arrangement vertex in the triangle. The check enumerates all 256 maps and all
786 such vertices (pairwise intersections of break lines and edges, a superset
of the cell vertices) in exact rational arithmetic and finds no violation (the
`c < 0` case is the relabeling `b -> -b`). Because the comparison is with the
target at each map's own `e(0)` level, this proves the stronger statement that
every merge map is dominated by B. Attainment is exhibited. The level-0 case
also has a short hand proof: a bijection sending `k` of the two agreeing inputs
to agreeing outputs has `e(1) >= |P_1(A) - Q g^{-1}(A)| = C|1 - (k - 1) lam|/2
>= C(1 - lam)/2` since `k <= 2`. QED

**(b) Worst-setting deterministic value (hand-provable).** Under `max`
aggregation (any schedule, equal magnitudes),

    delta_det = min( C(1 - lam)/2 , 1/4 ).

Proof: by Lemma 1 the value is the per-setting `min_g max(e(0), e(1))`. A
bijection has `e(0) = 0` and `e(1) >= C(1 - lam)/2` (level-0 argument above).
A non-bijection has an empty fiber, hence a fiber of size at least 2, hence
`e(0) >= 1/4`; the map `B` attains `max(1/4, (1 - lam C)/4) = 1/4`. QED

**(c) Averaged deterministic lower bound.** Under `avg` aggregation, any choice
of deterministic setting-preserving `g_i` yields `(E_0, E_1)` in the convex hull
of the per-setting pairs, hence (a) coordinatewise above a point of
`conv{A, B, D}`. Because `(A + D)/2 = B` exactly, this hull is the segment
`AD`, and

    delta_det(avg) >= delta_hull = (1 - lam)/(2 (2 - lam))   if (1 - C) < C (1 - lam),
                                 = C (1 - lam)/2               otherwise,

obtained by equalizing coordinates along `AD` (mixing weight
`(1 - lam)/(2 - lam)` on `D`). The first branch does not depend on `C`.

**(d) Strict gap.** For `0 < C < 1` and `0 <= lam < 1`:

    delta < delta_hull <= delta_det(avg)   and   delta < delta_det(max).

First branch: `(1 - lam)/(2(2 - lam)) > C(1 - lam)/(2(2 - C lam))` iff
`2 - C lam > C(2 - lam)` iff `2 > 2C`. Second branch and (b):
`C(1 - lam)/2 > delta` iff `2 - C lam > 1`; and `1/4 >= C/4 > delta` for
`lam > 0`, while at `lam = 0`, `1/4 > C/4 = delta` since `C < 1`. At `C = 1` the
worst-setting gap is strict iff `0 < lam < 1` (at `lam = 0` both equal `1/4`;
tested), and the averaged lower bound equals `delta`, so no averaged gap is
claimed at `C = 1`. For `C = 0` or `lam = 1` everything is 0.

*Mechanism.* The optimal randomized kernel mixes `I` and `M` inside one setting,
so its `v = 1` error is `(C(1 - lam) - s(1 - lam C))/2`, strictly less than the
chord value `(C(1 - lam) - s(2C - lam C - 1))/2` obtained by mixing the error
pairs of `A` and `D`. Mixing laws before TV cancels errors; mixing error pairs
across settings cannot.

**Maps that relabel the setting are not covered.** On the joint record a
deterministic map may also change the setting label, and then the hull bound
fails. On the rational schedule (`C = 3/5`, signs `+,+,+,-`, weights
`1/2, 1/4, 1/8, 1/8`) at `lam = 1/4`, the map `JOINT_DETERMINISTIC_MAP` (found
by a MILP during review, verified exactly here) has errors `1/8` at `v = 0` and
`23/160` at `v = 1`, so its value `0.14375` is below `delta_hull = 3/14` and
below the setting-preserving averaged deterministic value `69/320 = 0.215625`;
it stays above `delta = 9/74`. Whether such maps can reach `delta` is open.

**Relation to ST-T174.** ST-T174 shows that deterministic minimax value is not
a Blackwell invariant because stochastic garbling uses fresh randomness.
ST-T309 is a metric, Bell-family version for setting-preserving kernels: the
Le Cam deficiency (which allows stochastic kernels) is strictly smaller than the
best deterministic setting-wise disguise, and the gap is a randomization
resource. A public setting coin partially substitutes for it ((c) and the
finite check) but cannot close the gap when `0 < C < 1` and `0 <= lam < 1`. The
general separation between information and randomization resources is
classical in spirit (randomized garblings in Blackwell 1951 and Le Cam 1964) and
is recorded in ST-T174; only the explicit frontier and values for this family
are claimed.

## 7. Finite check ST-F60 (exact)

On the canonical uniform CHSH schedule (`C = 1/sqrt2`, in `Q(sqrt2)`) and on a
rational schedule (`C = 3/5`, signs `+,+,+,-`, weights `1/2, 1/4, 1/8, 1/8`),
for `lam in {0, 1/8, ..., 1}`, the exact averaged setting-preserving
deterministic value is computed by letting each setting choose among `A, B, D`
(complete by (a)), and the receipt lists it. Example, canonical `lam = 1/2`:
`delta = 0.107369`, `delta_hull = 1/6`, `delta_det(avg) = 0.169194`,
`delta_det(max) = 0.176777`. The check also verifies the joint-kernel dual, the
setting-relabeling map above, and Corollary ST-T307 on an unequal schedule.

## 8. Illustrative reading (not a data claim)

If one plugged the Delft 2015 value `S = 2.422 +- 0.204` (ST-F50) into the
canonical family as `lam = S/(2 sqrt2)`, the central value gives
`lam ~ 0.8563` and `delta ~ 0.0364`, and the 1-sigma range `S in [2.218, 2.626]`
gives `lam in [0.784, 0.928]` and `delta in [0.0188, 0.0528]`. A renderer at that
visibility could be post-processed to within that TV of ideal visibility-`v`
physics, uniformly in `v`, on this one-trial interface, and no post-processing
could do better. This needs the central (signalling) kernel: a float LP probe
during review over Bell-local (LOSR) post-processing returned the identity
value 0.0509 at `lam = 0.856`, so local post-processing gains nothing there.
This is only an arithmetic illustration: the Delft data are not modelled as this
family, and nothing here is evidence about simulation.

## 9. Nonclaims

- Deficiency is relative to the declared one-trial interface (public setting,
  binary outcomes, the fixed-phase visibility family, `v in [0, 1]`). Nothing is
  claimed about other parameter sets, phases, or richer records.
- **Locality.** The post-processing is central: it sees both settings and both
  outcomes. Deficiency under Bell-local (LOSR) post-processing is not computed;
  it is at least `delta`, and a float LP probe during review (not a
  certificate) gave 0.136730 versus 0.107369 at canonical `lam = 1/2` (compare
  the resource theory of nonlocality under wirings, Gallego, Wurflinger, Acin
  and Navascues, Phys. Rev. Lett. 109, 070401 (2012)).
- **Deterministic maps that relabel the setting** on the joint record are not
  covered by ST-T309; they can beat `delta_hull` (23/160 < 3/14 above); whether
  they can reach `delta` is open.
- Zero or small deficiency does not imply identical implementation; it bounds
  decision-relevant distinguishability on this interface only.
- The n-trial (product-experiment) deficiency is not computed; no asymptotic
  claim is made.
- Setting-blind kernels (not allowed to read the setting) are not analyzed;
  the optimal kernel here uses the sign of `c_i`.
- Under `avg` aggregation with unequal `|c_i|`, no closed form is claimed
  (ST-O08). For setting-preserving kernels a float LP probe during review (not
  a certificate) shows the value can be strictly below `sum_i pi_i V(C_i)`
  (`C = (1/2, 1/10)`, equal weights, `lam = 1/2`: LP `0.041353` versus
  `0.042125`); unrestricted joint kernels gave `1/26 = 0.038462` on the same
  probe, so the setting-preserving value is not the joint-record Le Cam
  deficiency in that case.
- The finite check covers only the listed schedules and `lam` grid; ST-T306 to
  ST-T309 are for all parameters.
- No statement here is evidence for or against any simulation hypothesis; it
  quantifies how far a declared visibility-degraded renderer can be disguised.

## 10. Relation to existing claims

ST-T11 (the family, `c_i = -cos`), ST-T12 (canonical uniform CHSH, joint TV),
ST-T58 (Dobrushin contraction, used only for the naive bound), ST-T174
(information versus randomness), ST-F50 (the Delft statistic in the
illustration). Main has no other deficiency claims.

## 11. Reproduction

    uv run python -m simtheory.le_cam_deficiency     # exact receipt, about 3 s
    uv run python -m pytest -q tests/test_le_cam_deficiency_bell_simulator.py

The receipt ends in `ALL CHECKS PASSED` with a SHA-256 of the receipt body;
every line is exact and environment-independent (no optional LP line).
