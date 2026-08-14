# Shared-randomness coding against continuous total-variation prior balls

## Scope

The deterministic TV-robust lane chooses one zero-error binary prefix codebook
before an unknown source law is selected from

\[
\mathcal U_{\mathrm{TV}}(p,\rho)
=
\{q\in\Delta_{n-1}:\operatorname{TV}(q,p)\le\rho\}.
\]

This lane adds one explicit assistance resource: encoder and every decoder share
a source-independent random seed that selects a complete deterministic
codebook before the source state is encoded.

The timing is essential. The principal model is:

1. a codebook distribution is fixed;
2. the source law is selected from the TV ball independently of the realized
   seed;
3. the shared seed selects one deterministic zero-error codebook;
4. the source state is drawn and encoded;
5. every receiver decodes using the same seed.

The source-law adversary is **oblivious to the realized seed**. A separate model
in which the source law may depend on that seed is derived later and has a
different value.

The completed result is finite, one-shot, rational, binary-prefix,
common-message, and zero-error. It does not price the random bits needed to
sample a non-dyadic mixture, infer a TV radius from data, prove queueing or hard
cut guarantees, or provide evidence for simulation or parent-level physical
costs.

---

## 1. Codebook mixtures collapse to expected state lengths

Let the complete bounded deterministic code universe be

\[
\mathcal C=\{c_1,\ldots,c_m\}.
\]

Each codebook has a state-length vector

\[
\ell^{(c)}
=
\bigl(\ell^{(c)}_1,\ldots,\ell^{(c)}_n\bigr).
\]

Every selected codebook is independently verified to be a proper zero-error
confusion-graph partition with a complete binary prefix tree.

Let

\[
x\in\Delta_{m-1}
\]

be the shared codebook mixture. Conditional on the seed, zero error remains
exact. Under source law \(q\), expected communication is

\[
\sum_c x_c E_q[\ell^{(c)}].
\]

By bilinearity,

\[
\sum_cx_cE_q[\ell^{(c)}]
=
E_q\left[\sum_cx_c\ell^{(c)}\right].
\]

Define the mixed expected state-length vector

\[
\boxed{
z(x)=\sum_cx_c\ell^{(c)}.}
\]

The entire oblivious-adversary payoff depends on the codebook mixture only
through \(z(x)\):

\[
\boxed{
\sup_{q\in\mathcal U_{\mathrm{TV}}(p,\rho)}
\sum_cx_cE_q[\ell^{(c)}]
=
\sup_{q\in\mathcal U_{\mathrm{TV}}(p,\rho)}E_q[z(x)].
}
\]

The right-hand side is exactly the rational TV mass-transport problem solved in
the preceding lane. This gives an independent continuous replay of any finite
game solution.

---

## 2. Event characterization of a finite TV ball

For finite laws \(p,q\), let

\[
D_i=q_i-p_i.
\]

The coordinates sum to zero. If

\[
S_+=\{i:D_i>0\},
\]

then

\[
\sum_{i\in S_+}D_i
=
\frac12\sum_i|D_i|
=
\operatorname{TV}(p,q).
\]

No event can have a larger signed difference, because including a negative
coordinate only lowers the sum. Therefore

\[
\boxed{
\operatorname{TV}(p,q)
=
\max_{S\subseteq[n]}[q(S)-p(S)]
=
\max_{S\subseteq[n]}|q(S)-p(S)|.
}
\]

Thus the TV ball has the exact event halfspace description

\[
\boxed{
-\rho
\le
q(S)-p(S)
\le
\rho
\qquad\forall S\subseteq[n].
}
\]

The empty and full events are trivial. An event and its complement produce the
same absolute constraint, because

\[
q(S^c)-p(S^c)
=-[q(S)-p(S)].
\]

One representative from each nontrivial complement pair is sufficient. The
implementation chooses the unique representative containing state zero and
retains both signs.

After eliminating the final coordinate

\[
q_n=1-\sum_{i<n}q_i,
\]

every event mass is affine in \(q_1,\ldots,q_{n-1}\). Together with simplex
nonnegativity, the TV ball is a bounded rational polytope in dimension
\(n-1\).

