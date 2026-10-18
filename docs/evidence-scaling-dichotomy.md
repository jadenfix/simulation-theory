# Evidence scaling dichotomy

Claims ST-T272 to ST-T280, ST-M84, ST-F53 to ST-F55 and ST-O02
([manifest](../claims/evidence-scaling-dichotomy-claims.json)). Certificate:
`src/simtheory/evidence_scaling.py`, receipt
[`receipts/evidence-scaling-dichotomy.txt`](../receipts/evidence-scaling-dichotomy.txt),
tests in `tests/test_evidence_scaling_dichotomy.py`.

## Summary

Two hypotheses about a bit source can differ in two ways, and the expected
evidence behaves very differently in the two cases.

**Part I (the hypotheses disagree about the per-world law).** Under the
alternative a bias q is drawn once from the Jeffreys prior and then the bits
are conditionally IID Bernoulli(q); under the null the bits are fair. For
`q != 1/2` the expected log Bayes factor grows linearly in n. The additive
constant is the Clarke-Barron Jeffreys constant:

```text
E_q[ln BF_n] = n KL(q || 1/2) - (1/2) ln n + (1/2) ln(2e/pi) + o(1)      (q interior)
```

We give a self-contained proof and a non-asymptotic two-sided sandwich of width
1.47 nats that holds for every n (ST-T272 to ST-T274). At `q = 1/2` the
expected log Bayes factor is `-(1/2) ln n + 0.274 + o(1)` and decreases.

**Part II (the hypotheses differ only in weights over shared worlds).** If
the two hypotheses `a` and `b` are laws of one persistent latent world M and
both use the same observation kernel, then no transcript of any length,
stopping rule, or label-independent adaptive policy gives more than
`KL(a || b)` nats of expected evidence about the world-level weights (ST-T277,
the data-processing inequality). The shortfall is an exact
posterior-disagreement term (ST-T278, the chain rule). For conditionally IID
transcripts in which all relevant component pairs have distinct laws, the
shortfall decays at least as fast as `exp(-T (min relevant pairwise Chernoff
information - o(1)))`; without distinct laws it can stay bounded away from
zero (ST-T279). Once the hypotheses also differ about the per-world laws, the
excess over the cap is bounded by the within-world divergence, which can grow
linearly (ST-T280).

**How the two parts relate.** Part I's alternative is itself a single
persistent latent draw (the bias q), so both parts draw a world once and then
sample conditionally IID trials. The dividing line is not "fresh versus
persistent" draws. It is whether the hypotheses differ in the per-world law
(`KL(a || b) = +inf`, or different kernels as in ST-T280) or only in
world-level weights with a common kernel and `KL(a || b) < inf`. Averaging
Part I over `q ~ Jeffreys` gives `KL(aK || bK)` with `a = Jeffreys` and
`b = delta_(1/2)`; since a is not absolutely continuous with respect to b, the
ST-T277 cap is `+inf` and does not bind. Part I's per-q statements refine that
average conditionally on the world. The phrase "fresh redraw" is reserved for
the ST-M67 sense, in which M is redrawn on every trial; that case is covered
by the N-unit form of ST-T277.

**What is new and what is standard.** The data-processing inequality, the KL
chain rule, the Clarke-Barron constant, the Le Cam two-point method with
Pinsker and Bretagnolle-Huber, the Krichevsky-Trofimov regret upper bound and
Hoeffding's inequality are standard; they are cited below and a
self-contained proof is given for completeness. The new content is the
explicit non-asymptotic constants (the uniform pathwise lower regret bound of
ST-T272 and the expected upper bound of ST-T273), the gap bound ST-T279, the
counterexamples, and the beacon power frontier ST-F54.

## Claim map

| claim | kind | statement | status |
| --- | --- | --- | --- |
| ST-T272 | theorem | pathwise sandwich for `ln BF_n` | upper half classical (KT 1981); uniform lower half new |
| ST-T273 | theorem | non-asymptotic expected sandwich | expected upper bound new |
| ST-T274 | theorem | exact additive constant | Clarke-Barron (1990) specialized; proof self-contained |
| ST-F53 | finite check | high-precision remainder table and beacon-scale fair expectation | bounded |
| ST-T275 | theorem | pathwise rejection region and power frontier | elementary, uses Hoeffding |
| ST-T276 | theorem | Le Cam two-point converse | standard (Le Cam, Pinsker, Bretagnolle-Huber) |
| ST-F54 | finite check | beacon power frontier at n = 131072 | bounded |
| ST-M84 | model result | binary symmetric coarsening rescales the frontier | extends ST-M83 |
| ST-T277 | theorem | persistent cap `KL(aK || bK) <= KL(a || b)` | data-processing inequality, standard |
| ST-T278 | theorem | saturation identity and finite-latent zero-gap condition | chain rule, standard; ratio form stated here |
| ST-T279 | theorem | gap bound and decay rate | new bound; MAP-error step classical |
| ST-T280 | theorem | different-kernel decomposition | chain rule plus data processing, standard |
| ST-F55 | finite check | exact-law persistent audit, including counterexamples | bounded |
| ST-O02 | open problem | second-order remainder | formally derived, not proved |

