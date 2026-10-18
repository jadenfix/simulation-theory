# Two persistent views identify a latent prior only up to an orthogonal fiber

Claims ST-T297 to ST-T305, ST-M86 to ST-M89, ST-F59 and ST-O07
([manifest](../claims/two-view-orthogonal-fiber-claims.json)). Certificate:
`src/simtheory/two_view_fiber.py`, receipt
[`receipts/two-view-orthogonal-fiber.txt`](../receipts/two-view-orthogonal-fiber.txt),
tests in `tests/test_two_view_orthogonal_fiber.py`.

**Topics:** the orthogonal fiber, a sharp identified interval, a certified
weight floor, and the 2-view / anchor / 3-view recovery ladder.

**Status.** Proved here: Theorem A(b,c) (the stochastic reparametrization of the
fiber), A'(b), B, C(i), D, and the necessary condition of Theorem F. Standard
or known: Theorem A(a) (already in the repository, see below), A'(a) (known,
Henry-Kitamura-Salanie 2014 and Hall-Zhou 2003), the orthogonal-fiber form of
symmetric factorizations, C(ii) (Kruskal, cited) and E (standard). Exact
witnesses and bounded grids are typed model result and finite check.

Several parts of the original sketch come out sharper:

- strict positivity of the alternative prior is automatic;
- the endpoints of the k = 2 interval are piecewise rational in the observable
  law (q, T): rational once the extreme outcome pair is fixed, and the pair is
  itself selected from T;
- for a strictly positive channel, the set of consistent priors contains an
  open neighbourhood of the true prior;
- there is a certified positive weight floor for every k;
- the counterexample pair of the PR #68 audit (finding 3) is exactly one
  endpoint of the k = 2 identified interval.

## 0. Setting and notation

There are k latent states with prior pi in the open simplex (pi > 0). K is a
k x n row-stochastic channel of full row rank k. One persistent latent M ~ pi
emits two observations Y1, Y2, conditionally iid given M with law K[M, .]. The
observable laws are

- one view: q = K^T pi (a vector in R^n);
- two views: T = K^T D_pi K (n x n, symmetric, PSD; ST-T259).

Write s = sqrt(pi) (entrywise) and W = D_s K (k x n, nonnegative). Then

- T = W^T W;
- W 1 = s, since K 1 = 1;
- |s| = 1;
- s . w_x = q_x and |w_x|^2 = T_xx, where w_x is column x of W.

The **two-view fiber** of (pi, K) is the set of all k-state models (pi', K')
with pi' a probability vector, K' a k x n row-stochastic matrix, and
K'^T D_pi' K' = T. Throughout, k is fixed and known. Models with more than k
states are not classified (see the nonclaims).

## Theorem A (fiber classification)

**Lemma A0.**

1. rank T = k, and the column space of T equals the row space of K.
2. If (pi', K') is in the fiber, then pi' > 0, K' has rank k, and the row space
   of K' equals the row space of K.
3. The one-view law is implied by the two-view law: T 1 = K^T D_pi K 1 = K^T pi = q.

*Proof.*

1. T = W^T W, so rank T = rank W = rank K = k, because D_s is invertible. The
   column space of T is contained in col(K^T) = row(K), and both have dimension
   k, so they are equal.