For \(n>1\), the checker uses

\[
\boxed{
n+2(2^{n-1}-1)
}
\]

inequalities:

- \(n\) simplex facets;
- two signs for each of \(2^{n-1}-1\) event-complement pairs.

This exponential description is exact and intentionally bounded. It is not
presented as a scalable high-dimensional representation.

---

## 3. Exact TV-ball vertex enumeration

A linear objective over a nonempty bounded polytope reaches its maximum and
minimum at a vertex.

In a \(d\)-dimensional rational polytope, every vertex has at least \(d\) active
facets whose coefficient rows contain a linearly independent subset of size
\(d\). Degenerate vertices may have more active constraints, but they still
contain such a basis.

Here

\[
d=n-1.
\]

The exact bounded vertex checker therefore:

1. enumerates every \(d\)-subset of event and simplex inequalities;
2. solves the corresponding square rational system;
3. rejects singular systems;
4. checks every inequality exactly;
5. reconstructs the eliminated final probability;
6. independently recomputes total variation;
7. deduplicates equal distributions.

The certificate records:

- every halfspace and label;
- ambient dimension;
- candidate, examined, and nonsingular basis counts;
- every vertex distribution;
- one independent active basis for each vertex;
- state and basis caps.

At radius zero, the vertex set is exactly the nominal prior. At radius one, the
TV ball is the full simplex and its vertices are exactly the deterministic
point masses.

---

## 4. Exact reduction of the continuous game to a finite game

The oblivious shared-randomness value is

\[
\boxed{
V_{\mathrm{mix}}^{\mathrm{TV}}
=
\min_{x\in\Delta(\mathcal C)}
\sup_{q\in\mathcal U_{\mathrm{TV}}(p,\rho)}
q^Tz(x).
}
\]

Let the exact TV-ball vertices be

\[
v^{(1)},\ldots,v^{(R)}.
\]

For fixed \(x\), the payoff is linear in \(q\), so

\[
\sup_{q\in\mathcal U}q^Tz(x)
=
\max_{1\le r\le R}(v^{(r)})^Tz(x).
\]

Expanding \(z(x)\), define the rational matrix

\[
A_{rc}
=(v^{(r)})^T\ell^{(c)}.
\]

Then

\[
\boxed{
V_{\mathrm{mix}}^{\mathrm{TV}}
=
\min_{x\in\Delta_m}
\max_r\sum_cx_cA_{rc}.
}
\]

The continuous distributional game is exactly the finite zero-sum game between:

- codebook columns;
- TV-polytope vertex rows.

The existing exact support solver enumerates primal and dual bases, checks every
omitted inequality, and requires an exactly zero rational duality gap.

### Safe code pruning

A deterministic codebook whose cost is no smaller at every TV vertex is
dominated throughout the entire TV ball, because every law in the ball is a
convex combination of vertices. Equal vertex-cost vectors are also equivalent
throughout the ball. Retaining one canonical representative and removing only
Pareto-dominated vectors is therefore exact for both deterministic and mixed
robust optimization.

---

## 5. Continuous mass-transport replay

The finite game returns a codebook mixture \(x^*\). The checker independently
forms

\[
z^*=\sum_cx_c^*\ell^{(c)}
\]

and applies the exact continuous TV transport solver directly:

\[
\widehat V
=
\sup_{q:\operatorname{TV}(q,p)\le\rho}q^Tz^*.
\]

The certificate requires

\[
\boxed{
\widehat V
=V_{\mathrm{game}}
}
\]

as an exact rational equality.

This comparison is structurally independent of vertex enumeration:

- the finite game uses event halfspaces and active-set vertices;
- the replay uses ordered donor-recipient mass transport.

Agreement provides two distinct constructions of the same continuous optimum.

The replay also returns an explicit worst-case source distribution for the
mixed code's expected state lengths.

---

## 6. Least-favorable prior identity

The dual finite-game mixture assigns weights

\[
y_r\ge0,
\qquad
\sum_ry_r=1
\]

to TV vertices. Its barycenter is