## Part I: hypotheses that disagree about the per-world law

### Setting

`x in {0,1}^n` has `k` ones, and `qhat = k/n`. The KT mixture is
`P_KT(x) = int q^k (1-q)^(n-k) w(q) dq`, where `w(q) = 1/(pi sqrt(q(1-q)))` is
the Jeffreys prior Beta(1/2, 1/2). Define `BF_n(x) = 2^n P_KT(x)` and
`KL(p || 1/2) = ln 2 - H(p)`. Using `Gamma(m + 1/2) = (2m)! sqrt(pi) / (4^m m!)`:

```text
BF_n(k) = C(2k, k) C(2n-2k, n-k) / (2^n C(n, k)),      BF_n(k+1)/BF_n(k) = (2k+1)/(2(n-k)-1).
```

This is exact rational arithmetic. The check matches it against the sequential
KT product on all 8190 sequences with n <= 12. Write
`rho_n(x) = ln[max_q P_q(x) / P_KT(x)]` for the KT regret. Since
`ln max_q P_q(x) = -n H(qhat)`,

```text
ln BF_n(x) = n KL(qhat || 1/2) - rho_n(x)            (exact, pathwise).
```

**Lemma G.** Let `f(x) = ln Gamma(x + 1/2) - x ln x + x - (1/2) ln(2 pi)` for
`x > 0`. Then f is strictly increasing with limit 0, so `f < 0`, that is
`Gamma(x + 1/2) < sqrt(2 pi) x^x e^(-x)`. Also `f(x) >= f(1) = 1 - (3/2) ln 2`
for `x >= 1`.

*Proof.* `f'(x) = psi(x + 1/2) - ln x`. The integral representations of psi
and ln give `psi(x + 1/2) - ln x = int_0^inf e^(-xt) (1/t - 1/(2 sinh(t/2))) dt`.
The integrand is positive because `2 sinh(t/2) > t`. Stirling gives
`f(x) -> 0`. Finally `f(1) = ln(sqrt(pi)/2) + 1 - (1/2) ln(2 pi) = 1 - (3/2) ln 2`.
QED. Both gamma-function inequalities are known (for example in the work of
Elezovic, Giordano and Pecaric, Math. Inequal. Appl. 3 (2000) 239-252, and
Smith-type bounds); the proof is included for completeness.

We also use Robbins' bounds (Amer. Math. Monthly 62 (1955) 26-29):
`sqrt(2 pi n)(n/e)^n <= n! <= sqrt(2 pi n)(n/e)^n e^(1/(12n))`.

### Theorem ST-T272: pathwise sandwich

For every `n >= 1` and every `x in {0,1}^n`:

```text
(1/2) ln(pi n / 2) < rho_n(x) <= (1/2) ln n + ln 2,
n KL(qhat || 1/2) - (1/2) ln n - ln 2 <= ln BF_n(x) < n KL(qhat || 1/2) - (1/2) ln n - (1/2) ln(pi/2).
```

The upper regret bound is an equality only at n = 1. In particular
`ln BF_n <= n KL(qhat || 1/2)` pathwise.

*Proof.* First take `1 <= k <= n-1`. Then
`P_KT = Gamma(k + 1/2) Gamma(n-k+1/2) / (pi n!)`. Lemma G bounds the numerator
above by `2 pi k^k (n-k)^(n-k) e^(-n)`, and Robbins bounds `n!` below. This
gives `P_KT < max_q P_q * sqrt(2/(pi n))`, which is the strict lower bound on
rho. In the other direction, Lemma G with `f(k), f(n-k) >= f(1)` and Robbins'
upper bound give `rho_n <= (1/2) ln(pi n/2) + 3 ln 2 - 2 + 1/(12n)`. For n >= 2
this is at most `(1/2) ln n + 0.347 < (1/2) ln n + ln 2`.

Now take `k = 0`; the case `k = n` is symmetric. Here `max_q P_q = 1` and
`P_KT = Gamma(n + 1/2) / (sqrt(pi) n!)`. Lemma G and Robbins give
`(1/2) ln(pi n) < rho_n <= (1/2) ln(pi n) - f(1) + 1/(12n)`. For n >= 2 this is
at most `(1/2) ln n + 0.654`. For n = 1, `rho_1 = ln 2`. QED.

**Prior art.** The upper regret bound is the classical KT bound (Krichevsky and
Trofimov, IEEE Trans. Inf. Theory 27 (1981) 199-207; Willems, Shtarkov and
Tjalkens, IEEE Trans. Inf. Theory 41 (1995) 653-664), and the pathwise KT upper
bound was already used for ST-T271 ([real-data-checks](real-data-checks.md),
section 4). The interior asymptotic `(1/2) ln(pi n/2)` is the Jeffreys and
Shtarkov value (Xie and Barron, IEEE Trans. Inf. Theory 46 (2000) 431-445), and
two-sided pathwise KT and Jeffreys regret bounds appear in Freund (1996) and Xie
and Barron (2000). We did not find the uniform non-asymptotic lower bound
`rho_n(x) > (1/2) ln(pi n/2)` for every x stated in this form; it may be new,
but it is a small lemma and no priority is claimed. Check: exact rational
verification of `ratio^2 <= 4n` on every count vector with n <= 128, and the
strict lower bound with minimum margin 0.00195.

