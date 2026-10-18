# CHSH escape routes as exact resource frontiers, tested anytime-validly on Delft 2015

Claims ST-T281 to ST-T285, ST-M85, ST-F56 and ST-O03
([manifest](../claims/bell-escape-route-frontier-claims.json)). Certificate:
`src/simtheory/bell_escape_routes.py`, receipt
[`receipts/bell-escape-route-frontiers.txt`](../receipts/bell-escape-route-frontiers.txt),
tests in `tests/test_bell_escape_route_frontiers.py`.

## Status

This page collects standard and cited results, re-certified exactly, plus one
negative finite check on real data.

- The frontiers for one-way signalling (silence free, and with an
  x-independent send flag), for measurement dependence and for detection
  efficiency are known or near-known. Frontier (b) reproduces Pironio (2003),
  frontier (d) reproduces Puetz et al. (2014), and the detection threshold (e)
  is Garg and Mermin (1987). The contribution is an exact, replayable
  certificate package (Fractions and exact Q(sqrt 2) arithmetic) with explicit
  attaining models.
- The betting test (ST-T281) is the conditional-null form of ST-T08 and is
  standard; the statistical-strength value at full visibility (ST-T284) is the
  van Dam, Gill and Gruenwald (2005) value; the growth ceiling and sample-size
  floor (ST-T285) are Kelly's and Wald's bounds.
- **Negative finite check (ST-F56).** At alpha = 0.05, no mixture of constant
  bets on the CHSH win indicator, at any prefix and any f >= 3/4, constrains the
  signalling routes (a), (b) or the measurement-dependence route (d) on the
  Delft 2015 data. Detection (e) is not tested: the Delft experiment is
  event-ready. The default uniform mixture gives an anytime-valid p of about
  0.36 against the plain local null. Tested predictable plug-in bets also stay
  far below 20 (running suprema 1.65 and 1.90 in the receipt; reviewers'
  explorations of other adaptive bets reached between 2.09 and 4.47); this is
  supporting evidence, not a proof for adaptive bets.

## Conventions

CHSH game: settings x, y in {0,1}, output bits a, b in {0,1}, win iff
a XOR b = x AND y. Let `E_xy = P(a = b | x,y) - P(a != b | x,y)` be the
correlator and `s = (+,+,+,-)`. Then `s_xy E_xy = 2 P(win | x,y) - 1`, and the
CHSH value is

    S = sum_xy s_xy E_xy = 8 wbar - 4,   wbar = (1/4) sum_xy P(win | x,y).          (0)

This is an identity. Under uniform settings, wbar is the per-trial win
probability. d(p || q) is the binary KL divergence.

The Delft file uses columns (timestamp, a, b, x, y), with a, b the settings and
x, y in {-1,+1} the outcomes. A trial is a win iff (-1)^(ab) x y = +1, which
is the same game.

## The unifying null

A resource level r indexes a class of classical simulators, and f(r) in (0,1)
is a number. The relaxed null H(f) states that for every trial i,

    P(W_i = 1 | F_{i-1}) <= f      almost surely,

where W_i is the CHSH win indicator and F_{i-1} holds everything that
happened before trial i. The frontier theorems supply f(r) for each escape
route. Each f(r) is valid conditionally on the past when the resource
constraint holds per trial, conditionally on the past. Each escape-route
model class is strictly smaller than H(f(r)), so tests that are valid only for
the smaller class can be more powerful than the tests treated here.

## Theorem ST-T281: anytime-valid test for every resource level

**Statement.** Fix f in (0,1) and q in [f,1]. Define the betting factor
e(q, 1) = q/f and e(q, 0) = (1-q)/(1-f). Under H(f):

1. E[e(q, W_i) | F_{i-1}] = 1 + (p_i - f)(q - f)/(f(1-f)) <= 1, where
   p_i = P(W_i = 1 | F_{i-1}).
