# The random-bit price of shared codebook randomness

Claims ST-T310 to ST-T313, ST-M90 to ST-M93 and ST-F61
([manifest](../claims/random-bit-price-claims.json)). Certificate:
`src/simtheory/random_bit_price.py`, receipt
[`receipts/random-bit-price-shared-randomness.txt`](../receipts/random-bit-price-shared-randomness.txt),
tests in `tests/test_random_bit_price_shared_randomness.py`.

Status: Theorems 1, 2 and 4, Proposition 5 and Corollary 3' are proved here.
Theorem 3(1)-(3) is the Knuth and Yao (1976) theorem, standard and reproved for
completeness (its upper bound E[T] < H + 2 is cited and numerically checked).
Finite checks cover the committed repository instances.

This prices, for finite rational one-shot shared-codebook games, the exact
non-dyadic seed cost left open by ST-T95 ("does not price exact non-dyadic
random-seed generation") and ST-T109 ("support size does not equal ... exact
random-bit cost of the shared seed"): the fixed budget completely, and the
variable budget exactly when the optimal set is a singleton (and as an attained
minimum in general). The analogous random-bit nonclaims in the pathwise-regret,
polyhedral-confidence and feedback-regret manifests are covered only insofar as
those games satisfy A1-A4, which was not checked.

## Prior work

A b-bit seed law is exactly a 2^b-uniform mixed strategy (a uniform choice over
a multiset of size 2^b), and Delta_b below is exactly the set of 2^b-uniform
strategies. Sparse and k-uniform approximation of optimal strategies is
classical: Althofer (Linear Algebra Appl. 199 (1994) 339-355) and Lipton and
Young (STOC 1994, 734-740) give k-uniform eps-optimal strategies with
k = O(log R / eps^2), so a gap O(range sqrt(ln R / 2^b)) independent of support;
see also Lipton, Markakis and Mehta (ACM EC 2003), Feder, Nazerzadeh and Saberi
(2007), Kalyanaraman and Umans (2007) on playing games with limited randomness,
Hubacek, Naor and Ullman (Theory Comput. Syst. 59 (2016) 722-746) on limited
randomness in repeated games, Neyman and Okada (GEB 29 (1999) 191-223) and
Valizadeh and Gohari (GEB 115 (2019) 363-380). The fact that bounded-depth
fair-coin samplers realize exactly the dyadic laws, which gives Lemma 0 and the
dichotomy, is in Knuth and Yao (1976). Lemma 0, Theorem 2(1)-(2) and the
denominator lower bound 2(4) are elementary or standard. The new content is the
exact two-sided Theta(2^-b) rate for a fixed rational game (arithmetic lower
bound plus deterministic largest-remainder rounding) without nondegeneracy
assumptions, the exact K3 and ST-M27 curves, the composition of Knuth-Yao with
the optimal set (Corollary 3'), and the application to the repository's
committed games. The Lipton-Young rate is complementary: worse in b, but
independent of s and n.

## 1. Setting and assumptions

A finite rational game A in Q^{R x n}: rows r are adversary scenarios
(point-mass models, declared priors, or TV-ball vertices), columns c are
deterministic complete zero-error codebooks, and A_rc is the expected codeword
length (or regret) of codebook c under scenario r.

- **A1 (public seed).** A seed is observed by the encoder and every decoder
  before the source is observed. It selects a column. Every selected codebook is
  zero error, so zero error is preserved (as in ST-T95).
- **A2 (oblivious adversary).** The scenario is chosen without seeing the seed.
  Hence a seed law that induces column law w in the simplex Delta has worst-case
  payoff f(w) = max_r (A w)_r, and V* = min_{w in Delta} f(w). Write O = argmin f,
  a nonempty rational polytope.
- **A3 (resource models).**
  - Fixed budget: b independent fair bits, and the column is any deterministic
    function g of them. V_b := min_g f(w_g).
  - Variable budget: an i.i.d. fair bit stream, a stopping time T of its natural
    filtration, an output that is a function of B_1..B_T, and P(T < infinity) = 1.
  - L-ary coin: t independent uniform tosses of an L-sided coin. V_{L,t} defined
    as for V_b.
- **A4 (rationality).** Entries of A are rational with common denominator D_A,
  and V* = p/q in lowest terms (V* is rational because it is a basic LP value).

**Lemma P (reduction invariance).** Merging payoff-identical columns, and moving
each weakly dominated column's weight onto its dominator (as
`robust_prior_codes._dominates` prunes the repository matrices), changes neither
V*, nor V_b, nor V_{L,t}, nor the infimum over the optimal set of the Knuth-Yao
cost of Theorem 3. *Proof.* A grid point of the reduced game embeds in the full
game with the same payoffs, and a grid point of the full game maps to the
reduced game by moving weight onto dominators (or merging copies); the image
stays on the same grid and no row payoff increases. So the grid values agree,
and optimal laws map to optimal laws in both directions. The coarsening map does
not increase the Knuth-Yao cost, because a sampler of a finer law yields a
sampler of any coarsening with the same stopping time; and the reduced optimal
set embeds in the full one with the same cost. QED. "Unique optimal law" and the
table entries below refer to the reduced game.

**Lemma 0 (realizable laws).** With b fair bits the realizable column laws are
exactly Delta_b := Delta intersect 2^-b Z^n. With t tosses of an L-ary coin they
are exactly Delta intersect L^-t Z^n.

*Proof.* g induces w_c = |g^{-1}(c)| / 2^b. Conversely, for integers k_c >= 0
summing to 2^b, partition {0,1}^b into blocks of sizes k_c. Same for L^t. QED

## 2. Model result ST-M90: the K3 fixed-budget value curve (Theorem 1)

The K3 public-randomness game (docs/blackwell-randomness-separation.md, ST-M26,
ST-M45, ST-M47): three one-state point-mass models, and every complete binary
prefix code on three symbols has lengths a permutation of (1, 2, 2). Column c
gives the one-bit codeword to state c, so A_mc = 1 if m = c else 2.

**Theorem 1.** For every b >= 0,

    V_b = 2 - floor(2^b / 3) / 2^b,
    V_b - 5/3 = (2^b mod 3) / (3 * 2^b) > 0,
    V_{2j} = V_{2j+1} = 5/3 + 1 / (3 * 4^j).

The sequence is 2, 2, 7/4, 7/4, 27/16, 27/16, 107/64, 107/64, 427/256, ... In
particular V* = 5/3 is never attained by any finite number of fair bits, every
odd-numbered bit is worthless, and for j >= 1 the 2j-th bit is worth exactly
1/4^j.

*Proof.* Since sum w = 1, (A w)_m = w_m + 2(1 - w_m) = 2 - w_m, so
f(w) = 2 - min_m w_m. On Delta_b write w = k / N with N = 2^b. Then
3 min k <= sum k = N gives min k <= floor(N/3), and (a, a, N - 2a) with
a = floor(N/3) attains it because N - 2a >= a. So V_b = 2 - floor(N/3)/N, and
1/3 - floor(N/3)/N = (N - 3 floor(N/3)) / (3N) = (N mod 3) / (3N). Finally
2^b mod 3 is 1 for even b and 2 for odd b, which gives the pair formula, and for
j >= 1, V_{2j-1} - V_{2j} = 2/(3 * 2^{2j-1}) - 1/(3 * 4^j) = 1/4^j. QED

**Corollaries for existing claims.**

- ST-M45 (regret, oracle value 1): the b-bit minimax regret is
  1 - floor(2^b/3)/2^b, never 2/3.
- ST-M47 (coordination term 1/3): with b public bits the realized coordination
  value is exactly floor(2^b/3)/2^b. One bit buys nothing.
- Blackwell separation note: the garbling (1/3, 1/3, 1/3) that makes the
  constant experiment simulate the public three-way coin cannot be implemented
  with any bounded number of fair bits. Its exact price is Theorem 3 below.

## 3. Theorems ST-T310 and ST-T311: the dyadic dichotomy and two-sided gap for any finite game (Theorem 2)

**Theorem 2.** Under A1 to A4:

1. (Monotonicity) V* <= V_{b+1} <= V_b for all b.
2. (Dichotomy, ST-T310) V_b = V* iff O meets Delta_b. Hence V_b = V* for some
   finite b iff some optimal mixture is dyadic, and then V_b = V* for all
   b >= b_0, where b_0 is the least such b.
3. (Upper bound, rounding) For every optimal w* with support S, s = |S|, and
   Delta_S := max_r (max_{c in S} A_rc - min_{c in S} A_rc),

       V_b - V* <= Delta_S * floor(s/2) / 2^b.

   By the Shapley-Snow basic-solution theorem (Contributions to the Theory of
   Games I, Ann. Math. Studies 24 (1950)) there is a basic optimal w* with
   s <= min(R, n) (compare ST-T95). With the payoff range
   max_r (max_c A_rc - min_c A_rc) >= Delta_S, this gives
   V_b - V* <= (payoff range) * floor(min(R, n)/2) / 2^b.
4. (Lower bound, arithmetic) If V_b > V* then

       V_b - V* >= 1 / lcm(2^b D_A, q) >= 1 / (D_A q 2^b).

5. (Theta without nondegeneracy assumptions, ST-T311) Consequently, if O
   contains no dyadic point then for every b >= 0

       2^-b / (D_A q)  <=  V_b - V*  <=  Delta_S floor(s/2) 2^-b,

   and b(epsilon) := min{b >= 0 : V_b - V* <= epsilon}, for epsilon > 0,
   satisfies max(0, log2(1/(epsilon D_A q))) <= b(epsilon) <=
   max(0, ceil(log2(Delta_S floor(s/2)/epsilon))).

*Proof.* (1) Delta_b is a subset of Delta_{b+1}, which is a subset of Delta.

(2) If w in O intersect Delta_b then V_b <= f(w) = V*, so V_b = V* by (1).
Conversely a grid minimizer w_b with f(w_b) = V* lies in O. Monotonicity gives
the tail statement.

(3) Let N = 2^b. Largest-remainder (Hamilton) rounding: set
k_c = floor(N w*_c) on S and 0 off S, deficit D = N - sum k_c. D equals the sum
of the fractional parts, so D is an integer with D < s when D > 0; add one unit
to the D coordinates of S with the largest fractional parts. The result w_b is
in Delta_b with support in S. Let d = w_b - w*, so sum d = 0. In units of 1/N,
the upward errors are (1 - frac) <= 1 on D coordinates and the downward errors
are frac < 1 on s - D coordinates, and the two totals are equal (sum d = 0). So
the positive part P of d satisfies P <= min(D, s - D)/N <= floor(s/2)/N. For each
row, (A d)_r = sum_{c in S} A_rc d_c <= (max_S A_r) P - (min_S A_r) P <=
Delta_S P. Hence f(w_b) <= f(w*) + max_r (A d)_r <= V* + Delta_S floor(s/2)/N.

(4) Write A = a / D_A with a integral. For the grid minimizer k / 2^b,
V_b = max_r sum_c k_c a_rc / (2^b D_A) lies in (1/M) Z with M = 2^b D_A. The
difference of an element of (1/M) Z and p/q lies in (1/lcm(M, q)) Z, so a
positive difference is at least 1/lcm(M, q).

(5) Combine (2), (3) and (4). The epsilon statements solve the two bounds for b.
QED

**Sharpness.** The lower constant is attained: K3 has D_A q = 3 and even-b gap
exactly 1/(3 * 2^b); ST-M27 at radius 1/2 has D_A q = 30 and even-b gap exactly
1/(30 * 2^b) (Proposition 5). The upper constant is not claimed to be tight.

**Lemma 2a (deciding the dichotomy; L >= 2).** For an integer L >= 2, a
rational polytope P meets Z[1/L]^n iff its affine hull does. *Proof.* If
x in aff P is in Z[1/L]^n, write aff P = x + span_Q(v_1..v_k) with integer v_i.
Since L >= 2, the points x + sum (m_i / L^e) v_i are in Z[1/L]^n and dense in
aff P, and relint P is a nonempty open subset of aff P. QED (For L = 1,
Z[1/L] = Z and density fails; the code decides L = 1 only for a single point
and refuses larger polytopes.) Parametrizing aff P by pivot coordinates as
x_J = z, x_{J^c} = c + G z, and letting m be the part of the common denominator
of (c, G) coprime to L, the condition becomes a congruence c' + G' z = 0 over
Z/m, which `polytope_meets_ring` decides by exhaustive search over (Z/m)^k. This
is an exact decision procedure, bounded in the checker by m^k <= 2 * 10^6.

## 4. Model result ST-M91: the skew TV instance at radius 1/2 (Proposition 5, ST-M27)

For K3 with nominal prior (4/5, 1/10, 1/10) and TV radius 1/2, the repository's
exact matrix (5 TV vertices x 3 codebooks; the columns give the short codeword
to states (1, 0, 2), the repository's column order) is

    (7/5, 17/10, 19/10), (19/10, 17/10, 7/5), (7/5, 8/5, 2), (2, 8/5, 7/5), (2, 1, 2),

for the TV-ball vertices (3/10, 3/5, 1/10), (3/10, 1/10, 3/5), (2/5, 3/5, 0),
(2/5, 0, 3/5) and (1, 0, 0).

**Proposition 5.** O = {(1/3, 1/3, 1/3)}, V* = 5/3, and for every b >= 0

    V_b = 5/3 + (2^b mod 3) / (30 * 2^b),

exactly one tenth of the K3 gap. The b-bit randomization gain over the
deterministic value 17/10 is floor(2^b/3)/(10 * 2^b): zero for b = 0 and b = 1.

*Proof.* Write w = u + d with u uniform and sum d = 0. Then (A u)_r = 5/3 for
every r, so f(u + d) = 5/3 + max_r (A d)_r. Row by row, A d equals
((-3d_0 + 2d_2)/10, (2d_0 - 3d_2)/10, (-d_0 + 2d_2)/5, (2d_0 - d_2)/5, -d_1).
The set {d : sum d = 0, A d <= 0} is {0}: rows 5 and 1+2 force d_1 >= 0 and
d_1/10 <= 0, so d_1 = 0 and d_2 = -d_0; rows 1 and 2 then give -d_0/2 <= 0 and
5d_0/10 <= 0, so d = 0. This gives both V* = 5/3 and O = {u}. On Delta_b put
N = 2^b and x_i = 3k_i - N, so d_i = x_i/(3N), sum x = 0, and the gap is the
maximum over rows of (integer numerator)/(30N) with numerators
(-3x_0 + 2x_2, 2x_0 - 3x_2, 2(-x_0 + 2x_2), 2(2x_0 - x_2), -10x_1).

- Even b (N = 1 mod 3): Theorem 2(4) gives gap >= 1/(30N). The grid point
  k = ((N-1)/3, (N+2)/3, (N-1)/3) has x = (-1, 2, -1) and numerators
  (1, 1, -2, -2, -20), so gap = 1/(30N).
- Odd b (N = 2 mod 3): every x_i = 1 mod 3. Suppose all numerators are <= 1.
  Row 5 gives x_1 >= 0, so x_1 >= 1; rows 1+2 give x_1 = -(x_0 + x_2) <= 2, so
  x_1 = 1 and x_2 = -1 - x_0. Row 1 becomes -5x_0 - 2 <= 1, so x_0 >= 0, hence
  x_0 >= 1; row 2 becomes 5x_0 + 3 <= 1, so x_0 < 0. Contradiction. So the gap is
  >= 2/(30N), and V_b <= V_{b-1} = 5/3 + 2/(30N) gives equality.

The gain statement is 17/10 - V_b = (2^b - (2^b mod 3))/(30 * 2^b). QED

**Radius <= 7/15 costs zero bits.** For 0 <= r <= 7/15, the deterministic code
that gives the heavy state 0 the one-bit codeword costs at most 6/5 + r, and the
ball point p = (4/5 - r, 1/10 + r/2, 1/10 + r/2) has max_c p_c = 4/5 - r, which
forces V* >= 2 - (4/5 - r) = 6/5 + r; so V* = V_0 = 6/5 + r (see also
[shared-randomness-tv-robust-coding](shared-randomness-tv-robust-coding.md),
where the 7/15 threshold of ST-M27 is derived). The check confirms this with
the repository solver for every r = k/30, k = 0..14, and a strict gain at
r = 1/2.

## 5. Theorem 3 (Knuth and Yao 1976; standard, reproved for completeness) and Corollary 3' (ST-T312)

For a law w on columns and t >= 0 let

    rho_t(w) := sum_c frac(2^t w_c) / 2^t = 1 - sum_c floor(2^t w_c) / 2^t,
    kappa(x) := sum_{t >= 0} frac(2^t x) / 2^t = sum_{k >= 1} k x_k 2^-k,

where x_k are the binary digits of x in [0, 1) (terminating expansion for dyadic
x; kappa(1) = 0). kappa is Knuth and Yao's nu.

**Theorem 3 (Knuth and Yao, "The complexity of nonuniform random number
generation", in Traub (ed.), Algorithms and Complexity, Academic Press 1976;
see Cover and Thomas, Elements of Information Theory, 2nd ed., Sec. 5.11).**
Under A1, A2 and the variable-budget model:

1. (Universal tail bound) Every exact sampler of w satisfies
   P(T > t) >= rho_t(w) for every t.
2. (Attainment) The Knuth-Yao DDG sampler has P(T > t) = rho_t(w) for every t
   and terminates almost surely. It is therefore optimal for E[T] and
   stochastically smallest, with

       E*[T](w) = sum_{t >= 0} rho_t(w) = sum_c kappa(w_c),

   a rational number computed exactly from the eventually periodic orbit of the
   doubling map: kappa(x) = head + cycle / (1 - 2^-pi).
3. (Entropy sandwich) H(w) <= E*[T](w) < H(w) + 2.

**Corollary 3' (ST-T312, the price of V*).**

4. V* is attainable with an almost surely finite number of fair bits for every
   game. The infimum of the expected number of fair bits over samplers attaining
   V* equals min_{w in O} sum_c kappa(w_c); the minimum is attained (kappa is
   lower semicontinuous, as a series of nonnegative lower semicontinuous terms,
   and O is compact), and equals sum_c kappa(w*_c) when O = {w*}.
5. (Bounded impossibility) If T <= B almost surely then w is in Delta_B. So if O
   has no dyadic point, no bounded-bit sampler attains V*, and every sampler that
   attains V* has P(T > t) >= min_{w in O} rho_t(w) > 0 for every t.

*Proof.* (1) The event {T <= t, column = c} is determined by B_1..B_t, so its
probability lies in 2^-t Z and is at most w_c, hence at most
floor(2^t w_c)/2^t. Sum over c.

(2) Build the tree level by level. Let U_t be the number of undecided depth-t
nodes, U_0 = 1 (if no w_c = 1). At depth t+1 the 2U_t children receive
bit_{t+1}(w_c) = floor(2^{t+1} w_c) - 2 floor(2^t w_c) leaves labelled c. By
induction U_t / 2^t = rho_t(w), and the step is feasible because
2U_t - sum_c bit_{t+1}(w_c) = 2^{t+1} rho_{t+1}(w) >= 0. The mass labelled c by
depth t is floor(2^t w_c)/2^t, which increases to w_c, so the output law is w
and rho_t -> 0 gives P(T < infinity) = 1. Then E[T] = sum_t P(T > t) equals the
lower bound from (1) termwise. The digit identity follows from
frac(2^t x) = sum_{k > t} x_k 2^{t-k} and exchanging sums. For rational x the
orbit frac(2^t x) is eventually periodic with preperiod mu and period pi, which
gives the closed form.

(3) Lower bound: the column is a function of the leaf (B_1..B_T); since the
stopping set is prefix free and bits are fair, H(B_1..B_T) = E[T]. Upper bound:
Knuth and Yao (1976); cited, and checked on 200 random rational laws (minimum
margin 0.179 bits).

(4) and (5): attaining V* means the induced column law lies in O; apply (2), (1)
and Lemma 0. If O has no dyadic point then rho_t(w) > 0 for every w in O
(rho_t(w) = 0 would put w in Delta_t). Since frac is lower semicontinuous, so is
rho_t, and it attains a positive minimum on the compact set O. QED

## 6. Model result ST-M92: Knuth-Yao prices of the committed instances

| Instance | Optimal law (reduced game) | Fixed budget reaching V* | Least expected fair bits |
|---|---|---|---|
| K3 = ST-M26 = ST-M45 | (1/3, 1/3, 1/3), unique | none | 3 kappa(1/3) = 3 * 8/9 = **8/3** |
| ST-M27 radius 1/2 | (1/3, 1/3, 1/3), unique | none | **8/3** |
| ST-M21 (minimax and regret) | (1/2, 1/2), unique | b = 1 | **1** |
| K4 nonoracle minimax | (1/2, 0, 1/2), unique | b = 1 | **1** |
| ST-M27 radius 2/5 and 7/15 | O contains a pure law (at 7/15, O is a segment) | b = 0 | **0** |

For K3, P(T > t) = (2^t mod 3)/2^t for the optimal sampler and no sampler does
better at any t; H = log2 3 = 1.585 < 8/3 < 3.585. The 8/3-bit cost of an exact
uniform ternary choice is the classical Knuth-Yao example (see also Lumbroso,
"Optimal discrete uniform generation from coin flips, and applications",
arXiv:1304.1916, 2013); the model result is its identification as the exact
coordination price of these games. One uniform ternary toss suffices
(Theorem 4).

## 7. Theorem ST-T313 and model result ST-M93: coin alphabets (Theorem 4)

**Theorem 4.** For integers L >= 2, with t independent uniform L-ary tosses,
V_{L,t} = V* iff O meets L^-t Z^n; V* is attainable by some finite number of
L-ary tosses iff O meets Z[1/L]^n; in one toss iff O meets (1/L) Z^n. Whenever
V_{L,t} > V*, V_{L,t} - V* >= 1/(D_A q L^t).

**Instances (ST-M93).** For K3 (and for ST-M27 at radius 1/2, also with
O = {uniform}), one toss attains V* iff 3 | L, finitely many tosses attain V* iff
3 | L, and the one-toss K3 value is V_{L,1} = 2 - floor(L/3)/L. For ST-M21 and
K4 (optimum (1/2, 1/2)) one toss attains V* iff 2 | L.

*Proof.* Lemma 0 and the argument of Theorem 2(2) and (4) with 2^b replaced by
L^t. For O = {(1/3,1/3,1/3)}: 1/3 is in L^-t Z iff 3 | L^t iff 3 | L (3 prime).
The K3 formula is the proof of Theorem 1 with N = L. QED

Building a uniform L-ary coin from fair bits is itself priced by Theorem 3 and
is not free.

## 8. Relation to existing claim IDs

- **ST-T95** (exact shared-randomness game; nonclaim: does not price non-dyadic
  seed generation): Theorem 2 and Corollary 3' supply that price for finite
  rational one-shot games.
- **ST-T109** (Caratheodory support; nonclaim: support is not the random-bit
  cost): support s enters only the rounding constant floor(s/2); the cost is
  governed by dyadicity of O (fixed budget) and by kappa (variable budget).
- **ST-M21**: its strict gain 19/10 -> 31/20 costs exactly one fair bit, fixed
  or expected.
- **ST-M26, ST-M45, ST-M47**: non-dyadic. The b-bit curve is Theorem 1; the
  coordination term 1/3 of ST-M47 is realized as floor(2^b/3)/2^b; the exact
  expected price is 8/3 bits; a 3-sided coin pays it in one toss.
- **ST-M27**: radius <= 7/15 costs zero bits (Section 4); at radius 1/2
  Proposition 5 gives the exact curve, one tenth of K3, with zero gain from a
  single bit.
- **ST-T171, ST-T174, ST-M41, ST-T182, ST-T184** (remark, not a claim): for
  those lanes, if the optimal set of the relevant public-mixing game contains no
  dyadic point (and the game satisfies A1-A4), its value is attained by no
  bounded-bit seed (Theorem 2(2)). A b-bit analogue of the ST-T184 coordination
  term could be defined, but the decomposition with bit-limited mixing classes is
  not derived or checked here, and those lanes' matrices are not rechecked.
- **ST-T152** (feedback-information regret) also mentions random-bit cost in its
  nonclaims; this result does not close it.
- **Formal-results open problem 2** (rendering lower bounds combining memory,
  update time, randomness and communication): tangential. Randomness is priced
  here only for one-shot shared-codebook games; nothing is said about rendering
  lower bounds.
- **Reading.** As in ST-T171 and ST-M41, the decision gain comes from a
  source-independent coin; this result prices that coin and makes no claim about
  simulators.

## 9. Nonclaims

- Fair, independent, public bits (or uniform L-ary tosses) are assumed. The cost
  of extracting them from a biased or physical source (including NIST beacon
  output) is not addressed, and no fairness of any real source is certified (for
  playing with a biased coin see Gossner and Vieille, GEB 41 (2002) 206-226).
- The adversary is oblivious to the seed (A2). If the scenario may depend on the
  realized seed, the value reverts to the deterministic value and no number of
  bits helps.
- Private encoder randomness is not covered (the repository's earlier result
  that it does not help zero-error alphabets is unchanged).
- When O is not a singleton, the minimum over O of the Knuth-Yao cost is attained
  but not computed in general.
- The Knuth-Yao upper bound E[T] < H + 2 is cited, not reproved; it is checked
  numerically on 200 seeded random laws.
- The upper constant Delta_S floor(s/2) is not claimed tight. Only the lower
  constant 1/(D_A q) is shown attained (K3, ST-M27 radius 1/2, even b).
- The arithmetic lower bound uses rationality of A; nothing is claimed for
  irrational payoffs.
- Approximate (TV-close) sampling with a bit budget is only treated through V_b;
  no rate-distortion tradeoff between bits and expected length is claimed beyond
  Theorem 2 (for optimal fixed-precision approximate sampling see Saad, Freer,
  Rinard and Mansinghka, Proc. ACM Program. Lang. 4 (POPL 2020), Art. 36).
- The congruence decision procedure is exact but bounded by m^k <= 2 * 10^6
  states.
- Nothing here bears on whether reality is simulated; it is resource accounting.

## 10. Finite check ST-F61

All exact (Fractions or integers) unless noted.

- T1: K3 V_b for b = 0..12 by exhaustive enumeration of all dyadic weight
  vectors through the min-weight reduction, and by a fully generic enumeration of
  all 2^b-compositions against the matrix for b <= 8; closed forms checked.
- T2: eight committed matrices (ST-M21 minimax and regret, K4 nonoracle, ST-M26,
  ST-M45, ST-M27 at radii 2/5, 7/15, 1/2) solved by an independent
  basis-enumeration solver with dual certificates; optimal-set vertices
  enumerated; dyadicity of O decided by Lemma 2a; V_b for b = 0..10 by exhaustive
  grid enumeration; monotonicity, both gap bounds, the rounding construction, and
  agreement between "V_b hits V*" and the dyadic decision verified. Gap curves for
  ST-M26 and ST-M27 radius 1/2 printed.
- T2r: 300 seeded random integer games (2 to 4 rows, 2 to 3 columns, entries
  0..5), b = 0..6: 219 dyadic (all exact by b <= 6), 81 non-dyadic (never exact,
  both gap bounds hold).
- T3: kappa via the periodic closed form; K3 = 8/3; the DDG level construction
  for K3 to depth 40 matches the universal tail lower bound at every depth; 200
  seeded random rational laws (2 to 5 atoms, denominators <= 40) agree across the
  closed form, the digit series and the DDG tail series; entropy sandwich in
  floating point; DDG terminates by depth 80 iff dyadic.
- T4: K3 and ST-M27 radius 1/2 for L = 1..12 one toss; K3 for L in
  {2, 4, 5, 7, 8, 10} and all L^t <= 1000; ST-M21 and K4 for L <= 12.
- X: seven matrices and values are matched against the repository's own exact
  certificates (`k3_shared_randomness_example`, `k4_nonoracle_minimax_example`,
  `full_tv_k3_shared_randomness_example`, `exact_shared_tv_robust_prefix_code`);
  for ST-M45 the hand-written regret matrix A - 1 is solved by
  `solve_exact_zero_sum_game` and only its value 2/3 is compared; the ST-M27
  radius sweep k/30, k = 0..15, uses the repository solver.

Runtime about 15 s single-threaded, standard library only.