### Theorem ST-T273: expected sandwich

For every `q in [0,1]` and `n >= 1`:

```text
E_q[ln BF_n] = n KL(q || 1/2) - R_n(q),   R_n(q) = KL(P_q^n || P_KT) >= 0,
E_q[ln BF_n] = n KL(q || 1/2) + E_q[n KL(qhat || q)] - E_q[rho_n],   0 <= E_q[n KL(qhat || q)] <= 1,
n KL(q || 1/2) - (1/2) ln n - ln 2  <=  E_q[ln BF_n]  <=  n KL(q || 1/2) - (1/2) ln n + 1 - (1/2) ln(pi/2).
```

The upper constant `1 - (1/2) ln(pi/2)` is about 0.7742. The lower half is
ST-T271; the upper half is new.

*Proof.* The first line comes from writing `ln BF = ln(P_KT/P_q) + ln(P_q/2^-n)`.
For the second line, `KL(qhat || 1/2) - KL(qhat || q) = ln 2 + qhat ln q +
(1-qhat) ln(1-q)` is affine in qhat, with mean `KL(q || 1/2)`. Next,
`KL <= ln(1 + chi^2) <= chi^2`, and
`E_q[n chi^2(qhat || q)] = n Var(qhat) / (q(1-q)) = 1`; this is checked exactly
in Fractions. The term is 0 at `q in {0,1}`. The third line combines this with
ST-T272. QED.

### Theorem ST-T274: exact constant

For fixed `q in (0,1)`, as `n -> inf`:

```text
E_q[ln BF_n] = n KL(q || 1/2) - (1/2) ln n + (1/2) ln(2e/pi) + o(1),      (1/2) ln(2e/pi) = 0.274209...
```

For `q in {0,1}`, `E_q[ln BF_n] = ln(C(2n,n)/2^n) = n ln 2 - (1/2) ln n -
(1/2) ln pi + o(1)`. The boundary constant is about -0.5724.

The interior constant is the Clarke and Barron expansion (IEEE Trans. Inf.
Theory 36 (1990) 453-471; J. Statist. Plann. Inference 41 (1994) 37-60)
specialized to Bernoulli with the Jeffreys prior: Clarke and Barron give
`R_n(q) = (1/2) ln(n/(2 pi e)) + (1/2) ln I(q) + ln(1/w(q)) + o(1)`, and with
`I(q) = 1/(q(1-q))` and Jeffreys `w`, `(1/2) ln I + ln(1/w) = ln pi`, which gives
the same constant. For memoryless sources the Jeffreys mixture redundancy is
also treated by Xie and Barron (IEEE Trans. Inf. Theory 43 (1997) 646-657), and
the boundary behaviour by Xie and Barron (2000). The boundary constant follows
from Wallis. The proof below is a self-contained re-derivation, not a new
result.

*Proof.* Use the second identity of ST-T273.

(i) Write `Z_n = sqrt(n)(qhat - q)/sqrt(q(1-q))`. A Taylor expansion gives
`n KL(qhat || q) = Z_n^2/2 + O_p(n^(-1/2))`, so it converges in distribution to
`chi^2_1 / 2`. It is dominated by `n chi^2 = Z_n^2`, and `sup_n E Z_n^4 < inf`,
so the family is uniformly integrable. Hence `E_q[n KL(qhat || q)] -> 1/2`.

(ii) For `1 <= k <= n-1`, the proof of ST-T272 gives
`0 <= rho_n(k) - (1/2) ln(pi n/2) <= -f(k) - f(n-k) + 1/(12n)`. This is at most
`-2 f(min(k, n-k)) + 1/(12n)`. Since `f(m) -> 0` and `-f(m) <= -f(1)` for
`m >= 1`, dominated convergence applies, because `min(K, n-K) -> inf` in
probability for interior q. On `{K in {0, n}}`, which has probability at most
`2 max(q, 1-q)^n`, rho is at most `(1/2) ln n + ln 2`. So
`E_q[rho_n] = (1/2) ln(pi n/2) + o(1)`.

Combining (i) and (ii) gives `n KL + 1/2 - (1/2) ln(pi n/2) + o(1)`, which is
the claim. The boundary case is Wallis:
`C(2n,n)/4^n = (pi n)^(-1/2)(1 - 1/(8n) + O(n^-2))`. QED.

### Finite check ST-F53: remainder table

The quantity is `r_n(q) = E_q[ln BF_n] - [n KL(q||1/2) - (1/2) ln n +
(1/2) ln(2e/pi)]`. It is computed by summing over all `k` with 60-digit
Decimals, for `q in {1/10, 1/5, 1/4, 1/3, 2/5, 1/2}` and n up to 5000 (table in
the receipt). At n = 5000, `|r_n| <= 6e-5` on the grid. The ST-T273 sandwich
holds strictly on every entry. One entry was recomputed with 80-digit working
precision (with the 60-digit constants for pi and ln 2) and agreed to better
than 1e-50; this checks accumulated rounding, not the constants.