2. For any probability measure pi on [f,1] that does not depend on the data,
   E_n = integral prod_{i<=n} e(q, W_i) pi(dq) is a nonnegative
   supermartingale with E_0 = 1. The same holds for predictable bets
   q_i in [f,1].
3. (Ville) P(sup_n E_n >= 1/alpha) <= alpha. So p = 1/sup_n E_n is an
   anytime-valid p-value. For a family r -> f(r), the set
   C_alpha = {r : sup_n E_n^{(r)} < 1/alpha} has P(r* not in C_alpha) <= alpha
   whenever the data satisfy H(f(r*)). When f is nondecreasing in r,
   inf C_alpha is an anytime-valid lower confidence bound for r*.
4. For the uniform mixture pi = Uniform[f,1], with n = k + m, k wins, m
   losses, and f = N/D in lowest terms,

        E_n = k! m! S / ((n+1)! N^k (D-N)^(m+1)),
        S = sum_{j=0}^{k} C(n+1, j) N^j (D-N)^(n+1-j).

**Proof.** (1) The conditional mean is p_i q/f + (1-p_i)(1-q)/(1-f). It is
affine in p_i, equals 1 at p_i = f, and has slope
q/f - (1-q)/(1-f) = (q-f)/(f(1-f)) >= 0. So for p_i <= f it is at most 1.
(2) Each product M_n(q) is a nonnegative supermartingale by (1). By
conditional Tonelli, the mixture is a nonnegative supermartingale too. The
same holds for predictable q_i, since (1) holds pointwise in q.
(3) Ville's maximal inequality for nonnegative supermartingales. The coverage
statement applies (3) to the single hypothesis H(f(r*)); C_alpha does not need
f to be monotone. (4) Since 1/(1-f) is the uniform density,
E_n = int_f^1 q^k (1-q)^m dq / (f^k (1-f)^(m+1)). The incomplete-beta
identity int_0^f q^k (1-q)^m dq = B(k+1, m+1) P(Bin(n+1, f) >= k+1) gives
int_f^1 = (k! m!/(n+1)!) P(Bin(n+1, f) <= k). Substituting f = N/D cancels
D^(n+1). QED.