\[
\boxed{
\bar q
=
\sum_ry_rv^{(r)}.
}
\]

Because the TV ball is convex,

\[
\bar q\in\mathcal U_{\mathrm{TV}}(p,\rho).
\]

For one deterministic codebook,

\[
\sum_ry_rA_{rc}
=
\bar q^T\ell^{(c)}.
\]

The dual objective is therefore

\[
\max_y\min_c\bar q^T\ell^{(c)}.
\]

The complete deterministic code universe contains every proper partition and
complete prefix tree. Minimizing under fixed \(\bar q\) is exactly nominal
prior-weighted zero-error coding:

\[
\min_c\bar q^T\ell^{(c)}
=L^*(G,\bar q).
\]

Finite-game primal-dual equality yields

\[
\boxed{
V_{\mathrm{mix}}^{\mathrm{TV}}
=
\max_{q\in\mathcal U_{\mathrm{TV}}(p,\rho)}
L^*(G,q).
}
\]

Thus shared codebook randomness closes the minimax gap between:

- selecting a mixture before the law is known;
- selecting a least-favorable prior in the TV ball and then evaluating its
  nominal zero-error coding optimum.

The checker computes \(\bar q\), reruns the independent nominal solver, and
requires

\[
L^*(G,\bar q)=V_{\mathrm{mix}}^{\mathrm{TV}}
\]

exactly.

This identity is for expected length, one-shot shared codebook randomness, and
the declared convex TV set. It is not transferred to peak length, queueing,
private randomness, or a seed-dependent source law.

---

## 7. Exact Caratheodory support compression

The finite-game solver bounds codebook support by the number of TV vertices,
which can be exponential in the number of source states. The payoff structure
gives a sharper dimension-dependent representation.

### Codebook support

A codebook mixture matters only through

\[
z=\sum_cx_c\ell^{(c)}\in\mathbb Q^n.
\]

By Caratheodory's theorem, every point in the convex hull of vectors in
\(\mathbb Q^n\) is a convex combination of at most

\[
\boxed{n+1}
\]

of them.

### Least-favorable vertex support

A source prior lies in the affine simplex plane

\[
\sum_iq_i=1,
\]

which has dimension \(n-1\). Using the first \(n-1\) coordinates, the same
theorem represents the least-favorable prior with at most

\[
\boxed{n}
\]

TV vertices.

### Constructive exact elimination

Suppose a convex representation in \(\mathbb Q^d\) has more than \(d+1\)
positive weights. Select \(d+2\) active points. They are affinely dependent, so
there exists nonzero rational \(\alpha\) with

\[
\sum_j\alpha_j=0,
\qquad
\sum_j\alpha_jv_j=0.
\]

The coefficients contain both signs. Let

\[
t
=
\min_{\alpha_j>0}\frac{w_j}{\alpha_j}.
\]

Update

\[
w'_j=w_j-t\alpha_j.
\]

Then:

- every new weight is nonnegative;
- the weights still sum to one;
- the barycenter is unchanged;
- at least one positive weight becomes zero.

Repeating yields the support bounds above.

The implementation performs exact rational row reduction, records every affine
dependence and elimination step, and verifies the original and reduced
barycenters exactly.

These support bounds price neither the entropy nor the exact random-bit cost of
the shared seed. They bound only the number of deterministic codebooks or TV
vertices that need positive probability.

---

## 8. Adversary timing theorem

The oblivious value is

\[
V_{\mathrm{obliv}}
=
\min_x
\sup_{q\in\mathcal U}
\sum_cx_cE_q[\ell^{(c)}].
\]

Now consider a stronger adversary that observes the realized codebook seed and
may choose a different source law \(q_c\) for each selected codebook. For fixed
mixture \(x\), its value is

\[
\sum_cx_c
\sup_{q\in\mathcal U}E_q[\ell^{(c)}].
\]

Let

\[
R(c)=\sup_{q\in\mathcal U}E_q[\ell^{(c)}].
\]

Then

\[
\min_x\sum_cx_cR(c)
=
\min_cR(c),
\]

because a convex combination cannot be below its smallest component, and a
point mass attains the minimum.