Beacon scale (q = 1/2, n = 131072): the exact value is
`E[ln BF_n] = -5.617542`. The asymptotic prediction
`-(1/2) ln n + (1/2) ln(2e/pi)` agrees to 9.7e-12. The committed beacon pulses
(n = 131072 bits, k = 65461 ones, both re-derived in the check from the pinned
pulse file) give `ln BF_n = -6.031714`, which reproduces the -6.03 of ST-F52.
It lies inside the ST-T272 pathwise sandwich `[-6.4991, -6.0317]`, close to its
upper end because qhat is near 1/2. The gap between -6.03 and -5.62 is one
realization of the `chi^2_1/2` fluctuation, whose standard deviation is about
0.71.

### Theorem ST-T275: power frontier

Fix `alpha, beta in (0,1)` and define

```text
d_n = sqrt((ln(1/alpha) + (1/2) ln n + ln 2) / (2n)),     e_n = sqrt((ln(1/alpha) + (1/2) ln(pi n/2)) / (4n)),     t_n = sqrt(ln(1/beta) / (2n)).
```

(i) If `|qhat - 1/2| >= d_n`, then `BF_n >= 1/alpha`. (ii) If
`BF_n >= 1/alpha`, then `|qhat - 1/2| >= e_n`. (iii) If
`|q - 1/2| >= d_n + t_n`, then `P_q(BF_n >= 1/alpha) >= 1 - beta`. Under fair
bits, `P(sup_n BF_n >= 1/alpha) <= alpha` (Ville's inequality, as in ST-T08 and
ST-F52), so the test has level alpha.

*Proof.* (i) Combine the lower half of ST-T272 with binary Pinsker,
`KL(p || 1/2) >= 2(p - 1/2)^2`. (ii) Combine the upper half of ST-T272 with
`KL(p || 1/2) <= chi^2(p || 1/2) = 4(p - 1/2)^2`. (iii) Suppose
`q >= 1/2 + d_n + t_n`. If the test fails to reject, then by (i)
`qhat < 1/2 + d_n <= q - t_n`, and one-sided Hoeffding bounds the probability of
that event by `exp(-2 n t_n^2) = beta`. The case `q < 1/2` is symmetric. QED.

For the committed beacon file (alpha = 0.01, beta = 0.05),
`d_n + t_n = 0.006534 + 0.003381 = 0.009914`. This is pinned in the tests:
`d_n^2 in (42686e-9, 42687e-9)` and `d_n + t_n in (0.009914, 0.009915)`.

### Theorem ST-T276: Le Cam converse

Let phi be any randomized test on n IID bits with `E_(1/2) phi <= alpha` and
`E_q phi >= 1 - beta` for one q. Then

```text
|q - 1/2| >= max over the branches whose condition holds of { (1 - alpha - beta)/sqrt(2n),  sqrt(ln(1/(2(alpha+beta))) / (4n)) }.
```

The first branch needs `alpha + beta < 1`; the second needs
`alpha + beta < 1/2`.

*Proof.* Let `delta = q - 1/2`. Then
`KL(P_q^n || P_(1/2)^n) = n KL(q || 1/2) <= n chi^2 = 4 n delta^2`.

- Pinsker branch: `1 - alpha - beta <= E_q phi - E_(1/2) phi <= TV <= sqrt(KL/2) <= delta sqrt(2n)`.
- Bretagnolle-Huber branch: `alpha + beta >= E_(1/2) phi + E_q(1 - phi) >=
  int min(dP_(1/2), dP_q) >= (1/2) exp(-KL) >= (1/2) exp(-4 n delta^2)`.

QED. This is a direct application of the classical Le Cam two-point method
(Le Cam, Ann. Statist. 1 (1973) 38-53) with Pinsker's inequality and the
Bretagnolle-Huber inequality (Z. Wahrsch. verw. Gebiete 47 (1979) 119-137); see
Tsybakov, Introduction to Nonparametric Estimation (2009), Lemma 2.6. It is not
claimed as new. A test that stops by time n is a test on the n bits and is
covered; only tests that may observe more than n bits are not.

### Finite check ST-F54: beacon frontier

**Lemma (power monotonicity).** For the symmetric test `{|K - n/2| >= j}` with
`a = n/2 + j` (so `a - 1 >= n - a`) the derivative of the power in q is
`n C(n-1, a-1) [q^(a-1)(1-q)^(n-a) - q^(n-a)(1-q)^(a-1)] >= 0` for `q >= 1/2`,
and the power is symmetric under `q -> 1 - q`. The one-sided Neyman-Pearson
power is monotone in q by stochastic ordering of Binomial(n, q) (monotone
likelihood ratio, Karlin-Rubin). Hence both powers are monotone in
`|q - 1/2|`, and bisection on a grid of q brackets the crossing of 0.95. The
tests check this monotonicity exactly in Fractions for small n.

