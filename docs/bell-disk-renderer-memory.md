# Sharp renderer-memory constants on the Bell visibility-phase disk

Claims ST-T290 to ST-T296, ST-F58, ST-O05 and ST-O06
([manifest](../claims/bell-disk-renderer-memory-claims.json)). Certificate:
`src/simtheory/bell_disk_zonoid.py`, receipt
[`receipts/bell-disk-renderer-memory.txt`](../receipts/bell-disk-renderer-memory.txt),
tests in `tests/test_bell_disk_renderer_memory.py`.

Status: Theorems 1 to 5 and Proposition 7 are proved below; Theorem 6 is a
bracket, not an exact value. The hexagon sub-claim (the regular three-direction
schedule is optimal among three-direction schedules) is proved, not only
checked; it is the main new piece. Theorems 1, 3 and 4 combine classical
convex-geometry facts (attributed in each section). Four corrections to the
direction sketch are recorded in Section 9. The check certifies bounded
instances in exact arithmetic.

## 0. Setting and notation

- A **schedule** is a finite probability vector w on setting pairs j, with
  setting difference theta_j = alpha_x - beta_y and unit direction
  s_j = (cos theta_j, sin theta_j). Directions s and -s give the same line; a
  **direction class** is a line, carrying the summed weight. Settings are chosen
  by the experimenter with law w; the renderer cannot change w.
- The **target family** (ST-T11): for q = (v cos phi, v sin phi) in the closed
  unit disk D,
  P_q(j, a, b) = w_j (1 - ab s_j.q)/4, a, b in {-1, +1}.
  The correlator is E[ab | j] = -s_j.q. The sign convention never matters below.
- **Support function and polar body.** h_Z(x) = sum_j (w_j/2)|s_j.x| is the
  support function of the zonotope Z = sum_j (w_j/2)[-s_j, s_j]. Its polar is
  Z° = {x : h_Z(x) <= 1}, with area A_w = area(Z°). The schedule has **rank 2**
  when it has at least two direction classes (distinct classes are non-parallel
  by definition). Exactly then is h_Z a norm and Z° a bounded convex polygon.