Therefore

\[
\boxed{
V_{\mathrm{seed\text{-}observing}}
=V_{\mathrm{det}}^{\mathrm{TV}}.
}
\]

Shared codebook randomness can help only when the source law cannot condition on
the realized seed.

The certificate reports both:

- the oblivious mixed value;
- the selected mixture's seed-observing cost;
- the optimal seed-observing value, equal to deterministic robustness.

This timing distinction is not philosophical decoration. It changes the exact
mathematical game.

---

## 9. Closed full-radius solution for every complete graph

Let the confusion graph be \(K_n\). Every state needs a distinct message.
At TV radius one, the uncertainty set is the full simplex, so an oblivious
adversary facing mixed expected state lengths \(z\) chooses a state of maximum
length:

\[
\sup_{q\in\Delta_{n-1}}q^Tz
=\max_i z_i.
\]

Let

\[
b=\lceil\log_2n\rceil.
\]

### Lower bound

For any mixed code,

\[
\max_i z_i
\ge
\frac1n\sum_i z_i.
\]

The right side is the codebook-mixture average of deterministic trees' uniform
average leaf depths.

The uniform-source optimal binary prefix tree has:

\[
a=2^b-n
\]

leaves at depth \(b-1\), and

\[
n-a=2n-2^b
\]

leaves at depth \(b\). This is the uniform Huffman tree. Its minimum total leaf
depth is

\[
\begin{aligned}
T_n
&=a(b-1)+(n-a)b\\
&=n(b+1)-2^b.
\end{aligned}
\]

Therefore every mixed code satisfies

\[
\max_i z_i
\ge
\frac{T_n}{n}
=
\boxed{b+1-\frac{2^b}{n}}.
\]

### Achievability

Take one near-balanced optimal length vector with \(a\) short leaves and cyclically
shift the assignment across the \(n\) states. Mix uniformly over the \(n\)
shifts. Every state is short in exactly \(a\) shifts and long in the other
\(n-a\), so every mixed state length is

\[
\frac{a(b-1)+(n-a)b}{n}
=b+1-\frac{2^b}{n}.
\]

The adversary sees a constant vector and cannot do better by changing the source
law.

Thus the exact shared-randomness full-TV value is

\[
\boxed{
V_{\mathrm{mix}}^{K_n,\rho=1}
=b+1-\frac{2^b}{n}.
}
\]

The deterministic value is

\[
V_{\mathrm{det}}^{K_n,\rho=1}=b.
\]

The exact gain is

\[
\boxed{
V_{\mathrm{det}}-V_{\mathrm{mix}}
=\frac{2^b-n}{n}.
}
\]

The gain is zero exactly when \(n\) is a power of two. Otherwise the cyclic
construction uses at most \(n\) codebooks and strictly improves worst-law
expected length while leaving the hard message alphabet and deterministic peak
length unchanged.

For \(n=3\),

\[
V_{\mathrm{mix}}=\frac53,
\qquad
V_{\mathrm{det}}=2.
\]

---

## 10. Skew three-state phase transition

Let \(G=K_3\) and nominal prior

\[
p=
\left(
\frac45,
\frac1{10},
\frac1{10}
\right).
\]

There are three complete trees, each placing one state at depth one and the
other two at depth two. Let \(x_i\) be the probability of shortening state
\(i\). The mixed state lengths are

\[
z_i=2-x_i.
\]

Because states one and two have equal nominal probability, symmetrizing their
codebook weights cannot worsen the convex robust objective. Set

\[
x_1=x_2=\frac{1-a}{2},
\qquad
x_0=a.
\]

Allocating less short-code probability to the high-probability state than to
each low-probability state, \(a<1/3\), already gives nominal cost above the
uniform mixture's \(5/3\). It cannot be optimal. Hence consider

\[
\frac13\le a\le1.
\]

The mixed lengths are

\[
z_0=2-a,
\qquad
z_1=z_2=\frac32+\frac a2.
\]

For the relevant radii, the TV adversary moves mass from state zero to states
one or two. The nominal expectation is