These are exact computations at n = 131072, alpha = 1/100, beta = 1/20, on the
grid `q = (65536 + i)/n`. Each bracketing power differs from 0.95 by more than
1e-30. The powers are for the fixed-n test `BF_n >= 1/alpha`; the sequential
ST-F52 test (rejecting if the running supremum crosses 1/alpha) rejects at least
as often, so the KT frontier below is conservative for it.

| bias \|q - 1/2\| | meaning |
|---|---|
| < 0.002011 | ST-T276: no fixed-n level-0.01 test has power >= 0.95 |
| 0.005478 to 0.005486 | the exact randomized Neyman-Pearson test (optimal against each simple alternative) crosses power 0.95 |
| 0.008667 to 0.008675 | the exact KT test crosses power 0.95; it rejects iff `\|k - n/2\| >= 839`, i.e. `\|qhat - 1/2\| >= 0.006401`, between `e_n = 0.004522` and `d_n = 0.006534` |
| >= 0.009914 | ST-T275 closed form: KT power >= 0.95 is guaranteed |

So the "did not reject" result of ST-F52 has explicit content. Any IID biased
simulator with `|q - 1/2| >= 0.0087` would have been caught by the fixed-n KT
test with probability at least 0.95. No fixed-n level-0.01 test on this sample
has power at least 0.95 against one with `|q - 1/2| < 0.002011`. The converse
is of order `1/sqrt(n)` and differs from the KT frontier by a `sqrt(ln n)`
factor plus constants, so it does not match it; the exact fixed-n
Neyman-Pearson frontier 0.00548 is the sharp converse for tests against a
single alternative. Small-n checks (n = 32, 64, 128, 256) confirm the KT power
exactly in Fractions at every grid q beyond `d_n + t_n`, and confirm the
converse against the exact NP power.

### Model result ST-M84: coarsened frontier

Seen through a known BSC(f) with `f in [0, 1/2)`, the observed bits are IID
Bernoulli(q_f) with `q_f - 1/2 = (1 - 2f)(q - 1/2)`. Fair bits stay fair. So
ST-T272 to ST-F54 apply verbatim to q_f. The contraction of the rate,
`KL(q_f || 1/2) <= KL(q || 1/2)`, is ST-M83 (and the contraction coefficient is
ST-M14); this model result extends ST-M83 with two consequences:

- The frontier and the converse in q both scale by `1/(1 - 2f)`. At the
  beacon, f = 1/10 moves them to 0.012393 and 0.002514, and f = 2/5 moves them
  to 0.049570 and 0.010055.
- For f > 0, even `q in {0,1}` maps to an interior q_f, so the interior
  constant (1/2) ln(2e/pi) replaces the boundary constant -(1/2) ln pi.

At f = 1/2 everything is undetectable, which is ST-T01.

## Part II: hypotheses that differ only in weights over shared worlds

### Setting

`M` takes values in a standard Borel space, and a and b are probability laws
on it. A Markov kernel `K(dy | m)` generates the transcript Y in a standard
Borel space. Y may have any length, may be randomly stopped, and may be
adaptive: actions chosen by a policy that does not depend on the hypothesis
label are part of Y, and the policy-plus-world law given M is still a kernel.
Write `P_a^Y = aK` and `P_b^Y = bK`. KL takes values in `[0, +inf]`.

### Theorem ST-T277: persistent cap

```text
KL(aK || bK) <= KL(a || b)                              (data processing; finite only when a << b)
KL(P_a^Y || P_b^Y) <= N KL(a || b)                      (N world draws, any common kernel from (M_1..M_N) to Y)
```

with equality to `sum_u KL(aK_u || bK_u)` when the N units and their
transcripts are independent.

*Proof.* Apply the chain rule for KL on standard Borel spaces to the joint laws
`a x K` and `b x K`. Conditioning on M first gives
`KL(a x K || b x K) = KL(a || b) + E_a KL(K(.|M) || K(.|M)) = KL(a || b)`.
Conditioning on Y first gives
`KL(a x K || b x K) = KL(aK || bK) + E_(aK)[KL(a(.|Y) || b(.|Y))] >= KL(aK || bK)`.
Both identities hold in `[0, +inf]`. For N draws, apply the same argument to
`a^(tensor N)` and `b^(tensor N)` with any common kernel, including cross-unit
adaptive policies; independence gives additivity. QED.

This is the classical data-processing inequality for KL (Csiszar, Studia Sci.
Math. Hungar. 2 (1967) 299-318; Cover and Thomas, Elements of Information
Theory, 2nd ed. (2006), Thm 2.8.1 and Sec. 2.5; Polyanskiy and Wu, Information
Theory (CUP, 2024), data processing and chain rule). It is not claimed as new;
the contribution is its application to world-level mixing weights. The N-unit
data-processing argument is already used in ST-T228, ST-T233 and
[independent-latent-prior-confidence](independent-latent-prior-confidence.md).

Remarks:

- ST-T277 is stated without `a << b` but is trivial when a is not absolutely
  continuous with respect to b: then `KL(a || b) = +inf`. The two sides are not
  infinite together (correction 1 below).