- **Exact TV (ST-T11, ST-T15).** For one setting, TV between (1 - ab r)/4 and
  (1 - ab r')/4 is |r - r'|/2. Hence TV(P_q, P_q') = h_Z(q - q'), and the TV
  eps-ball around P_q inside the family is (q + eps Z°) intersected with D.
- **Perimeter.** Cauchy's formula, int_0^{2pi} |s.u_theta| d theta = 4, gives
  per(Z) = int_0^{2pi} h_Z(u_theta) d theta = sum_j (w_j/2)*4 = 2 for every
  schedule.
- **Renderer count.** N_w(eps) is the minimum number of renderer states k, each
  emitting ONE arbitrary probability law Q_k on (settings) x {-1,+1}^2, such
  that every q in D has some k with TV(P_q, Q_k) <= eps. Here Q_k need not
  belong to the family, need not have setting marginal w, and may be
  signalling. N^fam_w(eps) is the same quantity when each Q_k must equal P_p
  for some p in D. Clearly N_w <= N^fam_w, and log2 N_w lower-bounds the memory
  in bits of any one-trial eps-accurate renderer (ST-T05 logic).

## 1. Theorem 1 (arbitrary-center area converse)

**Statement.** For every rank-2 schedule w and every eps > 0,

  N_w(eps) >= pi / (A_w eps^2).

**Proof.**
*Step 1 (reduction to correlators).* Let Q be any law on (j, a, b). For signs
sigma in {-1,+1}^J, the test function f_sigma(j,a,b) = sigma_j ab satisfies
|f_sigma| <= 1, so 2 TV(P_q, Q) >= E_P f_sigma - E_Q f_sigma. Write
m_j = sum_{a,b} ab Q(j,a,b) and c_j = -m_j / w_j, a real number with
|c_j| <= Q(j)/w_j (the bound below holds for every real c). Then
E_P f_sigma - E_Q f_sigma = sum_j sigma_j w_j (c_j - s_j.q). Maximizing over
sigma gives

  TV(P_q, Q) >= g_c(q) := sum_j (w_j/2) |s_j.q - c_j|.

So the set of q served by Q lies in A_c = {q : g_c(q) <= eps} for some c in
R^J. Note g_0 = h_Z, so A_0 = eps Z°.

*Step 2 (the central set has maximal area: planar Brunn principle).* A_c is
closed and convex because g_c is convex. Also g_{-c}(-q) = g_c(q), so
A_{-c} = -A_c. For q in A_c and q' in A_{-c}, the triangle inequality termwise
gives
  h_Z((q+q')/2) = sum_j (w_j/2) |(s_j.q - c_j) + (s_j.q' + c_j)|/2
  <= (g_c(q) + g_{-c}(q'))/2 <= eps.
Hence (1/2)A_c + (1/2)(-A_c) is contained in A_0 = eps Z°. Since A_0 is bounded
under rank 2, A_c is bounded too. If A_c is nonempty, the Brunn-Minkowski
inequality in the plane gives

  area(A_0)^{1/2} >= (1/2) area(A_c)^{1/2} + (1/2) area(-A_c)^{1/2} = area(A_c)^{1/2}.

So area(A_c) <= eps^2 A_w. This is the planar case of Brunn's theorem that
central sections of a symmetric convex body are maximal: A_c is linearly
isomorphic to an affine section, parallel to range(S), of the weighted l1 ball
{u : sum_j (w_j/2)|u_j| <= eps}, and A_0 is the central section.

*Step 3 (counting).* If N states cover D, then D is contained in the union of
N sets A_{c_k}. Hence pi <= N eps^2 A_w. QED.

**Prior art.** The volumetric covering argument and Brunn's central-section
principle (equivalently Brunn-Minkowski, area((K - K)/2) >= area(K)) are
classical; the theorem is new only as applied to off-family Bell renderers.

**Comparison with packing.** The TV triangle inequality already makes the
ST-T05/ST-T13 packing argument valid for off-family emissions. For tiling Z°
(2 or 3 direction classes, including CHSH), an optimal packing already gives
pi/(A_w eps^2), so Theorem 1 adds nothing to the lower constant there; the
change from 1/16 to pi/32 is an improvement over ST-T13's inscribed-square
construction, not over packing in general. Theorem 1 strictly beats every
packing bound only for non-tiling Z° (4 or more classes): an optimized packing
yields delta(Z°) pi/(A_w eps^2), where delta is the translative packing
density, and delta < 1 for non-tiles. For the isotropic schedule (under the
setting-measurable extension of Section 6), delta = pi/sqrt12, so packing gives
1/(sqrt12 pi) ~ 0.0919 while Theorem 1 gives 1/pi^2 ~ 0.1013. All these
improvements are asymptotic.

## 2. Theorem 2 (sharp canonical CHSH count)

For canonical CHSH (ST-T12), h_Z(x) = ||x||_inf / (2 sqrt2) and
Z° = [-2 sqrt2, 2 sqrt2]^2, so A = 32. Let a = 4 sqrt2 eps. Let G(eps) be the
number of closed grid squares [ia,(i+1)a] x [ja,(j+1)a] meeting D. Let
G_bd(eps) be the number of those not contained in D.

**Statement.** For every eps > 0,

  pi/(32 eps^2) <= N_CHSH(eps) <= G(eps) <= pi (1 + 8 eps)^2 / (32 eps^2),

and for 0 < eps <= 1/8 (needed only for the annulus bound on G_bd)

  N^fam_CHSH(eps) <= G(eps) + 3 G_bd(eps) <= pi (1 + 8 eps)^2/(32 eps^2) + 3 pi/eps.

Hence log2 N_CHSH(eps) = 2 log2(1/eps) + log2(pi/32) + O(eps), and the same holds
for N^fam_CHSH. Off-family emissions do not change the leading constant.

**Proof.** The lower bound is Theorem 1 (for CHSH it also follows from ST-T05
packing and the square tiling). For the upper bound, a grid square with center
x is the l_inf ball of radius a/2, which is the TV ball of radius eps around x.

*Boundary fix (clipping).* Emit Q_x(a,b|j) = (1 - ab c_j)/4 with
c_j = clamp(s_j.x, -1, 1). This is a valid law even when x lies outside D. For
q in D, |s_j.q| <= 1, and clamping is the 1-Lipschitz projection onto [-1,1],
which fixes s_j.q. Therefore |c_j - s_j.q| <= |s_j.x - s_j.q|, so
TV(Q_x, P_q) <= h_Z(x - q) <= eps for every q in the square. The squares meeting
D cover D, so N <= G. Each such square lies in the disk of radius
1 + sqrt2 a = 1 + 8 eps, which gives G <= pi(1+8eps)^2/a^2.

*In-family version.* For squares contained in D the center is in D, so emit
P_center. Split each boundary square into 4 subsquares of side a/2, and emit
P_p for any p in (subsquare intersected with D). For q in the same piece,
||p - q||_inf <= a/2, so TV <= eps. Boundary squares meet the circle, so they
lie in the annulus 1 - 8eps <= |x| <= 1 + 8eps of area 32 pi eps, and
G_bd <= 32 pi eps / a^2 = pi/eps. QED.

ST-T13 gave the constructive packing lower bound ceil(1/(4eps))^2 ~ (1/16)
eps^-2; the sharp two-sided constant is pi/32 ~ 0.09817. The improvement is
asymptotic: at finite eps, ST-T13 can be larger (at eps = 3/25 it gives 9 while
pi/(32 eps^2) ~ 6.82), so the valid finite-eps lower bound is
max(ceil(1/(4eps))^2, ceil(pi/(32 eps^2))). The new part of Theorem 2 is the
matching upper bound for arbitrary and in-family emissions.

## 3. Theorem 3 (universal ceiling of the area converse)

**Statement.** For every finite schedule, A_w > pi^3 (strictly). For a rank-1
schedule the bound is trivial (convention A_w = +infinity). Consequently the
converse of Theorem 1 never exceeds (1/pi^2) eps^-2.

**Proof.** Z° has radial function rho(theta) = 1/h_Z(u_theta), so
A_w = (1/2) int_0^{2pi} h_Z^{-2} d theta. The map t -> t^{-2} is convex on
t > 0, and Jensen's inequality gives
(1/2pi) int h^{-2} >= ((1/2pi) int h)^{-2} = (per(Z)/2pi)^{-2} = pi^2. Hence
A_w >= pi^3. Equality requires h_Z to be constant a.e., hence everywhere by
continuity, which makes Z a disk. A finite zonotope is a polygon, so equality
is impossible. The isotropic generalized schedule (uniform setting
difference, under the setting-measurable extension of Section 6) attains
equality, with h_Z = |x|/pi and Z° the disk of radius pi; it is the only
generalized schedule that does, by injectivity of the cosine transform on even
measures on the circle (Schneider, Convex Bodies, 2nd ed. 2014, Sec. 3.5). QED.

**Prior art.** This is the classical polar-area/perimeter inequality
area(K°) >= 4 pi^3 / per(K)^2 specialized to per = 2; it is equivalent to
Lutwak's planar dual mixed-volume inequality (Pacific J. Math. 58 (1975)), and
is not claimed as new.

Correction: the sketch mentions a Blaschke-Santalo route. Blaschke-Santalo
bounds area(Z) area(Z°) from above, which is the wrong direction for a lower
bound on A_w. It is not used.

## 4. Theorem 4 (tiling schedules are exact)

**Statement.** Let w have exactly 2 or 3 direction classes. Then Z° is a
parallelogram or a centrally symmetric hexagon, and for every eps > 0

  pi/(A_w eps^2) <= N_w(eps) <= pi/(A_w eps^2) + 2 per(Z°)/(A_w eps) + 4.

So N_w(eps) eps^2 -> pi/A_w. The in-family count N^fam_w has the same limit.

**Proof.** h_Z is linear on the cones between the rays +-n_j, where n_j is s_j
rotated by 90 degrees. So Z° is the polygon with vertices +-n_j/h_Z(n_j), with
4 vertices for 2 classes and 6 for 3. Every parallelogram, and every centrally
symmetric hexagon with consecutive vertices V1, V2, V3, -V1, -V2, -V3, tiles the
plane by the lattice generated by V1+V2 and V2+V3. This is classical; see
Fedorov's classification of planar translative tiles, or Gruber, Convex and
Discrete Geometry (2007), Sect. 32. The check certifies the covolume identity
|det(V1+V2, V2+V3)| = area exactly on random rational hexagons.

Take that lattice tiling by eps Z°. If a tile x + eps Z° meets D, then x is in
D + eps Z°, so the tile lies in D + 2 eps Z°. Tiles have disjoint interiors, so
their number M satisfies
M eps^2 A_w <= area(D + 2 eps Z°) = pi + 2 eps per(Z°) + 4 eps^2 A_w. This is
Steiner's formula with the mixed area V(D, Z°) = per(Z°)/2. Emit clipped-center
laws as in Theorem 2; the same Lipschitz argument applies verbatim. Hence
N_w <= M. The lower bound is Theorem 1.

In-family: tiles with center in D emit P_center. Every point of D in another
tile lies in the strip partial D + eps Z°, which has area O(eps). Cover that
strip with the half-scale tiling by (eps/2)Z°, using any point of D in each
piece as an in-family center; TV is at most eps by the triangle inequality for
h_Z, because q - b is a contraction of q - x. These pieces lie in
partial D + 2 eps Z°, which has area O(eps), so there are O(1/eps) of them. QED.

**Prior art.** Lattice tiles and covering asymptotics for lattice tiles are
classical; the lower bound for tiling schedules also follows from ST-T05
packing. The new content is the matching for arbitrary (off-family) emissions
via Theorem 1 and clipping.

A rank-1 schedule (one class) has h_Z(x) = |s.x|/2, and clipped strip centers
give N_w(eps) <= ceil(1/(2 eps)), so N_w eps^2 -> 0 (A_w = +infinity).

## 5. Theorem 5 (optimal schedule with at most 3 direction classes)

**Statement.** (i) For two classes with weights w1, w2 and angle alpha between
them, A_w = 8/(w1 w2 sin alpha) >= 32. Equality holds iff w1 = w2 = 1/2 and
alpha = 90 degrees, which is CHSH up to rotation. (ii) For three classes,
A_w >= 18 sqrt3, with equality iff the weights are equal and the directions are
60 degrees apart. (iii) Hence, among rank-2 schedules with 2 or 3 direction
classes, the largest exact memory constant lim N_w eps^2 = pi/A_w is
pi/(18 sqrt3) ~ 0.10077. It is attained uniquely, as a law on direction classes
and up to rotation, by the regular three-direction schedule. A one-class
schedule has constant 0 (Section 4). CHSH (pi/32 ~ 0.09817) is optimal among
2-class schedules but not among 3-class ones.

A realization of the regular three-class law: Alice and Bob each choose
uniformly and independently from {0, pi/3, 2pi/3}. The setting differences then
put weight exactly 1/3 on each of the classes 0, 60 and 120 degrees (checked
exactly), and the schedule contains a CHSH configuration (Alice {0, 60},
Bob {0, 120}) with |S| = 5v/2 at phi = 0, which violates CHSH for v > 4/5. The
constants depend only on the class law w, not on whether a particular setting
realization admits a Bell violation: Alice {0} with Bob {0, -pi/3, -2pi/3}
realizes the same class law and admits none. No 2x2 product schedule realizes
the regular three-class law.

**Proof of (i).** Z is the parallelogram with edge vectors w1 s1 and w2 s2, so
area(Z) = w1 w2 sin alpha. Every parallelogram has Mahler product 8, since it is
a linear image of the square. Also w1 w2 <= 1/4 and sin alpha <= 1.

**Proof of (ii).** Order the classes by angle theta1 < theta2 < theta3 <
theta1 + pi. Let alpha = theta2 - theta1 and beta = theta3 - theta2, and set
gamma = pi - alpha - beta. These are the angles of a triangle. Put
a = sin alpha, b = sin beta, c = sin gamma = sin(alpha+beta), so that
|det(s1,s2)| = a, |det(s2,s3)| = b and |det(s1,s3)| = c.

*Closed form.* The polar vertices are V_i = n_i/h_i, with
  h1 = (w2 a + w3 c)/2, h2 = (w1 a + w3 b)/2, h3 = (w1 c + w2 b)/2.
The cyclic order is V1, V2, V3, -V1, -V2, -V3, and the shoelace formula gives
  A = det(V1,V2) + det(V2,V3) + det(V1,V3) = 4(a H3 + b H1 + c H2)/(H1 H2 H3), with H_i = 2 h_i.
The check verifies this exactly against the shoelace formula on random
rational-direction schedules.

*Substitution.* Put y1 = w1/b, y2 = w2/c, y3 = w3/a, Y = y1+y2+y3, and
q1 = y2+y3, q2 = y1+y3, q3 = y1+y2. Then
  a H3 + b H1 + c H2 = 2abc Y, H1 H2 H3 = (abc)^2 q1 q2 q3, and
  sum w = L := b y1 + c y2 + a y3 = 1.
Both sides are homogeneous, so A = 8 Y L^2/(abc q1 q2 q3).

*Triangle.* By the law of sines, a, b, c are the side lengths of a triangle T of
circumradius 1/2, so abc = 2 area(T). The Ravi substitution with r1, r2, r3 > 0
gives a = r1+r2, b = r2+r3, c = r1+r3, Heron's formula gives
area(T)^2 = (r1+r2+r3) r1 r2 r3, and L = q1 r1 + q2 r2 + q3 r3. Writing
X = (q1 r1, q2 r2, q3 r3),

  A = 2 (sum q)(sum X)^2 / (q1 q2 q3 sqrt((r1+r2+r3) r1 r2 r3)),

and A >= 18 sqrt3 is equivalent to

  (*) 243 X1 X2 X3 (X1 q2 q3 + X2 q1 q3 + X3 q1 q2) <= (sum q)^2 (sum X)^4.

*Lemma: (*) holds for all X > 0 and q >= 0, with equality iff X1=X2=X3 and
q1=q2=q3.* Normalize sum q = sum X = 1, and let f(q) = sum_i X_i q_j q_k on the
simplex.
- On the face q_k = 0, f <= X_k/4. Moreover 243 X1X2X3 X_k/4 <= 243/256 < 1,
  because X_k^2 X_i X_j <= 1/64 on the simplex by AM-GM.
- At an interior critical point, M q = lambda 1, where M is the matrix with zero
  diagonal and off-diagonal entries X. Since adj(M)1 = (X_i(X_j + X_k - X_i))_i,
  an interior critical point exists only when X satisfies the strict triangle
  inequalities, and then f = X1X2X3/Delta with
  Delta = 2 sum_{i<j} X_i X_j - sum X_i^2. It remains to show
  243 (X1X2X3)^2 <= Delta. The Ravi substitution on X (X1 = t2+t3,
  X2 = t1+t3, X3 = t1+t2, with t_i > 0) gives Delta = 4 e2 and
  X1X2X3 = s e2 - e3, where s = t1+t2+t3, e2 = t1t2+t2t3+t3t1 and e3 = t1t2t3.
  In homogeneous form the claim is 243 (s e2 - e3)^2 <= 64 s^4 e2. Normalize
  s = 1.
  - If e2 <= 64/243: 0 <= e2 - e3 <= e2, so 243 (e2-e3)^2 <= 243 e2^2 <= 64 e2.
  - If e2 >= 64/243 (> 3/25): Schur's inequality s^3 - 4 s e2 + 9 e3 >= 0 gives
    e2 - e3 <= (5 e2 + 1)/9. Then 243 (e2-e3)^2 <= 3 (5e2+1)^2, and
    3(5e2+1)^2 - 64 e2 = (3 e2 - 1)(25 e2 - 3) <= 0 for e2 in [3/25, 1/3], with
    e2 <= s^2/3 = 1/3 always.
  Equality forces e2 = 1/3, that is t1 = t2 = t3, so X is constant and the
  critical point is q = (1/3, 1/3, 1/3).
The maximum of f lies on a face or at an interior critical point, which proves
the lemma.

*Equality.* Equality in (*) needs X constant and q constant. Then y is constant
and r1 = r2 = r3, so T is equilateral, all angles are 60 degrees, a = b = c, and
w1 = b y1, w2 = c y2, w3 = a y3 are equal. QED.

**Proof of (iii).** Combine (i), (ii), Theorem 4, and 18 sqrt3 < 32.

**Novelty.** T5(ii), and the 2-class optimization in T5(i), are the new pieces.
The values 32, 18 sqrt3 and 384 sqrt2 - 512 equal per(P)^2 area(P°)/4 for the
regular 4-, 6- and 8-gon, which suggests that Theorem 5 is the n = 4, 6
centrally symmetric case of a discrete dual-isoperimetric inequality for
n-gons (ST-O06). We did not find it stated in the discrete isoperimetric
literature (L. Fejes Toth, Regular Figures, and Lagerungen in der Ebene, auf
der Kugel und im Raum), but the search was not exhaustive, so priority for
T5(ii) is not asserted.

## 6. Theorem 6 (bracket for general schedules; the tiling optimum is not global)

**Statement.** For every rank-2 schedule,

  pi/A_w <= liminf N_w(eps) eps^2 <= limsup N_w(eps) eps^2 <= lim N^fam_w(eps) eps^2 <= theta_L(Z°) pi/A_w <= 2/(sqrt27 pi) ~ 0.12252,

where theta_L is the lattice covering density. The regular four-direction
schedule has A_4 = 384 sqrt2 - 512 ~ 31.0580. This lies strictly between pi^3
and 18 sqrt3, which is certified with rational enclosures of sqrt2, sqrt3 and
pi. So liminf N_{reg4} eps^2 >= pi/A_4 ~ 0.10115 > pi/(18 sqrt3) =
lim N_{reg3} eps^2. **The regular hexagon schedule is therefore not the global
memory-forcing optimum.** The supremum over finite schedules of
liminf N_w eps^2 lies in [1/pi^2, 2/(sqrt27 pi)] = [0.10132, 0.12252]. The lower
end comes from the regular m-direction schedules, with
A_m = 4 m^3 tan^2(pi/2m) sin(pi/m) -> pi^3.

**In-family limit (classical).** For in-family emissions the served set of P_p
is D intersected with (p + eps Z°), so N^fam_w(eps) is the classical covering
number of D by translates of eps Z° with centers in D. The asymptotic covering
theorem (Rogers, Packing and Covering, Cambridge Tracts 54 (1964); Boroczky,
Finite Packing and Covering (2004)) gives
lim N^fam_w(eps) eps^2 = theta_T(Z°) pi/A_w, where theta_T <= theta_L is the
translative covering density; restricting centers to D costs only O(1/eps), by
the strip argument of Theorem 4. For centrally symmetric planar convex bodies
the literature states theta_T = theta_L = |K|/|h(K)|, where h(K) is a maximum-area
inscribed hexagon (L. Fejes Toth; Dowker, Bull. Amer. Math. Soc. 50 (1944)
120-122; stated in Kuperberg, Discrete Comput. Geom. (2013)), which would give
lim N^fam_w eps^2 = pi/|h(Z°)|. We cite this and have not verified the
theta_T = theta_L step; the bracket above uses only theta_T <= theta_L.

**Proof.** The lower bound is Theorem 1. For the upper bound, take a lattice
covering Lambda of the plane by Z° with density theta, which exists for
theta = theta_L since the infimum over lattices is attained. Count the points x
of eps Lambda in D + eps Z°: the translates x + eps V of the Voronoi cell are
disjoint and lie in D + eps(Z° + V), so the count is at most
pi/(eps^2 det Lambda) (1 + O(eps)) = theta pi/(A_w eps^2)(1 + O(eps)). Use
clipped centers as in Theorem 2 (or, in family, the strip argument). For
centrally symmetric convex discs, theta_L(K) <= 2 pi/sqrt27 with equality only
for ellipses (L. Fejes Toth, "Some packing and covering theorems", Acta Sci.
Math. (Szeged) 12A (1950) 62-67, and Lagerungen in der Ebene, auf der Kugel und
im Raum (1953), using E. Sas, Compositio Math. 6 (1939) 468-470); Z° is
centrally symmetric, so this applies. (Fary's bound, Bull. Soc. Math. France 78
(1950) 152-161, is theta_L <= 3/2 for general convex discs, with triangles
extremal; it is not the bound used here.) Theorem 3 gives pi/A_w <= 1/pi^2. QED.

For the isotropic generalized schedule, assume emissions are setting-measurable
conditional laws so that Step 1 of Theorem 1 holds with a measurable c(theta).
The bracket is then [1/pi^2, 2/(sqrt27 pi)] = [0.1013, 0.1225] (Kershner's disk
covering density 2pi/sqrt27, Amer. J. Math. 61 (1939) 665-671).

## 7. Proposition 7 (local and global design rankings separate)

The per-trial Fisher matrix in q is I(q) = sum_j w_j s_j s_j^T/(1 - (s_j.q)^2),
because the four-outcome Fisher information about a correlator r is
1/(1-r^2). At the disk center I(0) = sum_j w_j s_j s_j^T. Its trace is 1, so
lambda_min(I(0)) <= 1/2, with equality iff I(0) = I/2. CHSH and all regular
m-direction schedules (m >= 2) attain I/2 exactly: for theta_k = k pi/m,
sum_k cos(2 theta_k) = sum_k sin(2 theta_k) = 0, so
(1/m) sum_k s_k s_k^T = I/2 (checked exactly in Q(sqrt2) and Q(sqrt3) for
m <= 4). They are therefore simultaneously E-, A- and D-optimal and tied at the
center. Their finite-deviation covering constants nevertheless differ:
pi/32 < pi/(18 sqrt3) < pi/A_4 <= liminf for reg-4. Local Fisher optimality does
not rank Bell schedules for renderer-memory forcing. This is an elementary
design-optimality computation and is not claimed as new.

## 8. Finite check ST-F58

The check uses only the standard library. Every certifying assertion is exact,
over Fraction or Q(sqrt d). It certifies:

- (a) A = 32 with Mahler product 8 for CHSH. The 4-setting support function
  equals the 2-class one at probe points. A = 18 sqrt3 with Mahler product 9 for
  regular-3, and A = 384 sqrt2 - 512 for regular-4, with pi^3 < A_4 < 18 sqrt3.
  The center Fisher matrix is I/2 for all three.
- (b) For eps = 1/n, n = 40, 80, ..., 400, exact integer grid counts satisfy
  ceil(pi_lo n^2/32) <= G <= pi_hi (1+8/n)^2 n^2/32 and G_bd <= pi n. The ratio
  G/(pi n^2/32) falls from 1.222 to 1.018. In 2465 exact (cell, point in D)
  pairs with n in {8, 20, 40}, including boundary cells, the clipped centers
  achieve TV <= eps.
- (c) 120 random rational off-plane CHSH correlator vectors give exact served-set
  areas equal to the closed form (t^2 - dU^2 - dV^2)/2 with t = 8 eps, and these
  are always <= 32 eps^2. 40 random rational-direction 3- and 4-class schedules
  satisfy central area = eps^2 A_w and off-center area <= central area.
- (T3) 60 random rational schedules with 2 to 6 classes all have A > pi_hi^3.
- (d) 80 random rational 3-schedules: shoelace area equals the closed form, the
  tiling covolume identity holds, and A^2 > 972. A 62468-case rational grid of
  direction triples and weights gives min A ~ 31.17919 > 18 sqrt3 ~ 31.17692.
  2000 random rational instances of the lemma (*) and of the final symmetric
  inequality are nonnegative, with equality at the regular point.
- The trine product schedule has class weights (1/3, 1/3, 1/3) and a CHSH
  sub-test with |S| = 5v/2 (exact), and at eps = 3/25 the ST-T13 count 9 exceeds
  pi/(32 eps^2).

Rational unit directions ((1-t^2)/(1+t^2), 2t/(1+t^2)) make every polar area
exactly rational. The finite check corroborates the proofs; it is not the
proof.

## 9. Corrections to the direction sketch

1. "It handles off-family renderer outputs, which the packing argument left
   open" is inaccurate. Packing via the TV triangle inequality already handles
   arbitrary emissions. What is new is the matching upper bound, the sharp
   constant for tiling schedules, and a converse that beats packing for
   non-tiling Z°.
2. The hexagon sub-claim is true and now proved, but "CHSH is not the
   memory-forcing optimum even among tiling schedules" should be paired with a
   further fact: the regular hexagon is not the global optimum either, since the
   regular 4-direction schedule has a strictly larger certified lower constant.
3. Section 3 replaces the candidate Blaschke-Santalo chain with Jensen plus
   Cauchy.
4. The Delft estimate: main now carries the Delft 2015 receipts (ST-F50,
   ST-F51). S = 2.422 implies v >= 2.422/(2 sqrt2) ~ 0.856 (about 0.78 at
   S - 1 sd), because |S| <= 2 sqrt2 v; this is a lower bound on v, not an
   estimate. No constant here depends on it.

## 10. Assumptions

Single-trial predictive TV. Externally randomized settings with a fixed law w.
The coplanar visibility-phase law of ST-T11. The target set is all of D. A
renderer state emits one fixed law. Classical theorems are cited, not
reproved: Brunn-Minkowski in R^2, Cauchy's perimeter formula, Schur's
inequality, Fedorov's classification of planar lattice tiles, the L. Fejes Toth
lattice covering bound for centrally symmetric discs (via Sas), the asymptotic
covering theorem, and Kershner's disk covering density.

## 11. Nonclaims

- The exact constant (and the existence of lim N_w eps^2) for arbitrary
  (off-family) emissions when Z° does not tile is open (ST-O05). The in-family
  constant is classical (Section 6).
- No claim about n-trial, adaptive, or transcript-level renderers (cf. ST-M05,
  ST-T14); n-fold TV is not h_Z.
- Clipped-center emissions are valid probability tables but need not be
  quantum-realizable. Quantum realizability matters only for the in-family
  count, which has the same leading constant for tiling schedules.
- The constants depend only on the law w on direction classes, not on whether a
  given setting realization admits a Bell violation (Section 5).
- No claim that a parent simulator stores classical bits, and no claim beyond
  the declared two-parameter coplanar family.
- The finite checks are bounded corroboration, not proofs of the asymptotic
  statements.

## 12. Relation to repository claim IDs

Builds on ST-T05 (packing lower bound), ST-T11 (exact family TV), ST-T12 (CHSH
l_inf metric, A = 32), ST-T13 (constructive packing lower bound 1/16, improved
asymptotically to pi/32; at finite eps the valid lower bound is the maximum of
the two), ST-T15 (rank-2 criterion = Z° bounded), ST-M04 (Fisher rank,
Proposition 7 at the center), ST-T56 and ST-T68 (arbitrary-center covers;
Theorem 1 is their two-dimensional Bell analogue), ST-M05 (finite-horizon only,
not extended). It settles a non-adaptive, one-trial, two-parameter special case
of the question behind ST-O01; ST-O01 remains open.

## 13. Open problems

- **ST-O05.** The exact renderer constant (and existence of the limit) for
  arbitrary emissions when Z° is not a tile (4 or more direction classes,
  including the isotropic schedule): only pi/A_w <= liminf and
  limsup <= theta_L(Z°) pi/A_w are known.
- **ST-O06.** Is per(P)^2 area(P°) >= 2 n^3 tan^2(pi/n) sin(2 pi/n) for every
  convex n-gon P containing the origin, with equality for regular n-gons? The
  centrally symmetric n = 4 and n = 6 cases are Theorem 5(i),(ii) (with per = 2,
  the left side over 4 is A_w). Float experiments during review (20000 random
  n-gons for each n = 3..6) found no violation; nothing is proved, and the
  literature has not been searched thoroughly. If true, the regular
  four-direction schedule would be optimal among schedules with at most 4
  classes.