\[
E_p[z]
=
\frac{19}{10}-\frac7{10}a.
\]

The value gap is

\[
z_1-z_0
=
\frac{3a-1}{2}.
\]

Thus

\[
R_\rho(a)
=
\frac{19}{10}-\frac\rho2
+a\left(
-\frac7{10}+\frac{3\rho}{2}
\right).
\]

The coefficient of \(a\) changes sign at

\[
-\frac7{10}+\frac{3\rho}{2}=0,
\]

so the exact threshold is

\[
\boxed{
\rho_c=\frac7{15}.
}
\]

Therefore:

- for \(0\le\rho<7/15\), choose \(a=1\): the deterministic tree shortening
  state zero is optimal, with value

  \[
  \frac65+\rho;
  \]

- at \(\rho=7/15\), every \(a\in[1/3,1]\) is optimal at value \(5/3\);
- for \(\rho>7/15\), choose \(a=1/3\): the uniform codebook mixture gives the
  constant length vector \((5/3,5/3,5/3)\).

Hence

\[
\boxed{
V_{\mathrm{mix}}^{\mathrm{TV}}(\rho)
=
\begin{cases}
\frac65+\rho,&0\le\rho\le\frac7{15},\\
\frac53,&\frac7{15}\le\rho\le1.
\end{cases}
}
\]

At \(\rho=1/2\), deterministic robustness is \(17/10\), shared robustness is
\(5/3\), and the exact gain is

\[
\boxed{\frac1{30}}.
\]

The finite solver's stable tie-break may return one deterministic codebook at
the exact crossing even though the uniform mixture is also optimal there.

---

## 11. Certificate contents

The shared continuous-TV certificate contains:

- exact nominal prior and radius;
- the complete event-halfspace list;
- every TV-ball vertex and active basis;
- basis counts and caps;
- the complete bounded nondominated deterministic code frontier;
- exact vertex-by-code cost matrix;
- deterministic robust reference value;
- exact primal codebook mixture;
- exact dual vertex mixture;
- zero rational game gap;
- mixed expected state-length vector;
- independent continuous mass-transport replay;
- explicit continuous worst-case source law;
- least-favorable barycenter prior;
- independent nominal coding optimum at that prior;
- selected-mixture and optimal seed-observing costs;
- exact Caratheodory reductions of both mixtures.

---

## 12. Independent audits

The tests:

1. verify radius-zero and radius-one TV vertex sets;
2. compare exact vertex maxima with mass transport on seeded rational
   three-state instances;
3. verify full-TV \(K_3\) value \(5/3\);
4. verify the skew-\(K_3\) threshold \(7/15\);
5. replay continuous transport and least-favorable nominal oracle equality on
   every labeled three-vertex graph;
6. compare event inequalities with denominator-ten simplex grids;
7. verify adversary timing changes the exact value;
8. verify exact Caratheodory barycenter preservation on seeded rational points;
9. verify the complete-graph closed formula for one through sixteen states and
   compare \(K_3\) with the generic game solver;
10. fail closed on state, active-set, candidate, and game-basis caps.

---

## 13. Boundaries and next questions

This lane does not establish:

- a statistical confidence theorem for the nominal prior or radius;
- exact random-bit cost for sampling rational codebook mixtures;
- private-randomness gains without a communicated codebook identity;
- a source law correlated with the realized seed under the oblivious value;
- minimax regret against the continuous TV ball;
- KL, Wasserstein, moment, or general polyhedral ambiguity;
- allowed-error or lossy function computation;
- block graph products or asymptotic graph entropy;
- queueing, buffer, or hard network-cut guarantees;
- quantum variable-length codebook mixtures;
- parent-level resource claims or evidence for simulation.

The next exact extensions should:

1. solve general rational polyhedral prior ambiguity with primal-dual receipts;
2. construct finite-sample confidence polytopes and time-uniform confidence
   sequences that feed robust code design;
3. add continuous minimax regret, whose oracle baseline is concave and changes
the adversary geometry;
4. quantify exact seed entropy and finite random-bit generation;
5. move from zero-error graphs to allowed-error loss structures.