2. rank(K'^T D_pi' K') is at most the number of nonzero entries of pi'. It
   equals k, so pi' > 0. Then rank K' = k, and row(K') = col(T) = row(K) by part
   1 applied to (pi', K').
3. Immediate. QED.

**Theorem A (ST-T297).** Let (pi, K) be as in Section 0. Statements (a) and (b)
classify the fiber, and (c) gives the orthogonal parametrization.

(a) (pi', K') is in the fiber if and only if K' = A K for a unique invertible
k x k matrix A with

- A 1 = 1,
- A^T D_pi' A = D_pi,
- K' = A K >= 0.

In that case pi' = A^{-T} pi, that is, pi'^T = pi^T A^{-1}.

(b) The map O -> (pi', K') given by

    u = O s,   pi' = u o u,   A = D_u^{-1} O D_s,   K' = A K = D_u^{-1} O W

is a bijection from

    G(W) := { O in O(k) : O W >= 0 entrywise }

onto the fiber. For O in G(W), u > 0 holds automatically. Two elements O, O' of
G(W) give models that differ only by a relabeling of the latents if and only if
O' = P O for a permutation matrix P.

(c) Equivalently, the fiber is in bijection with the ordered orthonormal frames
(o_1, ..., o_k) contained in the dual cone C* = { o : o . w_x >= 0 for all x }.
Here o_i is the i-th row of O, and C = cone{w_x} is the column cone of W.

*Proof.*

(a) By Lemma A0, row(K') = row(K) and K has full row rank, so K' = A K for a
unique A. This A is invertible because rank K' = k. Row sums give
1 = K' 1 = A K 1 = A 1.

Next, K^T (A^T D_pi' A - D_pi) K = 0. Let R = K^T (K K^T)^{-1} be a right inverse
of K. Multiplying on the left by R^T and on the right by R gives
A^T D_pi' A = D_pi. Multiplying this on the right by 1 and using A 1 = 1 gives
A^T pi' = pi.

Conversely, let A be invertible with A 1 = 1 and define pi' := A^{-T} pi. Then
1^T pi' = 1^T A^{-T} pi = (A^{-1} 1)^T pi = 1 because A^{-1} 1 = 1. If moreover
A^T D_pi' A = D_pi, then D_pi' = A^{-T} D_pi A^{-1} is congruent to the
positive definite D_pi, so pi' > 0 by Sylvester's law of inertia. If also
K' = A K >= 0, then K' is row-stochastic and K'^T D_pi' K' = K^T D_pi K = T.

(b) Suppose O is in G(W). Then O W 1 = O s = u, and O W >= 0 gives u >= 0. If
u_i = 0, row i of O W is zero. That is impossible, because O is invertible and
W has full row rank. So u > 0, pi' = u o u is positive, and
sum pi' = |u|^2 = |s|^2 = 1. Next, A 1 = D_u^{-1} O s = 1, K' = D_u^{-1} O W >= 0,
and

    A^T D_u^2 A = D_s O^T O D_s = D_pi.

So the image lies in the fiber by (a).

Conversely, given a fiber point with gauge A from (a), set u = sqrt(pi') > 0 and
O = D_u A D_s^{-1}. The identity A^T D_u^2 A = D_s^2 says exactly that
O^T O = I. Also A 1 = 1 gives O s = D_u A 1 = u. The two constructions are
mutually inverse, so the map is a bijection.

Relabeling a model by a permutation P sends (pi', K') to (P pi', P K'). This
changes u to P u and A to P A, hence O to P O.

(c) The condition O W >= 0 says o_i . w_x >= 0 for every i and every x. QED.

**Prior art and credit.** Theorem A(a) (K' = A K, A 1 = 1,
A^T D_pi' A = D_pi, with the data imposing only A K >= 0 and not A >= 0) is
already stated in [latent-mixture-two-view-rigidity](latent-mixture-two-view-rigidity.md)
Section 6 (PR #64), and the ST-T261 nonclaims and
`tests/test_latent_mixture_two_view.py` already record that two views do not
identify (pi, K) outside the nonnegative gauge class. That any two rank-k
factorizations T = W^T W differ by an orthogonal Q is the standard
symmetric-NMF fact (Huang, Sidiropoulos and Swami, IEEE Trans. Signal Process.
62 (2014) 211-224; Laurberg, Christensen, Plumbley, Hansen and Jensen, Comput.
Intell. Neurosci. 2008, Article 764206). The new content of Theorem A is the
stochastic reparametrization u = O s, pi' = u o u, K' = D_u^{-1} O W.

**Corollary A1 (ST-T298, strictly positive channels).** Suppose K > 0 entrywise
and k >= 2. Then W > 0, so G(W) contains a neighbourhood of I in O(k): it
contains a k(k-1)/2-dimensional manifold of fiber points that are not
relabelings of each other. Moreover, the set of consistent priors
{ (O s)^2 : O in G(W) } contains an open neighbourhood of pi in the simplex.

*Proof.* O W > 0 is an open condition, and it holds at O = I. Near I, P O lies
near I only for P = I, so distinct nearby O are not relabelings. The orbit map
SO(k) -> S^{k-1}, O -> O s, is a submersion (SO(k) acts transitively on the
sphere), so it is an open map. Squaring entrywise is a local homeomorphism near
the positive vector s. QED.

So for a strictly positive channel, the prior is not even locally identified
with two views, in any direction. For channels with zeros the fiber can be
finite even without anchors (ST-M89).

**Corollary A2 (ST-T299, relation to ST-T261 / P1-T7).** Because D_u and D_s are
positive diagonal, A >= 0 if and only if O >= 0. A nonnegative orthogonal matrix
has orthonormal nonnegative rows, so the rows have disjoint supports and O is a
permutation P. Then u = P s and A = D_u^{-1} P D_s = P. Hence the
nonnegative-gauge rigidity theorem (ST-T261 in PR #64, P1-T7 in PR #69) is
precisely the statement "G(W) intersected with the nonnegative matrices consists
of permutations". Its scope excludes every point of G(W) other than permutations,
and for a strictly positive K that is the whole manifold of Corollary A1.
ST-T261 and P1-T7 remain correct as scoped.

On the semantics argument in R11.3 of the paper's audit: nonnegativity of A
"is what makes each row of A K a convex combination of channel rows, preserving
its interpretation as a stochastic observation law". That condition is
sufficient, not necessary. In the witness below (ST-M87), A has a negative entry
while K' = A K > 0 is a genuine stochastic channel.

## Theorem A' (ST-T300, different channels)

**Setting.** T = K1^T D_pi K2, with K1 (k x n1) and K2 (k x n2) row-stochastic of
full row rank k, and pi > 0. The fiber is the set of (pi', K1', K2') with
K1'^T D_pi' K2' = T.

(a) Every fiber point has K1' = A K1 and K2' = B K2, with A and B invertible,
A 1 = B 1 = 1, pi' = A^{-T} pi, and

    B = D_pi'^{-1} A^{-T} D_pi.

Conversely, every invertible A with A 1 = 1 and A^{-T} pi > 0 defines B by this
formula. That B satisfies B 1 = 1 and A^T D_pi' B = D_pi, so it yields a signed
factorization of T. It is a stochastic fiber point exactly when A K1 >= 0 and
B K2 >= 0. The signed parameter set is an open subset of the (k^2 - k)-dimensional
affine space { A : A 1 = 1 }. When K1, K2 > 0, a neighbourhood of I in that space
is admissible.

(b) (Product-gauge rigidity.) If in addition A >= 0 and B >= 0, then A = B = P
for one permutation P.

*Proof.*

(a) As in Lemma A0, rank T = k, col(T) = row(K1) and row(T) = row(K2). The same
holds for the primed model, and it forces pi' > 0. So K1' = A K1 and K2' = B K2
with A 1 = B 1 = 1. Cancelling right inverses gives A^T D_pi' B = D_pi, hence
B = D_pi'^{-1} A^{-T} D_pi. Then

    B 1 = 1  <=>  A^{-T} pi = pi'.

The converse is the identity A^T D_pi' D_pi'^{-1} A^{-T} D_pi = D_pi. Positivity
is an open condition that holds at A = I.

(b) Take j != l. Then 0 = (D_pi)_{jl} = sum_i pi'_i A_ij B_il, and every term is
>= 0. With pi' > 0, this gives A_ij B_il = 0 for every row i. Fix i and pick j
with A_ij > 0. Then B_il = 0 for all l != j, so row i of B is e_j. If A_ij' > 0
for some j' != j, then B_ij = 0, a contradiction. So row i of A is also e_j.
Invertibility makes the map i -> j a permutation. QED.

The same-channel fiber is the slice A = B of this family, which is why its
dimension drops from k(k-1) to k(k-1)/2.

**Prior art.** With W = Y1 as the exclusion variable and Y = Y2, the
different-channel two-view model is the setting of Henry, Kitamura and Salanie,
"Partial identification of finite mixtures in econometric models", Quantitative
Economics 5 (2014) 123-144, whose Section 4.2 gives the observationally
equivalent models as a J(J-1)-parameter family; Hall and Zhou (Ann. Statist. 31
(2003) 201-224) show that the bivariate two-component case is identified only up
to a two-parameter family. So A'(a) and its dimension count are known. Only the
product-gauge rigidity (b), which supplies the different-channel statement that
the P1-T7 nonclaims set aside, is claimed here.

## Theorem B (ST-T301, sharp identified interval, k = 2)

Let k = 2 and drop outcomes with q_x = 0, which impose nothing. Define

- c_x := q_x^2 / T_xx, which lies in (0, 1];
- the extreme pair {x*, y*}: an outcome pair minimizing T_xy^2 / (T_xx T_yy),
  that is, the pair whose columns w_x, w_y span the widest angle. This pair is
  observable.

Call either element of the extreme pair x*. The latent favoured by x* is the one
with the larger K'_{i x*} / K'_{i y*} (a ratio with zero denominator reads as
+infinity); this is well defined in every fiber model, because columns x* and
y* are not parallel in any fiber model. Swapping the choice of x* maps the
interval below to [1 - U, 1 - L].

**Theorem B.** The identified set of the weight of the latent favoured by x* is
exactly

    [L, U] = [ 1 - q_{y*}^2 / T_{y*y*} ,  q_{x*}^2 / T_{x*x*} ].

The endpoints are piecewise rational in T: rational on each region where the
observable extreme pair is fixed, and continuous on the set of laws with q > 0.
The following also hold.

- pi_1 lies in [L, U].
- U is attained by the unique fiber model in which x* is an anchor for the
  favoured latent (K'_{2 x*} = 0). Explicitly, pi'_1 = c_{x*} and
  K'_{1 y} = T_{x* y} / q_{x*}.
- L is attained by the model in which y* is an anchor for the other latent.
- Without a label convention, the identified set of the unordered weights is
  { {p, 1 - p} : p in [L, U] }, so the identified set of "pi_1" is
  [L, U] union [1 - U, 1 - L].
- L = U if and only if each latent has an anchor outcome in the true model.

*Proof.* Columns w_x lie in the closed positive quadrant. Let phi_x in [0, pi/2]
be their angles. Full row rank means not all phi_x are equal. Write phi_min and
phi_max for the extremes. The vector s = sum_x w_x is a positive combination, so
its angle psi satisfies phi_min < psi < phi_max.

O(2) consists of the rotations R_theta and the reflections Pswap R_theta. Since
Pswap only permutes rows, Pswap R_theta is in G(W) if and only if R_theta is,
and the resulting model is the relabeled one (Theorem A(b)). So, up to
relabeling, the fiber is { R_theta : R_theta W >= 0 }.

R_theta rotates every column by theta and keeps its norm. Take theta in
(-pi, pi]. R_theta w_x stays in the closed quadrant if and only if
phi_x + theta is in [0, pi/2]. So the admissible set is the arc

    Theta = [ -phi_min , pi/2 - phi_max ],

which contains 0. Along this arc, u = R_theta s has angle psi + theta in
[psi - phi_min, psi + pi/2 - phi_max], a subset of (0, pi/2). The weight
pi'_1 = cos^2(psi + theta) is continuous and strictly decreasing in theta. Its
image is therefore

    [ cos^2(psi + pi/2 - phi_max) , cos^2(psi - phi_min) ] = [ 1 - cos^2(phi_max - psi) , cos^2(psi - phi_min) ].

Next, cos angle(s, w_x) = s . w_x / (|s| |w_x|) = q_x / sqrt(T_xx). All these
angles lie in [0, pi/2], so cos^2(psi - phi_x) = c_x. This gives U = c_{x*} and
L = 1 - c_{y*}, where x* has angle phi_min and y* has angle phi_max (the
naming device of the statement).

Observability of the pair: every angle lies in [phi_min, phi_max], a range of
length at most pi/2. So angle(w_x, w_y) = |phi_x - phi_y|, and it is maximized
by (x*, y*). The cosine of that angle is T_xy / sqrt(T_xx T_yy). Ties come from
parallel columns, which have equal c.

Labels: for a rotated model, K'_{2x} / K'_{1x} = (u_1 / u_2) tan(phi_x + theta).
This is increasing in phi_x, so x* stays the minimizer on the whole arc and the
label convention is constant there.

Endpoints: at theta = -phi_min, the column x* is rotated to angle 0, so
K'_{2 x*} = 0. Then q_{x*} = pi'_1 K'_{1 x*} and
T_{x* y} = pi'_1 K'_{1 x*} K'_{1 y}, which gives the stated formulas. The case
theta = pi/2 - phi_max is symmetric.

Point case: the weight is strictly monotone in theta, so L = U if and only if
Theta = {0}, if and only if phi_min = 0 and phi_max = pi/2. That means some
outcome is emitted only by latent 1 and some outcome only by latent 2. QED.

**Prior art.** Theorem B specializes the sharp two-component bounds of Henry,
Kitamura and Salanie (2014, Theorem 1) to a shared channel; the "rotate until a
component touches zero" mechanism is the Lawton-Sylvestre (Technometrics 13
(1971) 617-633) feasible-band construction of multivariate curve resolution.
Only the explicit closed form [1 - q_y^2/T_yy, q_x^2/T_xx] for the prior weight
is offered, with no priority claimed.

**Witness (ST-M87).** pi = (9/25, 16/25) and K = [[1/2, 1/4, 1/4], [1/6, 1/3, 1/2]].

- Observable law: q = (43/150, 91/300, 41/100). The diagonal of T is
  (97/900, 337/3600, 73/400).
- Extreme pair: x* = outcome 0, y* = outcome 2.
- Interval: [L, U] = [144/1825, 1849/2425] ~ [0.078904, 0.762474], around the
  true 0.36.
- Admissible arc: theta in [-0.41822, 0.35877] rad.
- Endpoint models:
  - U: K' = [[97/258, 145/516, 59/172], [0, 3/8, 5/8]]
  - L: K' = [[5/6, 1/6, 0], [59/246, 155/492, 73/164]]
- The rotation with cos 24/25 and sin 7/25 gives pi' = (1936/15625, 13689/15625),
  signed gauge A = [[18/11, -7/11], [7/39, 32/39]], and a strictly positive K'.
  This is the first ledger witness whose alternative channel is strictly
  positive; the existing PR #64 / PR #68 pair is an anchor (endpoint) model with
  a zero in K'.

**Other examples.**

- One anchor only: K = [[1/2, 1/2, 0], [1/4, 1/4, 1/2]] with the same pi gives the
  one-sided interval [9/25, 289/325].
- PR #68 audit pair: the pair ((1/2, 1/2), [[3/4, 1/4], [1/4, 3/4]]) versus
  ((1/5, 4/5), [[1, 0], [3/8, 5/8]]) is exactly the L-endpoint anchor model of the
  symmetric channel, whose identified interval is [1/5, 4/5].

## Theorem D (ST-T302, a certified weight floor for every k)

Define

    ell(T) := min over unit o in C* of (o . s)^2 = min over extreme rays nu of C* of (nu . s)^2 / |nu|^2.

The extreme rays of C* are the inward normals of the facets of the column cone C.

**Theorem D.**

- ell(T) depends only on T.
- 0 < ell(T) <= min_i pi_i.
- Every model in the two-view fiber satisfies pi'_i >= ell(T) for every latent i,
  and hence pi'_i <= 1 - (k-1) ell(T).
- For k = 2, ell(T) = min(L, 1 - U), and it is the exact minimum latent weight
  over the fiber.

*Proof.* Dependence on T only: by Theorem A, any two rank-k factors of T are
related by an orthogonal Q (W -> Q W), and s = W 1 moves to Q s. So C* moves to
Q C* and ell is unchanged.

Positivity: C is full-dimensional and s is a strictly positive combination of
all its generators, so s lies in the interior of C. Hence o . s > 0 for every
nonzero o in C*, and C* intersected with the unit sphere is compact. This gives
ell > 0.

The fiber bound: for a fiber point O, each row o_i is a unit vector in C*
(Theorem A(c)), and pi'_i = (o_i . s)^2 >= ell.

Reduction to extreme rays: for t >= 0, the set { o : o . s >= t |o| } is a
convex cone. C* is generated by its extreme rays. So if every extreme ray
satisfies the inequality, all of C* does.

The case k = 2: the extreme rays of C* are the normals to w_{x*} and w_{y*}, and
(nu . s)^2 / |nu|^2 = sin^2 angle(s, w) = 1 - c. Theorem B gives the exact minima
L (latent 1) and 1 - U (latent 2). QED.

**k = 3 instance (ST-M88 and ST-F59, exact).** pi = (1/9, 4/9, 4/9) and
K = [[1/2, 1/4, 1/8, 1/8], [1/8, 1/2, 1/4, 1/8], [1/8, 1/8, 1/4, 1/2]].

- **Floor:** ell = 4/153 ~ 0.026144, with minimizing ray nu = (1/24, -1/96, 0).
- **The floor is attained:** the slice C* intersected with nu^perp is a planar
  cone. Its two boundary rays have nonpositive inner product, which is checked
  exactly. So the slice contains two orthogonal unit vectors, and
  (nu/|nu|, o2, o3) is an orthonormal frame in C*. Its first weight is exactly
  4/153. Hence the smallest latent weight over this fiber is exactly 4/153.
- **Grid values (label-free):** a 9261-point rational Cayley grid gives 197
  admissible points, every one an exact fiber model (the check asserts that each
  reproduces T exactly and has a row-stochastic channel). Among them the first
  weight takes the exact values 784/23409 ~ 0.0335 and 1369/2025 ~ 0.6760. The
  maximum is attained near a cyclic relabeling, so "first weight" means some
  latent's weight; the admissible grid points form 4 components under axis
  adjacency, and on the component of the identity the first weight ranges only
  over [0.0335, 0.6049]. These are exact values attained by fiber models, not an
  interval: connectedness of the values in between is not certified.
- **Outer bound:** [ell, 1 - 2 ell] = [0.0261, 0.9477] is valid but loose at the
  top.
- **Float scan (not certified):** a float scan over the Cayley chart found a
  maximum label-free weight near 0.746.

## Theorem C (the recovery ladder)

(i) **Two views plus anchors (ST-T303).** Suppose each latent i has an anchor
outcome x_i in the true model: K_{j x_i} = 0 for j != i and K_{i x_i} > 0. Then
every fiber point is a relabeling, and

    pi_i = q_{x_i}^2 / T_{x_i x_i}.

*Proof.* Let A be the gauge of a fiber point. Column x_i of K' = A K equals
A[:, i] K_{i x_i} >= 0, so A[:, i] >= 0 for every i, that is, A >= 0. Corollary A2
then makes A a permutation. Equivalently, C contains every coordinate ray, so C*
is the nonnegative orthant and O >= 0. The formula follows because
q_{x_i} = pi_i K_{i x_i} and T_{x_i x_i} = pi_i K_{i x_i}^2. QED.

For k = 2 the anchors are also necessary (Theorem B). For k >= 3 they are not
(ST-M89 below). This is the separability / anchor-word mechanism of Donoho and
Stodden (NeurIPS 2003) and Arora, Ge, Kannan and Moitra (STOC 2012); no priority
is claimed.

(ii) **Three views (cited).** The three-view tensor is
sum_i pi_i K_i (x) K_i (x) K_i. All three factor matrices (D_pi K, K, K) have
Kruskal rank k, and 3k >= 2k + 2 for k >= 2. By Kruskal (Linear Algebra Appl. 18
(1977) 95-138), the rank-k decomposition is unique up to permutation and
scaling, and row-stochasticity fixes the scaling (see also Allman, Matias and
Rhodes, Ann. Statist. 37 (2009) 3099-3132; Anandkumar, Ge, Hsu, Kakade and
Telgarsky, JMLR 15 (2014) 2773-2832, for "pairs identify up to rotation, triples
identify"). Any k-state alternative gives a rank-at-most-k decomposition, so it
is a relabeling. This part is cited, not reproved. **Model result ST-M86:** in
the k = 2 witness, the three-view tensors of the two fiber models already differ
at entry (0, 0, 0): 259/5400 versus 42413/772200, and
KL(P_true || P_alt) is about 0.00293 nats per triple (the reverse direction is
about 0.00288).

### Theorem F (ST-T305): a necessary condition for point identification

**Statement.** Suppose two views point-identify (pi, K) up to relabeling. Then
the row supports of K are pairwise incomparable: there are no i != j with
supp(K_j) contained in supp(K_i). For k = 2 this is exactly the two-anchor
condition of Theorem B.

*Proof.* Suppose supp(K_j) is contained in supp(K_i) for some i != j, and let O
be the rotation by a small angle theta > 0 in the (i, j) plane:
new row i = cos theta W_i - sin theta W_j, new row j = sin theta W_i + cos theta W_j,
other rows unchanged. Row j stays nonnegative because both terms are. In
row i, on columns where W_j = 0 the entry is cos theta W_ix >= 0; on columns
where W_jx > 0 we have W_ix > 0 (supports are nested), so the entry is
nonnegative once tan theta <= min over those columns of W_ix / W_jx. So
O is in G(W) for all small theta > 0. The new prior has
u_i = cos theta s_i - sin theta s_j, which varies with theta, so these fiber
points are not relabelings of (pi, K) for small theta > 0 (they converge to it
and are distinct). QED.

The check exhibits this with K = [[1/2, 1/4, 1/4], [1/2, 1/2, 0]] and the rational
angle tan(theta/2) = 1/50. Together with ST-M89, the exact characterization lies
between "pairwise-incomparable row supports" (necessary) and "sufficiently
scattered" (sufficient); see ST-O07.

### Model result ST-M89: a channel without anchors that two views point-identify

Take pi uniform on 3 latents and

    K = (1/8) [[0, 0, 1, 3, 1, 3], [1, 3, 0, 0, 3, 1], [3, 1, 3, 1, 0, 0]].

K is row-stochastic of rank 3, and no column is an anchor (every column has
exactly two nonzero entries). Since s is proportional to 1, the fiber condition
is O K >= 0. The extreme rays of C* = {y : y . K_col >= 0 for every column} are
e1, e2, e3, (1, 1, -1/3), (1, -1/3, 1) and (-1/3, 1, 1); the check enumerates all
pairwise intersections of facet planes exactly. Each satisfies y . 1 >= |y|, with
equality only at the coordinate rays. The function f(y) = y . 1 - |y| is
superadditive and positively homogeneous, so f >= 0 on all of C*, with equality
only on the coordinate rays. For an orthonormal frame (o_1, o_2, o_3) in C*,
sum_i o_i . 1 >= sum_i |o_i| = 3, while sum_i o_i . 1 = 1 . (O 1) <=
|O 1| |1| = 3 because O is orthogonal. So equality holds throughout. Writing
each o_i as a nonnegative combination of extreme rays, superadditivity forces
every ray used to be a coordinate ray and the triangle inequality forces them
to be parallel, so every o_i is a coordinate vector and O is a permutation: two
views point-identify this model. A rational Cayley grid agrees (0 of 2196 non-identity
points admissible).

This is an instance of the sufficiently scattered uniqueness theorem for
symmetric NMF (Huang, Sidiropoulos and Swami 2014; see also Fu, Huang,
Sidiropoulos and Ma, IEEE Signal Process. Mag. (2019), arXiv:1803.01257): when
cone(H^T) contains the second-order cone {x : 1 . x >= sqrt(k-1) |x|} (plus a
boundary condition), the factorization is essentially unique. Point
identification from two views is equivalent to essential uniqueness of the
symmetric NMF T = W^T W with the stochastic normalization.

## Theorem E (ST-T304, no learning inside the fiber; standard)

For n iid two-view pairs, the likelihood prod_t T[y_1t, y_2t] is a function of T
only. Consequences:

- For any two models in one fiber, the Bayes factor equals 1 for every dataset.
  This is the repository's core boundary BF = 1 (ST-T01), located inside a
  restricted, otherwise informative model.
- For any prior on the k-state parameter space, the posterior conditional on T
  equals the prior conditional on T. The posterior density relative to the
  prior is a sigma(T)-measurable function.

This is the standard "no learning about non-identified directions" fact (J. B.
Kadane, "The role of identification in Bayesian theory", in Fienberg and Zellner
(eds.), Studies in Bayesian Econometrics and Statistics, North-Holland 1974,
175-191; Dawid, J. R. Stat. Soc. B 41 (1979) 1-31; Poirier, Econometric Theory 14
(1998) 483-509); only its location inside the two-view fiber is new.

**Remark (cited, not proved here).** Under the regularity conditions of
Giacomini and Kitagawa (Econometrica 89 (2021) 1519-1556), namely a consistent
reduced-form posterior at the true T and continuity of the identified-set
correspondence there, the set of posterior means of the label-fixed functional
of Theorem B over all conditional priors on the fiber converges to [L, U]. For
an unlabeled pi_1 the limit is the convex hull of [L, U] union [1 - U, 1 - L].
It does not converge to a point. Moon and Schorfheide (Econometrica 80 (2012)
755-782) give the related single-prior statement. L and U are continuous on the
set of laws with q > 0 (ties between parallel columns are harmless), but they
can jump where an outcome probability tends to 0: with pi = (1/2, 1/2) and
K_eps = [[3/4 - eps, 1/4, eps], [1/4, 3/4, 0]], U = 1/2 for every eps > 0 (outcome 2
is an anchor), while at eps = 0 the outcome is dropped and U = 4/5 (checked
exactly). So the continuity condition must be checked at the true T.

## Finite check ST-F59

The check makes every decision in Fraction arithmetic. Floats are used only to
place probe points next to irrational arc endpoints and to report a KL value.

- **k = 2 witness:** equal one-view and two-view laws; unequal three-view laws;
  A has a negative entry and K' > 0; the converse recovers A and O from K'.
- **k = 3 Cayley witness:** signed A, K' > 0, equal two-view laws, unequal
  three-view laws; all three skew directions at Cayley parameter +-1/100 are
  admissible.
- **Theorem A' witness:** K1 != K2, a signed A, and
  B = [[38/35, -3/35], [2/35, 33/35]] != A; 49 of 49 gauges in the two-parameter
  grid are admissible; among the 25-point nonnegative product-gauge grid, only
  the two same permutations survive.
- **Theorem B:** a 201-point rational tan(theta/2) grid whose admissible points
  form a contiguous run containing 0, each reproducing T exactly with pi'_1 in
  [L, U] and pi'_1 strictly decreasing along the run; exact probes at distance
  1e-6 inside and outside both arc endpoints; exact anchor models at both
  endpoints; the doubly anchored case is a point; the one-anchor case is
  one-sided; the PR #68 pair is an endpoint model.
- **Theorem C:** anchored k = 3: none of 728 non-identity Cayley grid points is
  admissible, a cyclic permutation is admissible, and the anchor formula recovers
  pi.
- **Theorem D (k = 3):** exact floor 4/153 with an exact attainment certificate;
  the 9261-point grid of exact fiber models described above.
- **ST-M89 and Theorem F:** the extreme-ray certificate and the 2196-point grid
  for the scattered channel; the nested-support rotation; the jump of U.

## Relation to existing claim IDs

| Existing claim | Relation |
|---|---|
| ST-T254..T258, ST-M75/M76, ST-F46 (PR #63, one-view gauge) | The one-view gauge family {A : A 1 = 1} is (k^2 - k)-dimensional. The second view cuts it down to G(W), a subset of O(k) of dimension at most k(k-1)/2: full-dimensional when K > 0, possibly finite otherwise (ST-M89). |
| ST-T259 (two-view law) | Used as the definition of T. |
| ST-T261, ST-T263 (PR #64); P1-T7 (PR #69) | Corollary A2 recovers ST-T261 as "G(W) intersected with the nonnegative matrices consists of permutations". ST-T263's statement is correct but partial: two views shrink the fiber without collapsing it. Theorem A'(b) supplies the different-channel analogue that the P1-T7 nonclaims set aside. |
| ST-T262 (redrawn latent gives q (x) q) | Unchanged; complementary. |
| ST-M77..M79, ST-F47 | Their boundary witnesses all remain correct. ST-M87 adds a signed-gauge witness whose alternative channel K' is strictly positive; the existing PR #64 / PR #68 pair has an anchor zero. |
| R11.3 (PR #69) | R11.3 does not price the exclusion of signed A. Corollaries A1 and A2 do: the excluded set is a manifold of genuine stochastic models, and Theorem B gives its prior range. |
| PR #68 audit, finding 3 | A restatement of the PR #64 Section 6 signed pair. Theorem B shows that this pair is the L endpoint of the identified interval [1/5, 4/5]. |
| PR #62 (rowwise certificates) | Rowwise certificates assume a known or bounded channel. Theorem B is the unknown-channel two-view counterpart. |

Suggested paper wording: "Two shared-latent views identify (pi, K) only up to
the orthogonal fiber of Theorem A. For k = 2, point identification from two
views holds iff each latent has an anchor outcome. For every k, anchors (or,
more weakly, a sufficiently scattered channel) suffice, and a third view
suffices under Kruskal's condition. For a strictly positive channel the prior is
not even locally identified."

## Assumptions

1. Finite latent and outcome alphabets, with pi > 0.
2. K has full row rank k, and k is known.
3. The two views share one persistent latent state, are conditionally iid given
   it, and use the same channel. Theorem A' drops "same channel".
4. Exact population laws. There is no finite-sample estimation theory here.
5. Anchors in Theorem C(i) refer to the true channel.

## Nonclaims

- **Models with more states are not classified.** Alternatives with k' > k
  latent states are not classified; for example, splitting a state into
  identical copies enlarges the set of consistent weights. Alternatives with
  k' < k are impossible, because rank T = k.
- **No finite-sample results.** Theorem B gives no finite-sample confidence
  interval and no estimator.
- **Nothing for k >= 3 is sharp beyond the instance.** The k = 3 numbers are
  exact values attained by fiber models, an exact floor that is attained on this
  instance, and a non-certified float estimate of the maximum. No sharp k >= 3
  identified set is claimed.
- **Anchors are not necessary for k >= 3** (ST-M89), and the exact
  characterization of point identification is open (ST-O07).
- **Kruskal / three-view identifiability is cited, not reproved.**
- **The Giacomini-Kitagawa limit is a cited remark** under its own regularity
  conditions.
- **Novelty.** Theorem A(a) is in the repository already (PR #64 Section 6), the
  orthogonal-fiber form is the standard symmetric-NMF fact, A'(a) is in
  Henry-Kitamura-Salanie 2014 and Hall-Zhou 2003, and anchor sufficiency is
  known. The stochastic reparametrization, the explicit closed form of the
  k = 2 prior interval, the floor ell(T), the product-gauge rigidity A'(b) and
  the exact witnesses were not found stated in this form; no priority is
  claimed.
- **No bearing on simulation.** Nothing here is evidence for or against any
  simulation hypothesis. "Latent = simulated versus base" is an interpretation
  of the mixture model, not a finding.

## Open problems

**ST-O07.** Point identification and sharp sets for k >= 3:

1. **Exact characterization of point identification.** Known sufficient
   conditions: anchors (separability), and more weakly the sufficiently
   scattered condition of Huang, Sidiropoulos and Swami (2014), which they show
   is NP-complete to check. Known necessary condition: pairwise-incomparable row
   supports (Theorem F). The gap between them is open; see also the necessary
   and sufficient conditions studied by Laurberg et al. (2008).
2. **Sharp sets for k >= 3.** Characterize { (O s)^2 : O in O(k), O W >= 0 } for
   k >= 3: the orthonormal frames inside a polyhedral cone. On the k = 3 witness
   the float estimate of the largest label-free weight is about 0.746, while the
   generic bound 1 - 2 ell gives 0.948. Related work on rotational ambiguity:
   Borgen and Kowalski, Anal. Chim. Acta 174 (1985) 1-26.
3. **Finite samples.** Give finite-sample, uniformly valid confidence sets for
   [L, U]. The endpoints are min/max functionals, so they are non-smooth at ties.

## References

Verified during review: Huang, Sidiropoulos and Swami (2014); Henry, Kitamura
and Salanie (2014); Hall and Zhou (2003); Giacomini and Kitagawa (2021).
Recalled and not re-verified here: the remaining entries below.

- J. B. Kruskal, Linear Algebra Appl. 18 (1977) 95-138.
- E. S. Allman, C. Matias, J. A. Rhodes, Ann. Statist. 37 (2009) 3099-3132.
- A. Anandkumar, R. Ge, D. Hsu, S. M. Kakade, M. Telgarsky, JMLR 15 (2014) 2773-2832.
- S. Arora, R. Ge, R. Kannan, A. Moitra, STOC 2012 (separable NMF).
- D. Donoho, V. Stodden, NeurIPS 2003.
- Y. Kasahara, K. Shimotsu, Econometrica 77 (2009) 135-175.
- S. Bonhomme, K. Jochmans, J.-M. Robin, J. R. Stat. Soc. B 78 (2016) 211-229.
- W. H. Lawton, E. A. Sylvestre, Technometrics 13 (1971) 617-633.
- O. S. Borgen, B. R. Kowalski, Anal. Chim. Acta 174 (1985) 1-26.
- P. Laurberg et al., Comput. Intell. Neurosci. 2008, Article 764206.
- X. Fu, K. Huang, N. D. Sidiropoulos, W.-K. Ma, IEEE Signal Process. Mag. (2019).
- H. R. Moon, F. Schorfheide, Econometrica 80 (2012) 755-782.
- D. J. Poirier, Econometric Theory 14 (1998) 483-509.
- A. P. Dawid, J. R. Stat. Soc. B 41 (1979) 1-31.
- J. B. Kadane (1974), in Studies in Bayesian Econometrics and Statistics, 175-191.
- L. A. Goodman, Biometrika 61 (1974), latent class identifiability.