**Prior art.** The one-step multiplier identity, Ville validity and closure
under mixtures are already in ST-T08
([formal-results](formal-results.md#anytime-valid-restricted-signature-tests)).
The conditional-null extension is a one-line tower argument. Test
supermartingales for Bell tests are standard (Gill, quant-ph/0301059 (2003)
and Statist. Sci. 29 (2014) 512-528; Zhang, Glancy and Knill, Phys. Rev. A 84,
062118 (2011)); the supplement of Hensen et al., Nature 526, 682 (2015) already
uses a martingale bound. The beta-mixture closed form and its inversion into a
confidence set are also standard (Robbins, Ann. Math. Statist. 41 (1970)
1397-1409; Shafer, Shen, Vereshchagin and Vovk, Statist. Sci. 26 (2011) 84-101;
Howard, Ramdas, McAuliffe and Sekhon, Ann. Statist. 49 (2021) 1055-1080;
Waudby-Smith and Ramdas, J. R. Stat. Soc. B 86 (2024) 1-27). New here is only the
exact rational closed form used by the check.

**Check.** The affine identity is verified exactly on a rational grid of
(f, q, p). The closed form agrees exactly with a separate term-by-term
antiderivative expansion for k, m <= 8 and three values of f. An exact
lattice dynamic program gives P(max_{n<=40} E_n >= 4) = 0.1541 <= 1/4 under
IID Bernoulli(3/4).

## Exact frontiers

Unless stated otherwise, settings are uniform and independent of the shared
randomness lambda and of the past. Private randomness is folded into lambda,
so every strategy is a mixture over lambda of deterministic strategies. The
cost and the win probability are both linear in the mixture. A linear
inequality that holds for every deterministic strategy therefore holds for
all strategies. This is the dual certificate.

### Theorem ST-T282: one-way signalling frontiers

**(a) Silence free.** Alice outputs a = A(x, lambda) and sends M(x, lambda) in
an alphabet that contains a designated silent symbol N. Bob outputs
B(y, M, lambda). The cost is c = P(M != N), the expected non-silent rate. Then

    P(win) <= 3/4 + c/2  on [0, 1/2],   P(win) <= 1 on [1/2, 1],   so S <= 2 + 4c.

*Proof.* Fix lambda. If M(., lambda) = N for both x, Bob's output does not
depend on x and the strategy is local, so it wins at most 3 of the 4 pairs
(see ST-T283). Its cost is 0. Otherwise its cost is at least 1/2, and
win <= 1 <= 3/4 + (1/2)/2. In both cases w_lambda <= 3/4 + c_lambda/2.
Average over lambda. *Attainment:* with probability 2c, Alice sends one bit
only when x = 1 (cost 1/2). Silence then tells Bob x = 0, so Bob knows x and
outputs A(x) XOR xy, which always wins. With probability 1 - 2c, play an
optimal local strategy. The cost is c and the win probability is 3/4 + c/2.
*Finite check:* for the ternary alphabet, all 2304 deterministic strategies
are enumerated. The upper concave hull of the (cost, win) points has vertices
(0, 3/4), (1/2, 1), (1, 1). The dual inequality win - c/2 <= 3/4 holds for all
2304 and is tight at 128 cost-0 strategies and 64 cost-1/2 strategies. The
argument above covers any alphabet; as a check, all 16384 strategies with a
4-symbol alphabet also satisfy win - c/2 <= 3/4 with equality attained.

**(b) Send flag independent of x.** Here the decision to communicate is a
function F(lambda) and cannot depend on x. When F = 1, Alice sends any
message. The cost is c = P(F = 1). Then

    P(win) <= 3/4 + c/4,   S <= 2 + 2c,

and the bound is attained. *Proof.* Given F = 0 the strategy is local and
wins with probability at most 3/4. Given F = 1 it wins with probability at
most 1, and sending x attains 1. *Finite check:* 272 deterministic flag
strategies have hull (0, 3/4), (1, 1), and the dual win - c/4 <= 3/4 holds for
all of them.

The gap between (a) and (b) is the information carried by the timing of
silence. In (a), an expected non-silent rate of 1/2 buys a perfect win,
because silence itself reveals x (at c = 1/2 the protocol transmits one full
bit of information about x through the silence pattern).

**(c) One bit always suffices.** If Alice always sends x (one bit, cost 1 in
either accounting), every binary-input behaviour p(a,b | x,y) whose Alice
marginal does not depend on y is reproduced exactly. Alice draws
a ~ p(a | x) from lambda, and Bob, knowing x, y and a, draws
b ~ p(b | a, x, y). This includes the PR box (win 1) and the Tsirelson law;
the check confirms that Alice's marginal is 1/2 free of y and that Bob's
conditionals are nonnegative in Q(sqrt 2). With zero bits, the maximum win
probability is 3/4. One bit is therefore the exact worst-case (fixed-length,
number of bits always sent) one-way communication cost of every nonlocal
binary-input behaviour whose Alice marginal does not depend on y. Under the
expected-non-silent accounting of (a), cost 1/2 already suffices for every such
behaviour and is necessary for the PR box; under the accounting of (b), cost 1
is necessary for the PR box, matching Pironio (2003).

**Prior art.** Frontier (b), S <= 2 + 2c, is exactly Pironio's CHSH bound:
average communication at least B/2 - 1 = (S-2)/2, so sqrt2 - 1 = 0.4142 bits is
necessary and sufficient for the Tsirelson correlations (Pironio, Phys. Rev. A
68, 062102 (2003), Prop. 1). Frontier (a) is the same game under an accounting
in which silence is free and informative; its frontier S <= 2 + 4c is at most a
modest variant, and although we found no explicit statement we treat it as
possibly known. Variable-length protocols in which not sending is free were
used by Maudlin (PSA 1992) and Steiner (Phys. Lett. A 270, 239 (2000));
Brassard, Cleve and Tapp (Phys. Rev. Lett. 83, 1874 (1999)) use worst-case
cost. Toner and Bacon (Phys. Rev. Lett. 91, 187904 (2003)) show that one bit
suffices for continuous settings; Bacon and Toner (Phys. Rev. Lett. 90, 157904
(2003)) treat Bell inequalities with auxiliary communication; (c) is a
trivial finite analogue. Related relaxation frameworks: Maxwell and Chitambar,
Phys. Rev. A 89, 042108 (2014); Chaves, Kueng, Brask and Gross, Phys. Rev.
Lett. 114, 140403 (2015); Brask and Chaves, J. Phys. A 50, 094001 (2017); and
Hall's relaxed CHSH bounds for signalling, Phys. Rev. A 82, 062117 (2010).

### Theorem ST-T283: measurement-dependence frontier (Puetz et al.)

Outputs are local: a = A(x, lambda), b = B(y, lambda). The setting law may
depend on lambda, subject to p(x, y | lambda) >= l for all x, y, lambda, with
l in [0, 1/4]. Then

    P(win) <= 1 - l,

with equality attained by a model whose observed setting marginal is uniform.
For uniform observed marginals, (0) gives S <= 4 - 8l. (Without uniform
observed settings the S form can fail; the win form does not.)

*Proof.* Every deterministic local strategy loses on at least one setting
pair. The parity sum_xy [A(x) XOR B(y) XOR xy] equals
(sum of the a-b terms, which is even) + 1, so it is odd. (Exactly 8 of the 16
strategies lose one pair and 8 lose three.) If (x0, y0) is a losing pair of
the strategy at lambda, then
P(win | lambda) <= 1 - p(x0, y0 | lambda) <= 1 - l. Averaging gives the
bound. In LP form: with multiplier 1 on the constraint
mu(D, x0 y0) >= l mu(D, .), the per-strategy coefficients become
win(D, xy) - 1 + [xy = x0 y0] <= 0. This is checked for all 16 strategies.
*Attainment:* let lambda be uniform over four strategies s_j, where s_j loses
only on pair j. Given s_j, put mass l on pair j and (1-l)/3 on each other
pair. Each pair then receives (1/4)(l + 3 (1-l)/3) = 1/4, so the observed
settings are uniform. The win probability is 1 - l, and p(xy | lambda) >= l
holds iff l <= 1/4. Every quantity is affine in l, so the exact checks at
l = 0 and l = 1/4 cover the interval.

*Corollary (connection to the Delft xi).* Suppose each setting bit has
conditional bias at most tau given lambda and the other bit. Then
p(xy | lambda) >= (1/2 - tau)^2, so the local win bound becomes
1 - (1/2 - tau)^2 = 3/4 + tau - tau^2, which is at most
xi = 3/4 + 3(tau + tau^2). Under this extra bias assumption the paper's xi is
conservative. This corollary does not replace the paper's own derivation.

**Prior art.** The bound win <= 1 - l (S <= 4 - 8l under uniform observed
settings) is stated in Puetz, Rosset, Barnea, Liang and Gisin, Phys. Rev.
Lett. 113, 190402 (2014): their vertex analysis gives CHSH max 1 - 2l' with
l' = max(1 - 3h, l), which with h unconstrained is S = 4(1 - 2l). See also
Puetz and Gisin, New J. Phys. 18, 055006 (2016); Hall, Phys. Rev. Lett. 105,
250404 (2010) and Phys. Rev. A 84, 022102 (2011), for other dependence
measures; and Koh et al., Phys. Rev. Lett. 109, 160404 (2012), for setting bias.
New here: the exact 16-strategy dual certificate and the explicit attaining
model with uniform observed settings.

### Model result ST-M85: exact certificate of the Garg-Mermin detection threshold

Consider the behaviour with outcomes {+1, -1, no-click}. Coincidences follow
the Tsirelson law, with E_xy = s_xy / sqrt 2 and uniform marginals. Each side
clicks independently with efficiency eta, independently of settings and
outcomes. This behaviour has a local model iff

    eta <= eta* = 2/(1 + sqrt 2) = 2 sqrt 2 - 2 ~ 0.8284.

*Only if.* The CH functional
P(++|00) + P(++|01) + P(++|10) - P(++|11) - P_A(+|0) - P_B(+|0)
is at most 0 on all 81 deterministic three-outcome local strategies (checked
exhaustively), so it is at most 0 for every local model. On the behaviour it
equals eta^2 (1 + sqrt 2)/2 - eta, which is exact in Q(sqrt 2) and positive iff
eta > eta*. *If.* `DETECTION_MODEL` is an explicit local model at eta* with 17
deterministic strategies. Eight full-click CHSH strategies have weight
eta*^2 (2 - sqrt 2)/8 each, eight one-sided-no-click strategies have weight
eta* (1 - eta*)/2 each, and the all-no-click strategy has weight
(1 - eta*)^2. The model reproduces all 36 entries exactly in Q(sqrt 2), with
exact positivity. (The support was found by a simplex solve; the certificate
is the exact identity and does not depend on that solve.) For eta < eta*,
each side independently relabels a click as no-click with probability
1 - eta/eta*. This local post-processing maps the eta* behaviour to the eta
behaviour, as one can check entry by entry: for example,
P(no-click, no-click) becomes ((1-eta*) + eta*(1 - eta/eta*))^2 = (1-eta)^2.
Coincidences conditioned on two clicks then show S = 2 sqrt 2 although the
model is local.

**Prior art.** The threshold and the tightness of a local model are Garg and
Mermin, Phys. Rev. D 35, 3831 (1987), and Larsson, Phys. Rev. A 57, 3304
(1998). Eberhard, Phys. Rev. A 47, R747 (1993), treats non-maximally entangled
states, which are not covered here. This concerns one fixed behaviour, so it
is typed as a model result.

### Theorem ST-T284: optimal per-trial exponent under uniform settings

**Statement.** For v in [0,1], let P_v be the law of (x, y, a, b) with uniform
settings and p(ab | xy) = (1 + (-1)^(a XOR b XOR xy) v/sqrt 2)/4, so that
P(win | xy) = w_v = (1 + v/sqrt 2)/2. A local law with uniform settings is
L(x,y,a,b) = (1/4) sum_lambda pi(lambda) [a = A_lambda(x)][b = B_lambda(y)],
so the settings are uniform and independent of lambda. Over all such L,

    min_L D(P_v || L) = d(w_v || 3/4)  if v >= 1/sqrt 2,   and 0 otherwise.

At v = 1 this equals d(cos^2(pi/8) || 3/4) = 0.032074586 nats
= 0.046273847 bits.

**Proof.** *Lower bound:* the win indicator is a deterministic function of
(x, y, a, b), so data processing gives D(P_v || L) >= d(w_v || L(win)). Every
such L has L(win) <= 3/4 by ST-T283 with l = 1/4. For u <= 3/4 <= w_v,
d(w_v || u) is nonincreasing in u, because d/du d(w||u) = (u - w)/(u(1-u)) <= 0.
Hence D >= d(w_v || 3/4). *Attainment:* L* is the uniform mixture of the 8
strategies that lose exactly one pair. On each pair it wins with probability
3/4, uniformly across the two winning output pairs and across the two losing
ones (checked exactly in Fractions). Both P_v and L* are uniform within the win
and loss classes, so D(P_v || L*) = d(w_v || 3/4) exactly. For
v <= 1/sqrt 2, P_v = t L* + (1 - t) U with t = v sqrt 2 and U the uniform local
box, so P_v is local and the minimum is 0. QED. A seeded search over 3000
random local mixtures stayed above the bound, as a sanity check only. The
logarithmic constants are floats checked with tolerance 1e-14; a reviewer's
50-digit Decimal recomputation agrees (0.0320745864801 nats =
0.0462738468534 bits).

**Prior art.** The v = 1 value is the van Dam, Gill and Gruenwald uniform-setting
CHSH statistical strength (IEEE Trans. Inf. Theory 51 (2005) 2812-2835); Acin,
Gill and Gisin, Phys. Rev. Lett. 95, 210402 (2005), treat related KL strengths.
Only the v-family and the data-processing proof are new.

### Theorem ST-T285: growth ceiling and sample-size floor (standard)

**(a) Ceiling.** Let Q = Bernoulli(f)^n, which belongs to H(f), and
P = Bernoulli(p)^n with p, f in (0,1). For every nonnegative E(W_1..W_n) with
E_Q[E] <= 1,

    E_P[log E] <= n d(p || f).

*Proof.* E_P[log E] - D(P||Q) = E_P[log(E dQ/dP)]
<= log E_P[E dQ/dP] = log E_Q[E] <= 0 by Jensen.

**(b) Expected-sample-size floor.** Let E_n be an e-process on the win
filtration that is a supermartingale under Bernoulli(f)^infinity. Let
tau = inf{n : E_n >= 1/alpha}, and suppose that under P = Bernoulli(p)^infinity
we have P(tau < infinity) = 1 and E_P[tau] < infinity. Then

    E_P[tau] >= ln(1/alpha) / d(p || f).

*Proof.* Let LR_n = prod (p/f)^{W_i} ((1-p)/(1-f))^{1-W_i}. On {tau = n},
dP/dQ = LR_n. So E_P[E_tau / LR_tau] = E_Q[E_tau ; tau < infinity] <= 1, by
optional stopping and Fatou for the nonnegative Q-supermartingale. Jensen
gives E_P[log E_tau] <= E_P[log LR_tau], and Wald's identity (bounded
increments) gives E_P[log LR_tau] = E_P[tau] d(p||f). Finally
E_P[log E_tau] >= ln(1/alpha). QED.

The same floor holds for e-processes on the full data (settings and outcomes)
against the local null with f = 3/4 when the truth is IID P_v: replace Q by
(L*)^infinity and use ST-T284, which gives D(P_v || L*) = d(w_v || 3/4). At
uniform settings, betting on the win indicator therefore loses nothing in the
growth rate against the isotropic law. This extension is proved only at
f = 3/4, not at f = xi.

**Prior art.** Both inequalities are classical: (a) is the Kelly/GROW
log-optimality bound (Kelly, Bell Syst. Tech. J. 35 (1956) 917-926; Shafer,
J. R. Stat. Soc. A 184 (2021) 407-431; Gruenwald, de Heide and Koolen, J. R.
Stat. Soc. B 86 (2024) 1091-1128) and (b) is Wald's lower bound on expected
sample size (Wald, Ann. Math. Statist. 16 (1945) 117-186; Hoeffding, Ann.
Math. Statist. 31 (1960) 352-368). The full-data remark specializes Zhang,
Glancy and Knill (2011): the optimal asymptotic test-factor growth rate equals
the minimum KL to the local set. New here are only the CHSH and Delft numbers.
ST-T02 (a pointwise likelihood-ratio ceiling) and ST-T10 (the fixed-design
adaptive KL bound) are related but different.

Numbers at alpha = 0.05 and f = xi: at the Tsirelson rate,
E[tau] >= ln 20 / d(cos^2(pi/8) || xi) = 93.5 trials. If the per-trial win rate
were 0.8 IID (the Delft empirical rate 196/245), any power-one e-process on the
win indicator at 5% would need at least 428.4 trials in expectation. This is a
heuristic comparison with n = 245, not a pathwise impossibility: a single run
can stop earlier than its expectation, and 0.8 is a point estimate.

## Finite check ST-F56: Delft 2015 (negative)

Data: the 245 committed valid trials of ST-F50
(`data/real/delft2015-bell-trials.json`, trial digest `ca9dd147...5bda5f`
pinned in code), in timestamp order (verified), with k = 196 wins. The bound
is xi = 3/4 + 3(tau + tau^2), with tau = 27/2500000, so
xi = 4687702502187/6250000000000. All e-values below are exact rationals, and
the reported intervals are exact rational brackets.

| quantity | f = 3/4 | f = xi |
| --- | --- | --- |
| uniform-mixture E_245 | 1.369782 | 1.366934 (in [1.3669, 1.3670]) |
| running sup_n E_n (attained at n = 6, six straight wins) | 2.782089 | 2.781599 (in [2.7815, 2.7817]) |
| anytime-valid p = 1 / sup_n E_n | 0.359 | 0.360 |
| fixed bet q = 17/20: E_245 / running sup | 0.607 / 2.119 | 0.606 / 2.119 |
| hindsight best constant bet at n = 245: 245 d(0.8 \|\| f) | 1.715516 nats (e^ = 5.5595) | 1.713400 nats (e^ = 5.5478) |

The uniform mixture is a default, data-independent choice made after the data
were public, without tuning; it was not preregistered. The p = 0.36 is the
value for this one default mixture and is illustrative. The negative
conclusion does not depend on that choice, because it rests on the realised
ceiling below, which holds uniformly over all constant-bet mixtures.

For comparison, the fixed-n binomial tail of ST-F50 is
P(Bin(245, xi) >= 196) = 0.039175 (1/p = 25.53); against 3/4 it is 0.039078. The
published 0.039 of Hensen et al. is itself martingale-based (Elkouss and Wehner,
npj Quantum Inf. 2, 16026 (2016)) and is valid against memory-ful local models
for a fixed n. Whether n = 245 was fixed in advance is not verified here.

**Realised ceiling over the whole resource range (exact).** For any
probability pi on [f,1], E^pi_n(f) <= C_n(f) := sup_{q in [f,1]} prod e(q, W_i).
Here C_n(f) = exp(n d(phat_n || f)) if phat_n > f, and C_n(f) = 1 otherwise,
since the product is log-concave in q and peaks at phat_n. Since
d(phat || f) decreases in f on [0, phat], C_n(f) <= C_n(3/4) for every
f >= 3/4. On the Delft data, max_{n <= 245} C_n(3/4) = 7.7797 (at n = 241,
k = 194), which is less than 20 (exact rational comparison).

Every escape-route frontier has f(r) >= 3/4:
- (a): f = 3/4 + c/2.
- (b): f = 3/4 + c/4.
- (d): f = 1 - l, with l <= 1/4.
- The local null with the RNG bias: f = xi.

So for every constant-bet mixture fixed independently of the data and every
resource level, sup_n E_n < 7.78. Consequences:

- At alpha = 0.05, the confidence sets built from this class are the full
  ranges: c in [0, 1/2] for (a), c in [0, 1] for (b), and l in [0, 1/4] for (d).
  Levels with f = 1 (c >= 1/2 in (a), c = 1 in (b), l = 0 in (d)) are never
  rejectable, and Theorem ST-T281 needs f in (0,1); they are included trivially.
  In (d), f = 1 - l decreases in l, so the statement is an upper confidence bound
  on l, which equals 1/4 here. The same holds for every alpha < 1/7.7797 = 0.1285.
- This conclusion does not depend on how tau is combined with a resource
  budget, provided the combined bound is at least 3/4.
- The default uniform mixture gives anytime p-values of 0.36 (c = 0), 0.37
  (c = 1/100 under (a)), and 0.46 (l = 1/5, or c = 1/10 under (a)).
- Context only, with no inferential claim: the setting counts are
  00:53, 01:79, 10:62, 11:51, a fixed-n chi-square of 7.98 on 3 df (p = 0.046)
  against uniform settings. RNG independence and the tau model are assumed, not
  tested.

**Reading (heuristic).** One reading is that Delft 2015 is evidence-limited
rather than loophole-limited: the fixed-n p = 0.039 needs n to have been fixed
independently of the data, while the anytime-valid statement needs no such
assumption and delivers much less evidence. An earlier draft expected
nontrivial anytime-valid lower bounds on c and l; that is false at
alpha = 0.05 for constant-bet mixtures, and this negative result is the
finite-check outcome recorded here.

## Assumptions

1. Settings are uniform and independent of lambda and of the past, except in
   ST-T283, where the dependence is the modelled resource. The Delft local null
   uses the paper's tau model. RNG independence is assumed, not tested.
2. Resource budgets hold per trial, conditionally on the past (expected cost
   <= c, or p(xy | lambda, past) >= l, per trial). Budgets that hold only on
   average over the run are not covered.
3. In ST-M85, losses are independent across sides and independent of settings
   and of the outcomes, and the local model must reproduce the full
   three-outcome behaviour.
4. The trial order is the timestamp order, and the betting mixture does not
   depend on the data.

## Nonclaims

- CHSH only. ST-T284 assumes uniform settings; no optimisation over setting
  distributions is done.
- The realised-ceiling statement covers mixtures of constant bets on the win
  indicator, tested against the relaxed null H(f(r)). It does not cover
  e-processes valid only for the narrower escape-route model classes, full-data
  (setting- and outcome-resolved) test factors such as the PBR factors of
  Zhang, Glancy and Knill (Phys. Rev. A 88, 052119 (2013)), or predictable
  adaptive bets; the adaptive bets explored above reached at most 4.47, which
  is not a proof. ST-T285 still bounds their expected log growth.
- A fixed-n e-variable 1{K >= 196} / P_xi(K >= 196) would realise 25.5. It is
  valid only if the threshold 196 had been fixed in advance, which it was not.
- Budgets that vary per trial, or that hold only on average over a run, need
  a separate Azuma-type argument, which is not given.
- Prior-art reanalyses of these data and related betting framings: Elkouss and
  Wehner (2016); Gill, arXiv:2209.00702 (2022); Nomura, Yamagata and Fujiwara,
  arXiv:2601.09339 (2026), on game-theoretic capital processes for CHSH
  locality and measurement-dependence loopholes.
- Nothing here bears on whether the world is simulated. These are frontiers
  for restricted classical-simulator hypotheses of the "local simulator with a
  leak" type.

## Relation to repository claims

- **ST-F50** (Delft fixed-n statistic, p = 0.039): ST-F56 adds an
  optional-stopping-valid counterpart and shows that it is much weaker.
- **ST-T08** (one-sided Bernoulli e-process): ST-T281 is its conditional-null
  form with an exact closed form for the uniform mixture.
- **ST-T02** (likelihood-ratio evidence ceiling) and **ST-T10** (adaptive Bell
  KL bound, [bell-predictive-bounds](bell-predictive-bounds.md) section 5):
  ST-T285 is the related KL and expected-log statement for composite
  e-variables, with the expected-sample-size floor.
- **ST-T271** (KT Bayes-factor rate): the uniform-mixture penalty seen here is
  the same phenomenon; log E_n is roughly n d(phat || f) minus an O(log n)
  penalty.
- **Formal-results open problem 4** (sequential tests on real data): this
  partially addresses its real-data half for Bell escape-route nulls.

## Open problems

1. **ST-O03.** Find the entropy-cost frontier: the maximum win probability
   given H(M) <= h or I(M; x) <= h. This is open within this program; no
   literature search for mutual-information or entropy-cost CHSH frontiers was
   done.
2. Find the joint frontier for simultaneous signalling, setting dependence and
   RNG bias, with f(c, l, tau) derived rather than bounded below by 3/4. A joint
   measurement-dependence and detection-efficiency frontier with Hall's measure
   was posted by Alai, arXiv:2608.18886 (2026), unrefereed and with a different
   dependence measure; the problem stays open for the l-measure, signalling and
   tau jointly.
3. Give Azuma-type versions of these results for budgets that hold only on
   average over a run.