- Since `KL(a || b) = E_a ln(a/b) <= ln max_m (a_m/b_m)`, ST-T277 bounds the
  a-expected log Bayes factor by the mean of the ST-T226 pointwise ceiling.
  ST-T226 controls every transcript; ST-T277 controls only an expectation. The
  ST-T226 support condition (and the PR #69 P1-T4 caveat and audit finding 5)
  remains necessary for any finite ceiling.
- Expected evidence about world-level weights is at most `N KL(a || b)`, so it
  scales with the number N of independent world draws, not with transcript
  length.
- Continuous latent example: Jeffreys versus uniform priors on a coin's bias.
  The cap is `KL(Beta(1/2,1/2) || Beta(1,1)) = ln(4/pi) = 0.2416`, and the exact
  transcript KL climbs to 0.2035 by n = 256.

### Theorem ST-T278: saturation identity

If `KL(a || b) < inf`, then

```text
KL(a || b) - KL(aK || bK) = E_(Y ~ aK)[ KL(a(.|Y) || b(.|Y)) ].
```

Now take M finite with component densities `k_m` with respect to a common
measure mu. Set `r_m = a_m/b_m` and `S_b(y) = {m : b_m k_m(y) > 0}`. The gap is
zero iff, for aK-almost every y, r is constant on `S_b(y)`. In particular:

- "if": if M is a.s. a function of Y under `b x K`, the gap is 0;
- the converse (gap 0 implies M is a.s. a function of Y) is guaranteed when the
  ratios `r_m` are pairwise distinct on `supp(b)`; it fails in general (see the
  counterexamples below).

*Proof.* The identity is the second chain-rule decomposition in ST-T277. With
`a << b` we have `aK << bK`, and the posteriors are `a(m|y) = a_m k_m / p_a`
and `b(m|y) = b_m k_m / p_b`. These are equal for all m iff
`r_m = p_a(y)/p_b(y)` for all m in `S_b(y)`; components with `b_m = 0` have
`a_m = 0`. If M is a function of Y under b, then `|S_b(y)| = 1` for bK-a.e. y,
hence aK-a.e. Conversely, with distinct ratios, constancy forces
`|S_b(y)| <= 1` for aK-a.e. y. To pass to bK-a.e. y (bK need not be
absolutely continuous with respect to aK), consider a bK-positive set on which
`p_a = 0`: there every m in `S_b(y)` has `a_m = 0`, so `r_m = 0`, and pairwise
distinct ratios allow at most one such m. Hence `|S_b(y)| <= 1` bK-a.e., so M
is a function of Y under `b x K`. QED.

The identity is the KL chain rule, and the zero-gap condition specializes the
Kullback-Leibler (Ann. Math. Statist. 22 (1951) 79-86) equality condition for
data processing: equality holds iff Y is sufficient for the pair, i.e. the
density ratio `r_M` is sigma(Y)-measurable. Only the finite-M ratio form is
stated here.

**Example (non-identifying components).** Take `theta = (1/4, 1/4, 3/4)`,
`a = (1/2, 1/3, 1/6)` and `b = (1/6, 1/3, 1/2)`. Components 1 and 2 have the same
law, so the transcript KL never exceeds `KL(merged) = 0.242586`, while
`KL(a || b) = 0.366204`. The gap stays at least `0.123618` for every T. This is
consistent with the zero-gap condition (the gap is positive and M is not a
function of Y); what it shows is that "gap -> 0 as T -> inf" needs
distinguishable component laws, the distinctness hypothesis of ST-T279.

**Counterexamples to "gap = 0 only if M is a function of Y".** (1) Take
`a = (1/4, 1/4, 1/2)`, `b = (1/8, 1/8, 3/4)`, components 1 and 2 with the common
law `(1/2, 1/2, 0)` on a ternary alphabet and component 3 with law `(0, 0, 1)`.
Then `r_1 = r_2 = 2` and `KL_T = KL(a || b) = 0.143841` for T = 1, 3 and 6, so
the gap is 0, yet M is not a function of Y. (2) Deterministic components
`theta = (0, 1, 1)`, `a = (1/2, 1/4, 1/4)`, `b = (1/4, 3/8, 3/8)` give the same
value at T = 1 and T = 4. The trivial case `a = b` with overlapping components
also works. Both are verified exactly in the receipt.

### Theorem ST-T279: gap bound

Let M be finite with `a << b`. Let `S = supp(a)`, `Z = supp(b) \ S`, and
`R = max_(m, m' in S) r_m / r_m'`. Let `P_a(err) = E_(aK)[1 - max_m a(m|Y)]`
be the Bayes error of the MAP rule under prior a. Then, for any choice of
`s_(m m') in (0, 1]` (chosen separately for each pair),

```text
gap <= (R - 1) P_a(err) + sum_(m in S, m' in Z) (a_m / s_(m m')) (b_m' / b_m)^(s_(m m')) rho_(s_(m m'))(K_m, K_m'),
rho_s(P, Q) = int p^(1-s) q^s dmu.
```

When `supp(a) = supp(b)` the mismatch sum vanishes and the bound is
`(R - 1) P_a(err)`. For conditionally IID transcripts of length T,
`rho_s(K_m, K_m') = rho_s(k_m, k_m')^T` and
`P_a(err) <= sum_(m < m' in S) a_m^(1-s) a_m'^s rho_s(k_m, k_m')^T`, with s
chosen separately for each pair. Hence

```text
limsup_T (1/T) ln gap_T <= - min over relevant pairs of C(k_m, k_m'),     C(P, Q) = sup_(s in (0,1)) [-ln rho_s(P, Q)].
```

The relevant pairs are pairs within S when R > 1, and the pairs in S x Z. So
the gap decays at least as fast as `exp(-T min C + o(T))` whenever all
relevant pairs have distinct laws. The rate is an upper bound on the exponent
and is not shown to be tight.

*Proof.* Fix y and write alpha, beta for the a- and b-posteriors, and `p_b^S`,
`p_b^Z` for the b-mixture densities restricted to S and Z. Since
`alpha_m / beta_m = r_m p_b / p_a` and `p_b^S / p_a = E_alpha[1/r]`,

```text
KL(alpha || beta) = { E_alpha ln r + ln E_alpha[1/r] } + ln(1 + p_b^Z / p_b^S).
```

Let `m0 = argmax alpha` and `eps = 1 - alpha_(m0)`. Then
`E_alpha ln r - ln r_(m0) <= eps ln(r_max / r_(m0))` and
`ln(r_(m0) E_alpha[1/r]) <= ln(1 - eps + eps r_(m0)/r_min) <= eps(r_(m0)/r_min - 1)`.
Their sum is convex in `r_(m0)`, so it is at most
`eps max(ln R, R - 1) = eps (R - 1)`. Taking the aK-expectation of eps gives
`P_a(err)`.

For the last term, use `p_a = sum_(m in S) a_m k_m`, `p_b^S >= b_m k_m`,
`ln(1 + sum_j x_j) <= sum_j ln(1 + x_j)` and `ln(1 + x) <= x^s / s` for
`s in (0,1]`. This gives the stated sum after integration. The MAP error bound
uses `1 - max alpha <= sum over pairs of min(a_m k_m, a_m' k_m') / p_a` and
`min(u, v) <= u^(1-s) v^s`. QED.

The multi-hypothesis MAP-error Chernoff exponent is classical (Chernoff, Ann.
Math. Statist. 23 (1952) 493-507; Leang and Johnson, IEEE Trans. Inf. Theory
43 (1997) 280-282); only the `(R - 1)` factor and the support-mismatch term are
new here.

### Theorem ST-T280: kernel decomposition

If the hypotheses use different kernels `K^a` and `K^b`, then

```text
KL(aK^a || bK^b) <= KL(a || b) + int KL(K^a(.|m) || K^b(.|m)) a(dm).
```

When `KL(a || b) + E_a KL(K^a || K^b) < inf`, the difference between the two
sides is `E_(aK^a)[KL(a(.|Y) || b(.|Y))]`, where the posteriors are computed
with each hypothesis's own kernel. For conditionally IID transcripts the second
term is `T sum_m a_m KL(k^a_m || k^b_m)`, which is linear in T. Only the first
term is world-level.

*Proof.* The same two chain-rule decompositions of `KL(a x K^a || b x K^b)` as
in ST-T277. QED. This is the chain rule plus data processing and is standard.

In the example `theta^a = (1/3, 2/3)`, `theta^b = (2/5, 3/5)`, the transcript KL
passes the world-level cap 0.5493 by T = 64. At T = 256 it is 2.9727, within
1e-6 of the bound. This complements the ST-T226 scope nonclaim (the ceiling
concerns mixing weights, not component distinguishability) by showing that the
excess over `KL(a || b)` is at most the within-component divergence
`E_a KL(K^a || K^b)`, less a posterior-disagreement term. No matching lower
bound is claimed.

### Finite check ST-F55: persistent audit

The audit uses exact Fraction laws over sufficient count vectors and 60-digit
logarithms. It covers binary, ternary, support-mismatch, ternary-emission and
non-identifying latent examples up to T = 64 (T = 32 for ternary emissions),
and the two counterexamples above. For each, it asserts:

- monotonicity in T and `KL_T <= KL(a || b)`;
- the ST-T278 identity, against an independent computation of
  `E_a KL(posteriors)`, to within 1e-30;
- the ST-T279 bound, and its Bhattacharyya relaxation.

The support-mismatch example has R = 1, so only the mismatch term is active,
and the gap decreases 0.3041 -> 0.1683 -> 0.0239 at T = 4, 16, 64. The audit
also checks that two independent world draws give exactly twice the
single-draw KL.

**Corrections to the original direction sketch (negative findings).**

1. The sketch said that "both sides are +infinity together when a is not << b".
   That is false. Take `a = (1/2, 1/2)`, `b = (1, 0)` and identical component
   laws. Then `KL(a || b) = +inf` while the transcript KL is 0 for every T. Only
   one implication holds: transcript KL infinite implies `KL(a || b)` infinite.
2. The sketch said the gap "is zero iff M is a.s. a function of Y". That is
   false in general; the counterexamples are recorded above and the correct
   statement is ST-T278.
3. The sketch's upper bound `E_q[ln BF_n] <= n KL(q || 1/2) + 1` is valid but
   weak. The exact identity `E_q[ln BF_n] = n KL(q || 1/2) - R_n(q)`, with
   `R_n >= 0`, already gives `<= n KL`. ST-T273 improves this to
   `n KL - (1/2) ln n + 0.7742`.
4. The sketch value 0.180 at T = 4 is 0.1794 (rounding slip). The values
   0.056, 0.409 and 0.544 reproduce for `theta = (1/3, 2/3)`, `a = (3/4, 1/4)`,
   `b = (1/4, 3/4)`.

## Open problem ST-O02: second-order term

The table suggests `r_n(q) = (1 - 2q)^2 / (24 n q(1-q)) + O(1/n^2)` for interior
q. At n = 5000, `n r_n` is 0.2970, 0.0939, 0.0557, 0.0209 and 0.0070 at q = 1/10,
1/5, 1/4, 1/3 and 2/5; the conjectured values are 0.2963, 0.0938, 0.0556, 0.0208
and 0.0069.

**Formal derivation.** With `s = q(1-q)`, a second-order moment expansion (from
`E delta^3 = s(1-2q)/n^2` and `E delta^4 = 3 s^2/n^2 + O(n^-3)`, the
Williams-type correction; cf. Williams, Biometrika 63 (1976) 33-37) gives
`E[n KL(qhat || q)] = 1/2 + (1 - s)/(12 s n) + O(n^-2)`. From
`f(x) = -1/(24x) + O(x^-3)` and Stirling, `E[rho_n] = (1/2) ln(pi n/2) +
1/(24 s n) + 1/(12 n) + O(n^-2)`. Hence
`r_n = (1-2q)^2/(24 q(1-q) n) + O(n^-2)`, which vanishes at q = 1/2, consistent
with the remainder 9.7e-12 at n = 131072 there. A reviewer's independent
45-digit computation (not part of the receipt) gave `n(n r_n - conj) = 3.768`
at n = 5000 and 3.758 at n = 20000 for q = 1/10, and 0.2815 versus 0.2813 for
q = 1/3, consistent with an `O(n^-2)` remainder.

The claim stays an open problem: the derivation is formal, and the dominated
remainder bounds (which would follow the ST-T274 proof pattern) are not
written.

## Assumptions

Part I assumes IID bits under each hypothesis given the world, a fair base
law, and the KT (Jeffreys) composite alternative declared in advance. Part II
assumes:

- standard Borel spaces;
- a hypothesis-independent experimenter policy;
- a common kernel, except in ST-T280;
- a finite latent set for the ST-T278 characterization and for ST-T279.

## Nonclaims

- Nothing here is evidence for or against simulation. A simulator that
  reproduces the base law exactly is invisible (ST-T01).
- ST-T274 is pointwise in q, not uniform near the boundary. ST-O02 is not
  proved.
- The frontier numbers of ST-F54 concern IID biased simulators only. They are
  not a randomness certification of the NIST beacon.
- ST-T277 bounds the expected log Bayes factor about world-level weights. It
  does not limit learning which world is active, and does not bound a single
  transcript's Bayes factor beyond ST-T226.
- The ST-T279 rate is an upper bound on the gap's exponent and is not shown to
  be tight.

## Relation to existing claims

- **ST-T01** (unrestricted indistinguishability): the zero-signal endpoint.
  ST-T273 and ST-T274 give `-(1/2) ln n + 0.274` at q = 1/2, and ST-M84 gives
  f = 1/2.
- **ST-T08** (Bernoulli e-process) and **ST-F52** (NIST beacon Ville check):
  ST-T275 uses the same Ville validity for the KT mixture, and ST-F54 turns the
  ST-F52 "did not reject" into an explicit fixed-n power frontier with a
  converse of the right order.
- **ST-T06** (Fano identification): ST-T279 is a Chernoff-rate complement for
  persistent latents.
- **ST-T271** (composite Bayes-factor detection rate): its lower bound
  `n KL - (1/2) ln n - ln 2` is the lower half of ST-T273; ST-T272 adds the
  uniform pathwise lower regret bound, ST-T273 the expected upper bound, and
  ST-T274 the exact constant. The pathwise upper bound is the classical KT
  bound already used there.
- **ST-M14 and ST-M83**: ST-M84 extends the frontier and the constant to the
  coarsened source; the rate contraction itself is ST-M83.
- **PR #56 (ST-T225 to ST-T228, ST-M66, ST-M67)**:
  - ST-T277 is the KL (expected) form of ST-T226;
  - ST-T278 and ST-T279 quantify the ST-T227 saturation;
  - the N-unit statement of ST-T277 is the KL form of ST-T228;
  - ST-T280 complements the ST-T226 scope nonclaim about component
    distinguishability.
- **PR #57** (independent latent draws, ST-T233): expected evidence about
  world-level weights is at most `N KL(a || b)`, so it scales with the number of
  independent world draws.
- **PR #69 P1-T4 nonclaims and PR #68 audit finding 5**: ST-T277 holds without a
  support assumption but is vacuous (`+inf`) precisely when a is not << b; the
  support condition remains necessary for any finite ceiling.
