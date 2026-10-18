// Identification, evidence caps, and the price of shared randomness
// Compile: python figures.py && python build.py (see README.md)

#let ink = rgb("#1c2230")
#let accent = rgb("#2c5d8f")
#let soft = rgb("#f3f5f8")
#let citedfill = rgb("#f6f4ef")
#let citedrule = rgb("#a67c1a")

#let shorttitle = [Identification, evidence caps, and shared randomness]
#set document(title: "Identification, evidence caps, and the price of shared randomness", author: "Jaden Fix")
#set page(
  paper: "us-letter",
  margin: (x: 1.05in, top: 1in, bottom: 1in),
  numbering: "1",
  header: context {
    if counter(page).get().first() > 1 [
      #set text(size: 8.5pt, fill: luma(110))
      #shorttitle #h(1fr) J. Fix
    ]
  },
)
#set text(font: "New Computer Modern", size: 10.5pt, fill: ink, lang: "en")
#set par(justify: true, leading: 0.6em, spacing: 0.95em, first-line-indent: (amount: 1.1em, all: false))
#set heading(numbering: "1.1")
#show heading.where(level: 1): it => block(above: 1.5em, below: 0.85em, text(size: 12.5pt, weight: "bold", it))
#show heading.where(level: 2): it => block(above: 1.2em, below: 0.7em, text(size: 11pt, weight: "bold", it))
#set math.equation(numbering: "(1)")
#show link: set text(fill: accent)
#show ref: set text(fill: accent)
#show figure.caption: it => {
  set text(size: 9pt)
  set par(justify: true, first-line-indent: 0em)
  set align(left)
  block(width: 100%, inset: (x: 0.2em))[#text(weight: "bold")[#it.supplement #context it.counter.display(it.numbering).] #it.body]
}
#set figure(gap: 0.9em)
#set place(clearance: 1.6em)
#show figure: set block(above: 1.4em, below: 1.4em)
#set table(stroke: none)
#show table.cell: set text(size: 9pt)
#show table.cell: set par(justify: false)
#show figure.where(kind: table): set figure.caption(position: top)
#set footnote.entry(separator: line(length: 30%, stroke: 0.5pt + luma(150)))
#show footnote.entry: set text(size: 8.5pt)

// claim IDs never break across lines
#let id(x) = box(text(fill: accent, x))
// equation references as "(3)"
#let eqref(l) = [(#ref(l, supplement: none))]

// claim-typed result blocks ---------------------------------------------------
// Header: "<Kind> (<claim ID or source>). <Name>." No running number: every
// cross-reference uses the claim ID.
#let result(kind, id: none, name: none, cited: false, breakable: false, body) = {
  block(
    width: 100%,
    inset: (left: 9pt, right: 8pt, y: 7pt),
    fill: if cited { citedfill } else { soft },
    stroke: (left: 1.4pt + if cited { citedrule } else { accent }),
    breakable: breakable,
    above: 1.05em,
    below: 1.05em,
  )[
    #set par(first-line-indent: 0em)
    #text(weight: "bold")[#kind]#if id != none [ #box(text(weight: "bold", fill: if cited { citedrule } else { accent })[(#id)])]#if name != none [ #emph(name).] else [.]
    #body
  ]
}
#let theorem = result.with("Theorem")
#let corollary = result.with("Corollary")
#let model = result.with("Model result")
#let fcheck = result.with("Finite check")
#let standard = result.with("Standard result", cited: true)
#let cited = result.with("Cited theorem", cited: true)
#let openp = result.with("Open problem")
// the QED square never collides with a full last line: it stays at least
// 0.6em from the text and, if it wraps, is right-aligned on the next line
#let proof(body, name: "Proof sketch") = block(above: 0.6em, below: 1em)[
  #set par(first-line-indent: 0em)
  #emph(name). #body#h(0.6em)#box()#h(1fr)$square$
]
#let KL = math.op("KL")
#let dm(x) = math.equation(block: true, numbering: none, x)
#let diag = math.op("diag")
#let supp = math.op("supp")
#let upi = math.upright(math.pi)

// title -----------------------------------------------------------------------
#align(center)[
  #v(0.4em)
  #text(size: 17pt, weight: "bold")[Identification, evidence caps,\ and the price of shared randomness]
  #v(0.2em)
  #text(size: 11.5pt)[Orthogonal two-view fibers, persistent-latent evidence,\ and exact fair-bit costs in finite games]
  #v(0.9em)
  #text(size: 10.5pt)[Jaden Fix] \
  #text(size: 9pt)[Tempera #h(0.6em) #link("mailto:Jaden@Tempera.dev")[Jaden\@Tempera.dev]] \
  #v(0.2em)
  #text(size: 9pt, fill: luma(90))[October 2026 #h(0.6em)·#h(0.6em) results from #link("https://github.com/jadenfix/simulation-theory")[github.com/jadenfix/simulation-theory] at commit `aa61193`]
]
#v(0.6em)

#block(inset: (x: 2.2em))[
  #set text(size: 9.5pt)
  #set par(first-line-indent: 0em, leading: 0.58em)
  #text(weight: "bold")[Abstract.]
  We collect three exact finite results from a public claim ledger in which every statement has an ID, a type and an executable certificate; their shared lesson is to separate what an observable law identifies from what evidence or randomness can buy. (i) Given the population law, across independent world draws, of two views of one persistent latent state through a common channel, the consistent models form an orthogonal fiber, a stochastic reparametrization of the standard orthogonal ambiguity of symmetric factorizations. A strictly positive channel leaves the prior not even locally identified; for two latent states we give a closed form of the Henry-Kitamura-Salanié bounds for a shared channel. (ii) Hypotheses that differ only in world-level weights $a, b$ over a shared kernel yield at most $KL(a || b)$ nats of expected evidence per world draw (data processing); we bound the shortfall by the MAP error. (iii) The mixed value $V^*$ of a finite rational game is reached by some finite number of public fair bits iff some optimal mixture is dyadic; otherwise the $b$-bit gap is $Theta(2^(-b))$, and the least expected cost is the Knuth-Yao cost minimized over the optimal set. The gain from randomizing over three prefix codes costs the classical $8\/3$-bit Knuth-Yao cost of a uniform ternary choice. Nothing here is evidence for or against the hypothesis that reality is simulated.
]

= Introduction

The simulation hypothesis @bostrom2003 is usually argued about with priors and counting. A prior question is what an observer inside a world could learn at all. The repository behind this paper @simtheory takes that question literally, and its first theorem fixes the boundary: if a simulator produces exactly the observable law of an ordinary physical model, every test has power equal to its size and the Bayes factor is one on every data set (#id[ST-T01], an elementary fact recorded for this setting). Everything else in the ledger lives on the other side of that boundary. One declares a _restricted_ simulator, derives the law it can produce, and asks whether, how fast, and at what cost the difference can be seen. Proposed signatures of finite resources, such as lattice artifacts @beane2014, are of this restricted kind.

This paper collects three results from that program. They share one lesson: what an observable law identifies is a different question from what evidence or randomness can buy, and in the models below each question has an exact finite answer.

_Identification._ Arguments about simulation often posit a latent "world type" drawn once (base or simulated, or which of several simulators), followed by many observations of that one draw. Whether data can then update beliefs about the population of world types depends on whether the mixture of world types and their observation laws is identified by the law of the observations. Section 3 parametrizes the answer exactly for the shared-latent two-view design, solves it in closed form for two latent states, and gives a certified floor and a necessary condition for $k >= 3$ (the sharp set is open, #id[ST-O07]). The identification question presumes access to the population law of (view 1, view 2) across independent world draws; an observer confined to one draw sees only $K[M, dot]$ for its own $M$. Section 4 makes this quantitative: evidence about world-level weights accrues per world draw, not per observation.

_Randomness._ A decision maker facing an unknown world can lower its worst-case loss with a coin that carries no information about the world. Such gains are coordination value, not learning, but they are real, and the ledger had left their cost open. Section 5 answers the direct question: what does exact shared randomness cost, in fair bits, when the optimal mixture is not dyadic?

The two halves meet in one question that this paper does not answer (Section 7): the fair-bit cost of reaching a target value in a game played against a whole identified set rather than a declared finite list of scenarios.

#heading(numbering: none, level: 2)[Contributions]

Each result is listed with its claim ID; Section 2 explains the types.

+ *The two-view fiber* (#id[ST-T297–ST-T305], #id[ST-M86–ST-M89], #id[ST-F59]). An orthogonal parametrization of all models sharing a two-view law; local non-identification for every strictly positive channel; the sharp closed-form identified interval for $k = 2$; a certified positive floor on every latent weight; product-gauge rigidity for different channels; a necessary condition for point identification; and exact witnesses, including a no-anchor channel that two views still identify.
+ *The persistent-latent cap* (#id[ST-T277–ST-T280], #id[ST-F55], with #id[ST-T273] for contrast). Expected evidence about world-level weights is at most $KL(a || b)$ per world draw (data processing, standard); the shortfall is an exact posterior-disagreement term with a zero-gap characterization; a new bound controls the shortfall by the MAP error.
+ *The price of shared randomness* (#id[ST-T310–ST-T313], #id[ST-M90–ST-M93], #id[ST-F61]). An (elementary) dyadic dichotomy, a two-sided $Theta(2^(-b))$ gap with no nondegeneracy assumption, the composition of the Knuth-Yao sampler with the optimal set, the analogue for $L$-sided coins, and exact curves and prices for the ledger's committed games.

Appendix A records how these results re-read earlier ledger entries.#footnote[The same repository merge also added Bell-scenario results and the fresh-draw half of the evidence dichotomy (#id[ST-T272–ST-T276]). They are outside the scope of this paper, except that Section 4 uses #id[ST-T273] as a contrast.]

= Two-view setting, notation and claim types

*Persistent latent, channel, views.* There are $k$ latent states with prior $pi$ in the open simplex, and a row-stochastic $k times d$ channel $K$ of full row rank $k$. One latent $M tilde pi$ is drawn once and emits observations that are conditionally i.i.d. given $M$ with law $K[M, dot]$. Write $D_v = diag(v)$. The one- and two-view laws are
$ q = K^top pi, quad quad T = K^top D_pi K quad (#id[ST-T259]). $
Put $s = sqrt(pi)$ entrywise and $W = D_s K$. Then $T = W^top W$, $W bb(1) = s$, $|s| = 1$, and for the column $w_x$ of $W$: $s dot w_x = q_x$ and $|w_x|^2 = T_(x x)$. The _two-view fiber_ of $(pi, K)$ is the set of $k$-state models $(pi', K')$ with $K'^top D_(pi') K' = T$. Throughout, $k$ is fixed and known; alternatives with more latent states are not classified. Latents are indexed $1, dots, k$ and outcomes $1, dots, d$ (the repository indexes outcomes from 0).

*Notation.* The letter $pi$ always denotes a prior; the circle constant appears only inside constants, written upright ($ln(upi\/2)$ in #eqref(<eq:kt>)), and angles are in degrees. $T$ is always the two-view matrix: transcript lengths and trial counts are $n$, and stopping times (numbers of fair bits consumed) are $tau$. In Section 5 the game matrix is $Gamma$, and $K_3$ names the complete confusion graph on three source states, not a channel.

*Claim types.* The ledger types every claim. A _theorem_ (`ST-T`) follows from its stated assumptions. A _model result_ (`ST-M`) is exact inside one declared model or example. A _finite check_ (`ST-F`) is a reproducible computation on an explicitly bounded domain. An _open problem_ (`ST-O`) is a target, not a conclusion. Results that are classical carry the label _standard_ in the ledger, and results from the literature that are used but not reproved are _cited_. In this paper, blue blocks are the repository's own claims (theorems, model results, finite checks and open problems), and amber blocks are standard or cited results; the block header names the type and then the claim ID or the source. Proofs are given in full or sketched, with pointers to `docs/` in the repository @simtheory, where every step is written out; each result has a module in `src/simtheory/`, a test file, and a committed receipt that a test compares byte for byte.

*What is not claimed.* No result here is evidence for or against simulation. "Latent = simulated versus base" is an interpretation of a mixture model, not a finding. Where a result is known, the ledger and this paper say so, and novelty is claimed only for the stated forms, with no claim of priority.

= The two-view orthogonal fiber

== Classification

#theorem(id: "ST-T297", name: "Fiber classification")[
  Let $pi > 0$ and let $K$ be row-stochastic of full row rank $k$.
  + $(pi', K')$ is in the two-view fiber iff $K' = A K$ for a unique invertible $A$ with $A bb(1) = bb(1)$, $A^top D_(pi') A = D_pi$ and $A K >= 0$; then $pi' = A^(-top) pi$.
  + Let $G(W) = {O in O(k) : O W >= 0 "entrywise"}$. The map
    $ O |-> (pi', K'), quad u = O s, quad pi' = u dot.o u, quad K' = D_u^(-1) O W $
    is a bijection from $G(W)$ onto the fiber, and $u > 0$ holds automatically. Two elements $O, O'$ give models that differ only by relabeling iff $O' = P O$ for a permutation matrix $P$.
  + Equivalently, the fiber is in bijection with the ordered orthonormal frames contained in the dual cone $C^* = {o : o dot w_x >= 0 "for all" x}$ of the column cone $C = "cone"{w_x}$.
]
#proof[
  Since $T = W^top W$ has rank $k$ and column space $"row"(K)$, any fiber point has $pi' > 0$ and $"row"(K') = "row"(K)$, which gives $K' = A K$; cancelling a right inverse of $K$ in $K^top (A^top D_(pi') A - D_pi) K = 0$ gives (1). For (2), if $O W >= 0$ then $u = O W bb(1) >= 0$, and $u_i = 0$ would make row $i$ of $O W$ vanish, impossible for invertible $O$ and full-rank $W$. Then $A = D_u^(-1) O D_s$ satisfies $A bb(1) = bb(1)$ and $A^top D_u^2 A = D_s O^top O D_s = D_pi$. Conversely $O = D_(sqrt(pi')) A D_s^(-1)$ is orthogonal exactly when $A^top D_(pi') A = D_pi$. Part (3) restates $o_i dot w_x >= 0$. Full proof: `docs/two-view-orthogonal-fiber.md`, Theorem A.
]

*Credit.* Part (1) is already in the repository (`docs/latent-mixture-two-view-rigidity.md`, Section 6), and that two rank-$k$ factorizations $T = W^top W$ differ by an orthogonal matrix is the standard symmetric-NMF fact @huang2014 @laurberg2008. The new content is the stochastic reparametrization $u = O s$, $pi' = u dot.o u$, $K' = D_u^(-1) O W$, which turns statements about the fiber into statements about orthonormal frames in a polyhedral cone.

#corollary(id: "ST-T298", name: "Strictly positive channels are not even locally identified")[
  If $K > 0$ entrywise and $k >= 2$, then $G(W)$ contains a neighborhood of $I$ in $O(k)$, so the fiber contains a $k(k-1)\/2$-dimensional manifold of models that are not relabelings of each other, and the set of consistent priors ${(O s)^2 : O in G(W)}$ contains an open neighborhood of $pi$ in the simplex.
]
#proof[
  $O W > 0$ is an open condition that holds at $O = I$. The orbit map $"SO"(k) -> S^(k-1)$, $O |-> O s$, is a submersion, hence open, and squaring is a local homeomorphism near $s > 0$.
]

#corollary(id: "ST-T299", name: "What the earlier rigidity theorem excludes")[
  $A = D_u^(-1) O D_s >= 0$ iff $O >= 0$, and a nonnegative orthogonal matrix is a permutation. Hence the nonnegative-gauge rigidity theorem of the ledger (#id[ST-T261]\; P1-T7 of the companion paper @fixcompanion) is exactly the statement that $G(W)$ meets the nonnegative matrices only in permutations.
]

So #id[ST-T261] remains correct as scoped, but its scope excludes every non-permutation point of $G(W)$, which for a strictly positive channel is the whole manifold of #id[ST-T298]. Nonnegativity of $A$ is sufficient, not necessary, for $A K$ to be a stochastic channel: in the witness #id[ST-M87] below, $A$ has a negative entry and $K' = A K > 0$.

#theorem(id: "ST-T300", name: "Different channels per view")[
  Let $T = K_1^top D_pi K_2$ with $K_1, K_2$ row-stochastic of full row rank $k$. (a) Every fiber point is $(pi', A K_1, B K_2)$ with $A bb(1) = B bb(1) = bb(1)$, $pi' = A^(-top) pi$ and $B = D_(pi')^(-1) A^(-top) D_pi$; the signed parameter set is an open subset of the affine space ${A : A bb(1) = bb(1)}$, which has dimension $k^2 - k$. (b) _Product-gauge rigidity:_ if moreover $A >= 0$ and $B >= 0$, then $A = B = P$ for one permutation $P$.
]
#proof[
  For (b), take $j != l$: $0 = (D_pi)_(j l) = sum_i pi'_i A_(i j) B_(i l)$ with nonnegative terms, so $A_(i j) B_(i l) = 0$. Fix $i$ and $j$ with $A_(i j) > 0$; then row $i$ of $B$ is $e_j$, and a second positive entry in row $i$ of $A$ would force $B_(i j) = 0$. Invertibility makes $i |-> j$ a permutation.
]

*Credit.* Part (a) and its dimension count are known: the different-channel model is the setting of Henry, Kitamura and Salanié @henry2014, and Hall and Zhou @hall2003 show that the bivariate two-component case is identified only up to a two-parameter family. Only (b) is claimed. The same-channel fiber is the slice $A = B$, which is why its dimension drops from $k(k-1)$ to $k(k-1)\/2$.

== The sharp identified interval for two latent states

For $k = 2$, drop outcomes with $q_x = 0$ and set $c_x = q_x^2 \/ T_(x x) in (0, 1]$. The _extreme pair_ ${x^*, y^*}$ minimizes $T_(x y)^2 \/ (T_(x x) T_(y y))$; it is the pair of columns $w_x, w_y$ spanning the widest angle, and it is observable. In any fiber model, the latent _favored by_ $x^*$ is the latent $i$ with the larger ratio $K'_(i x^*) \/ K'_(i y^*)$ (a zero denominator reads as $+infinity$). Columns $x^*$ and $y^*$ are not parallel in any fiber model, so this convention labels every fiber model; we call the favored latent latent 1.

#theorem(id: "ST-T301", name: [Sharp identified set, $k = 2$])[
  With latent 1 favored by $x^*$, the identified set of the prior weight $pi'_1$ is exactly
  $ [L, U] = [1 - q_(y^*)^2 / T_(y^* y^*), quad q_(x^*)^2 / T_(x^* x^*)]. $ <eq:interval>
  The endpoints are rational in $T$ on each region where the extreme pair is fixed and continuous on the laws with $q > 0$. $U$ is attained by the unique fiber model in which $x^*$ is an anchor for latent 1, and $L$ by the model in which $y^*$ is an anchor for latent 2. Without a label convention the identified set of $pi_1$ is $[L, U] union [1 - U, 1 - L]$. Finally $L = U$ iff each latent has an anchor outcome in the true model.
]
#proof[
  Up to relabeling the fiber is ${R_theta : R_theta W >= 0}$. If the columns have angles $phi_x in [0 degree, 90 degree]$ with extremes $phi_min < phi_max$, a rotation keeps every column in the quadrant iff $theta in [-phi_min, 90 degree - phi_max]$, an arc containing $0$. Along it $pi'_1 = cos^2(psi + theta)$, with $psi$ the angle of $s$, is strictly decreasing, so its image is an interval whose endpoints are $cos^2(psi - phi_min)$ and $1 - cos^2(phi_max - psi)$. Since $cos angle(s, w_x) = q_x \/ sqrt(T_(x x))$, these are $c_(x^*)$ and $1 - c_(y^*)$. At $theta = -phi_min$ the column $x^*$ lies on an axis, so it is an anchor. The point case is $phi_min = 0 degree$ and $phi_max = 90 degree$.
]

*Credit.* The interval #eqref(<eq:interval>) specializes the sharp two-component bounds of Henry, Kitamura and Salanié @henry2014 (their Theorem 1) to a shared channel, and "rotate until a component touches zero" is the feasible-band construction of Lawton and Sylvestre @lawton1971 in multivariate curve resolution. Only the explicit closed form for the prior weight is offered.

#model(id: "ST-M87", name: "An exact witness with a strictly positive alternative channel")[
  Take $pi = (9/25, 16/25)$ and $K = mat(1/2, 1/4, 1/4; 1/6, 1/3, 1/2)$. Then $q = (43/150, 91/300, 41/100)$, the extreme pair is $(x^*, y^*) = (1, 3)$, and
  $ [L, U] = [144/1825, 1849/2425] approx [0.0789, 0.7625], $
  around the true $0.36$. The rotation with $cos theta = 24/25$, $sin theta = 7/25$ gives $pi' = (1936/15625, 13689/15625)$, the signed gauge $A = mat(18/11, -7/11; 7/39, 32/39)$, and the strictly positive channel $K' = mat(47/66, 13/66, 1/11; 53/234, 149/468, 71/156)$, with identical one- and two-view laws.
]

#figure(
  placement: top,
  image("figures/fig_fiber_k2.pdf", width: 100%),
  caption: [The $k = 2$ fiber of #id[ST-M87]. (a) The columns $w_x$ of $W = D_(sqrt(pi)) K$ span the blue cone. Rotations keep all columns in the quadrant until one reaches an axis (green and rust cones); the image $u = O s$ of $s$ moves along the unit circle (dots at the two extremes). (b) The prior weight $pi'_1 = cos^2(psi + theta)$, with $psi$ the angle of $s$, along the admissible arc $theta in [-0.418, 0.359]$ rad (about $-24.0 degree$ to $20.6 degree$) sweeps out the identified interval $[L, U]$ (shaded). Black dots are exact fiber models on the rational grid $tan(theta\/2) in {j\/200 : |j| <= 100}$, each checked in rational arithmetic to reproduce $T$ (79 of the 201 grid points are admissible, #id[ST-F59]); the curve is the closed form. The endpoints are the anchor models.],
) <fig:k2>

@fig:k2 shows the geometry. The endpoint models are explicit: $K'_U = mat(97/258, 145/516, 59/172; 0, 3/8, 5/8)$ and $K'_L = mat(5/6, 1/6, 0; 59/246, 155/492, 73/164)$. A boundary pair recorded earlier in the ledger (prior $(1/5, 4/5)$ against the symmetric channel with prior $(1/2, 1/2)$) is exactly the $L$-endpoint model of its interval $[1/5, 4/5]$, and a channel with one anchor gives a one-sided interval ($[9/25, 289/325]$ in #id[ST-F59]).

== A certified floor for every $k$, and the recovery ladder

For general $k$ the identified set is not known in closed form (#id[ST-O07]), but the cone picture yields a floor.

#theorem(id: "ST-T302", name: "Weight floor")[
  Let $ell(T) = min_(o in C^*, |o| = 1) (o dot s)^2 = min_nu (nu dot s)^2 \/ |nu|^2$ over the extreme rays $nu$ of $C^*$. Then $ell(T)$ depends only on $T$, $0 < ell(T) <= min_i pi_i$, and every model in the two-view fiber has $pi'_i >= ell(T)$ for all $i$, hence $pi'_i <= 1 - (k - 1) ell(T)$. For $k = 2$, $ell(T) = min(L, 1 - U)$ is the exact minimum latent weight.
]
#proof[
  Two factors of $T$ differ by an orthogonal $Q$ that moves $C^*$ and $s$ together. The vector $s$ is a strictly positive combination of the generators of the full-dimensional cone $C$, so it lies in its interior and $o dot s > 0$ on $C^* without {0}$. Rows of $O in G(W)$ are unit vectors in $C^*$ and $pi'_i = (o_i dot s)^2$. The minimum over a cone of $(o dot s)^2\/|o|^2$ is attained on an extreme ray.
]

#model(id: "ST-M88", name: "Three latent states")[
  For
  #dm($pi = (1/9, 4/9, 4/9), quad K = mat(1/2, 1/4, 1/8, 1/8; 1/8, 1/2, 1/4, 1/8; 1/8, 1/8, 1/4, 1/2)$)
  the floor is $ell = 4/153 approx 0.0261$, and it is attained by an exact orthonormal frame in $C^*$, so the smallest latent weight over this fiber is exactly $4/153$. A 9261-point rational Cayley grid contains 197 admissible points, each an exact fiber model; the different-channel witness of #id[ST-T300] is also exact.
]

The grid's extreme label-free weights, $784/23409 approx 0.0335$ and $1369/2025 approx 0.676$, are attained by exact fiber models. They bound the range of the sharp set from inside but do not determine it, and a float scan suggests a largest label-free weight near $0.746$ against the outer bound $1 - 2 ell approx 0.948$ (not certified). @fig:k3 shows the consistent priors in the simplex for this channel and two contrasting ones.

#theorem(id: "ST-T303", name: "Two views plus anchors identify")[
  If each latent $i$ has an anchor outcome $x_i$ in the true model ($K_(j x_i) = 0$ for $j != i$, $K_(i x_i) > 0$), then every fiber point is a relabeling, and $pi_i = q_(x_i)^2 \/ T_(x_i x_i)$. For $k = 2$ anchors are also necessary.
]
#proof[
  Column $x_i$ of $A K$ is $A[:, i] K_(i x_i) >= 0$, so $A >= 0$, and #id[ST-T299] makes $A$ a permutation. Necessity for $k = 2$ is the point case of #id[ST-T301].
]

This is the separability (anchor-word) mechanism of Donoho and Stodden @donoho2003 and Arora, Ge, Kannan and Moitra @arora2012; no priority is claimed. For $k >= 3$ anchors are not necessary:

#model(id: "ST-M89", name: "Point identification without anchors")[
  With $pi$ uniform on three states and
  #dm($K = 1/8 mat(0, 0, 1, 3, 1, 3; 1, 3, 0, 0, 3, 1; 3, 1, 3, 1, 0, 0)$)
  no outcome is an anchor, yet two views identify $(pi, K)$ up to relabeling. The extreme rays of $C^*$ are $e_1, e_2, e_3$ and the three permutations of $(1, 1, -1\/3)$; each satisfies $y dot bb(1) >= |y|$ with equality only on the coordinate rays, and an orthonormal frame in $C^*$ must then consist of coordinate vectors.
]

This is an instance of the sufficiently scattered uniqueness theorem for symmetric NMF @huang2014 @fu2019; point identification from two views is equivalent to essential uniqueness of the symmetric factorization $T = W^top W$ with the stochastic normalization. A necessary condition holds for all $k$.

#theorem(id: "ST-T305", name: "A necessary condition for point identification")[
  If two views point-identify $(pi, K)$ up to relabeling, then no row support of $K$ is contained in another: there are no $i != j$ with $supp(K_j) subset.eq supp(K_i)$. For $k = 2$ this is exactly the two-anchor condition.
]
#proof[
  If $supp(K_j) subset.eq supp(K_i)$, rotate rows $i, j$ of $W$ by a small $theta > 0$: row $j$ becomes $sin theta W_i + cos theta W_j >= 0$, and row $i$ becomes $cos theta W_i - sin theta W_j$, which is nonnegative once $tan theta <= min_(x : W_(j x) > 0) W_(i x) \/ W_(j x)$ (positive by the support inclusion). These fiber points converge to the true model, are distinct from it, and change $u_i$, so they are not relabelings.
]

#figure(
  placement: auto,
  image("figures/fig_fiber_k3.pdf", width: 100%),
  caption: [Consistent priors for three latent states, in the simplex with vertices $e_i$ (star: true prior). (a) Strictly positive channel of #id[ST-M88]: a compact, label-symmetric region with nonempty interior, containing a neighborhood of $pi$ (#id[ST-T298]). Blue: a Haar float scan of $O(3)$ ($3 times 10^6$ draws, 27,064 admissible), shown for illustration only and not a certificate. Black: the 197 exact fiber models of the rational Cayley grid in #id[ST-F59]. Dashed: the certified floor $pi'_i >= ell(T) = 4\/153$ (#id[ST-T302]). (b) The anchored channel $K$ with rows $(1\/2, 0, 0, 1\/2)$, $(0, 2\/3, 0, 1\/3)$ and $(0, 0, 3\/4, 1\/4)$, with the same prior (outcomes 1 to 3 are anchors): only relabelings survive (#id[ST-T303]), and a float scan of $2 times 10^5$ Haar draws finds no admissible point, as expected for a finite fiber. (c) The scattered channel of #id[ST-M89] with uniform prior: point identified without anchors.],
) <fig:k3>

The third rung of the ladder is cited, not reproved.

#cited(id: [Kruskal @kruskal1977], name: "Three views identify")[
  The three-view tensor $sum_i pi_i K_i times.o K_i times.o K_i$ has factor matrices $D_pi K, K, K$ of Kruskal rank $k$, and $3k >= 2k + 2$ for $k >= 2$, so the rank-$k$ decomposition is unique up to permutation and scaling; row-stochasticity fixes the scaling. See also @allman2009 @anandkumar2014.
]

#model(id: "ST-M86", name: "The third view separates the witness pair")[
  In the $k = 2$ witness of #id[ST-M87], the three-view laws of the true and alternative models already differ at entry $(1, 1, 1)$: $259/5400$ against $42413/772200$, with $KL(P_"true" || P_"alt") approx 0.00293$ nats per triple.
]

@tab:ladder collects the rungs of the ladder.

#figure(
  placement: auto,
  table(
    columns: (1fr, 1.45fr, auto),
    align: (left, left, left),
    inset: (x: 5pt, y: 3.5pt),
    table.hline(stroke: 0.6pt),
    table.header([*Data*], [*What is identified*], [*Claims*]),
    table.hline(stroke: 0.4pt),
    [one view $q$], [a row-stochastic gauge family of dimension $k^2 - k$], [#id[ST-T254–ST-T258]],
    [two views, $K > 0$], [only up to $G(W) subset O(k)$, a $k(k-1)\/2$-dimensional set; prior not locally identified], [#id[ST-T297], #id[ST-T298]],
    [two views, $k = 2$], [the interval #eqref(<eq:interval>)\; a point iff both latents have anchors], [#id[ST-T301], #id[ST-T303]],
    [two views, any $k$], [floor $ell(T)$; point identification needs incomparable supports], [#id[ST-T302], #id[ST-T305]],
    [two views + anchors, or sufficiently scattered $K$], [point (up to labels)], [#id[ST-T303]\; cited @huang2014 \ (instance #id[ST-M89])],
    [three views], [point (up to labels), by Kruskal's theorem], [cited @kruskal1977],
    table.hline(stroke: 0.6pt),
  ),
  caption: [The identification ladder for one persistent latent observed repeatedly through a common channel.],
) <tab:ladder>

== No learning inside the fiber

#standard(id: "ST-T304", name: "Bayes factor one inside the fiber")[
  For $n$ i.i.d. two-view pairs the likelihood $product_t T[y_(1 t), y_(2 t)]$ depends on the model only through $T$. Hence any two models in one fiber have Bayes factor one on every data set, and for any prior on $k$-state models the posterior given $T$ equals the prior given $T$.
]

This is the standard "no learning about non-identified directions" fact @dawid1979 @poirier1998; only its location inside the two-view fiber is new. It is the ledger's boundary #id[ST-T01] reappearing inside a restricted, otherwise informative model. A cited remark completes the picture: under the regularity conditions of Giacomini and Kitagawa @giacomini2021 (a consistent reduced-form posterior and continuity of the identified-set correspondence at the true $T$), the set of posterior means of the label-fixed weight over all conditional priors on the fiber converges to $[L, U]$, not to a point; Moon and Schorfheide @moon2012 give the related single-prior statement. The continuity condition is not automatic. With $pi = (1/2, 1/2)$ and $K_epsilon$ with rows $(3\/4 - epsilon, 1\/4, epsilon)$ and $(1\/4, 3\/4, 0)$, $U = 1/2$ for every $epsilon > 0$ (outcome 3 is an anchor) while $U = 4/5$ at $epsilon = 0$; #id[ST-F59] confirms this exactly.

#fcheck(id: "ST-F59", name: "Exact fiber audit")[
  In rational arithmetic: the $k = 2$ witness and its converse; a 201-point rational grid around the arc (79 admissible), with probes at distance $10^(-6)$ inside and outside both endpoints; anchored $k = 3$ (none of 728 non-identity Cayley points admissible); the 9261-point $k = 3$ grid and the exact floor certificate; the different-channel grids (49 of 49 signed gauges admissible; only the two common permutations survive among 25 nonnegative product gauges); the scattered channel (0 of 2196 non-identity points); the nested-support rotation; and the jump of $U$.
]

= The persistent-latent cap: the evidential counterpart

Section 3 asked which hypotheses the observable law can separate at all. This section asks how much evidence can accumulate when the hypotheses differ only in how likely each world is. Let $M$ take values in a standard Borel space, let $a, b$ be two laws of $M$ ("world-level weights"), and let a Markov kernel $K(d y | m)$ generate the whole transcript $Y$, which may have any length, be randomly stopped, or be adaptive under a policy that does not depend on the hypothesis label. Write $P_a^Y = a K$ and $P_b^Y = b K$.

#standard(id: "ST-T277", name: "Persistent cap")[
  $ KL(a K || b K) <= KL(a || b), $ <eq:cap>
  and with $N$ independent world draws $M_1, dots, M_N$, i.i.d. from $a$ (resp. $b$), and any common kernel from $(M_1, dots, M_N)$ to $Y$, $KL(P_a^Y || P_b^Y) <= KL(a^(times.o N) || b^(times.o N)) = N KL(a || b)$, with equality to $sum_u KL(a K_u || b K_u)$ when each unit's transcript depends only on its own draw through a kernel $K_u$ and the units are independent.
]

This is the data-processing inequality for KL divergence @cover2006 @polyanskiy2024, not claimed as new; the contribution is its application to world-level weights. Its meaning for the simulation question is direct: expected evidence about how likely each kind of world is scales with the number of independent world draws, not with transcript length. It is the expected (KL) form of the pointwise ceiling $ln max_m a_m \/ b_m$ of #id[ST-T226], and it does not limit evidence about _which_ world is active. When $a$ is not absolutely continuous with respect to $b$, #eqref(<eq:cap>) is vacuous, and the two sides need not be infinite together: $a = (1/2, 1/2)$, $b = (1, 0)$ with identical component laws give $KL(a || b) = +infinity$ but transcript divergence $0$ for every length.

#theorem(id: "ST-T278", name: "Saturation identity")[
  If $KL(a || b) < infinity$, the _saturation gap_ $"gap" := KL(a || b) - KL(a K || b K)$ satisfies
  $ "gap" = EE_(Y tilde a K) [KL(a(dot | Y) || b(dot | Y))]. $
  For finite $M$ with component densities $k_m$ (with respect to a common dominating measure), put $r_m = a_m \/ b_m$ and $S_b (y) = {m : b_m k_m (y) > 0}$. The gap is zero iff $r$ is constant on $S_b (y)$ for $a K$-almost every $y$. In particular the gap is zero if $M$ is a function of $Y$; the converse holds when the ratios $r_m$ are pairwise distinct on $supp(b)$ and fails in general.
]

The identity is the KL chain rule, and the zero-gap condition specializes the Kullback-Leibler equality condition for data processing @kullback1951; only the finite-$M$ ratio form is stated here. The converse fails: with $a = (1/4, 1/4, 1/2)$, $b = (1/8, 1/8, 3/4)$, two components sharing the law $(1/2, 1/2, 0)$ and a third with law $(0, 0, 1)$, the transcript divergence equals $KL(a || b) approx 0.1438$ at lengths 1, 3 and 6, yet $M$ is not a function of $Y$ (#id[ST-F55] records a second, deterministic counterexample). The main new piece of this section is a quantitative bound on the gap.

#theorem(id: "ST-T279", name: "Gap bound and decay")[
  Let $M$ be finite with $a << b$, $S = supp(a)$, $Z = supp(b) without S$, $r_max = max_(m in S) r_m$, $r_min = min_(m in S) r_m$, and let $P_a ("err")$ be the Bayes error of the MAP rule for $M$ under $a$. For any orders $lambda_(m m') in (0, 1]$,
  $ "gap" <= (r_max / r_min - 1) P_a ("err") + sum_(m in S, m' in Z) a_m / lambda_(m m') (b_(m') / b_m)^(lambda_(m m')) B_(lambda_(m m')) (k_m, k_(m')), $
  where $B_lambda (P, Q) = integral p^(1-lambda) q^lambda d mu$. For conditionally i.i.d. transcripts of length $n$ whose relevant component pairs have distinct laws, the gap therefore decays at least as fast as $exp(-n(min C(k_m, k_(m')) - o(1)))$, the minimum of Chernoff informations over relevant pairs (pairs within $S$ when $r_max > r_min$, and pairs in $S times Z$).
]
#proof[
  Fix $y$, let $alpha$ and $beta$ be the posteriors of $M$ under $a$ and $b$, and let $p_b^S (y) = sum_(m in S) b_m k_m (y)$ and $p_b^Z (y) = sum_(m in Z) b_m k_m (y)$ be the parts of the $b$-mixture density from $S$ and from $Z$. Then $KL(alpha || beta) = {EE_alpha ln r + ln EE_alpha [1\/r]} + ln(1 + p_b^Z \/ p_b^S)$. With $epsilon = 1 - max alpha$ the bracket is at most $epsilon (r_max \/ r_min - 1)$ by convexity, and its expectation is $(r_max \/ r_min - 1) P_a ("err")$. The last term is bounded with $ln(1 + x) <= x^lambda \/ lambda$. The rate follows from the classical multi-hypothesis Chernoff bound on the MAP error @chernoff1952 @leang1997. Full proof: `docs/evidence-scaling-dichotomy.md`.
]

The MAP-error exponent is classical; only the $(r_max \/ r_min - 1)$ factor and the support-mismatch term are new, and the rate is an upper bound on the exponent, not shown to be tight. Distinct component laws are needed. Take binary transcripts with success probabilities $eta_m = P(Y_t = 1 | M = m)$ equal to $(1/4, 1/4, 3/4)$, $a = (1/2, 1/3, 1/6)$ and $b = (1/6, 1/3, 1/2)$: two components coincide, the transcript divergence never exceeds the merged value $0.2426$, and the gap stays at least $0.1236$ for every $n$.

#standard(id: "ST-T280", name: "Different kernels")[
  If the hypotheses also use different kernels $K^a, K^b$, then $KL(a K^a || b K^b) <= KL(a || b) + integral KL(K^a (dot | m) || K^b (dot | m)) a(d m)$, and for conditionally i.i.d. transcripts the second term is linear in $n$.
]

#figure(
  placement: top,
  image("figures/fig_evidence.pdf", width: 100%),
  caption: [Two regimes of evidence. (a) Per-world law differs: $EE_beta [ln "BF"_n]$ for the Krichevsky-Trofimov Bayes factor against fair bits, computed exactly (60-digit arithmetic), with the #id[ST-T273] sandwich #eqref(<eq:kt>) shaded for each $beta$; at $beta = 1\/2$ it decreases like $-1/2 ln n$. (b) Only world weights differ: transcript divergence for one persistent binary latent ($eta = (1\/3, 2\/3)$, $a = (3\/4, 1\/4)$, $b = (1\/4, 3\/4)$) saturates at $KL(a || b) = 0.5493$ (#id[ST-T277]); with the non-identifying components of Section 4 (gold) it saturates at the merged value $0.2426$; with different kernels it passes the cap and tracks the #id[ST-T280] bound (dashed), within $10^(-6)$ of it at $n = 256$. (c) The saturation gap (solid) and the #id[ST-T279] bound (dashed, same color) on three #id[ST-F55] examples. The bound is valid at every $n$. For the binary and ternary examples it uses the exact MAP error; for the support-mismatch example its mismatch term is evaluated at $lambda = 1\/2$ (Bhattacharyya), whose exponent $0.034668$ is within $0.1%$ of the Chernoff exponent $0.034688$.],
) <fig:evidence>

*The dichotomy.* The contrast with hypotheses that disagree about the per-world law is sharp. For $n$ tosses of a coin of bias $beta$, with fair bits as the null and a Krichevsky-Trofimov (Jeffreys) mixture of biased coins as the alternative, the ledger proves the two-sided bound (#id[ST-T273])
$ n KL(beta || 1/2) - 1/2 ln n - ln 2 <= EE_beta [ln "BF"_n] <= n KL(beta || 1/2) - 1/2 ln n + 1 - 1/2 ln(upi/2) $ <eq:kt>
for every $n >= 1$ and $beta in [0, 1]$, with exact constant $1/2 ln(2 e \/ upi)$ for interior $beta$ (#id[ST-T274], the Clarke-Barron constant @clarke1990 specialized; the upper regret bound is Krichevsky-Trofimov @krichevsky1981). The alternative in #eqref(<eq:kt>) is itself one persistent draw of the bias, so the dividing line is not "fresh versus persistent". It is whether the hypotheses differ in the per-world law ($KL(a || b) = +infinity$ in the cap, or different kernels as in #id[ST-T280]) or only in world-level weights over a common kernel. @fig:evidence shows both regimes on the ledger's exact examples.


#fcheck(id: "ST-F55", name: "Exact persistent-latent audit")[
  Exact laws over sufficient count vectors with 60-digit logarithms, for binary, ternary, support-mismatch, ternary-emission and non-identifying examples up to $n = 64$: monotonicity, the cap, the identity of #id[ST-T278] against an independent computation to within $10^(-30)$, the bound of #id[ST-T279] and its Bhattacharyya relaxation, the two counterexamples, and additivity over two independent world draws.
]

*Relation to Section 3.* The two sections describe one structure from two sides. Inside a two-view fiber the evidence is exactly zero (#id[ST-T304]). Outside it, if two hypotheses share the channel and differ only in the prior over latent states, then any transcript of a single draw, including the two-view and three-view transcripts of Section 3, gives at most $KL(a || b)$ nats of expected evidence about the prior (#id[ST-T277] applies to every transcript design). Evidence beyond that per-draw budget requires either more independent world draws or hypotheses that disagree about the per-world laws.

= The price of shared randomness

== Setting

A finite rational game $Gamma in QQ^(R times J)$ has rows $r$ for adversary scenarios (point-mass models, declared priors, or vertices of a total-variation ball) and columns $c = 1, dots, J$ for deterministic zero-error codebooks; $Gamma_(r c)$ is the expected codeword length, or regret, of codebook $c$ under scenario $r$. Write $Delta$ for the simplex of column laws $w$.

*The $K_3$ game.* Three source states are pairwise confusable (the complete confusion graph $K_3$), so a zero-error code gives them distinct codewords. The scenarios are the three point masses, and the columns are the three complete prefix codes whose codeword lengths are a permutation of $(1, 2, 2)$: $Gamma_(m c) = 1$ if code $c$ gives state $m$ the one-bit codeword, and $2$ otherwise. Every deterministic code has worst case $2$, while the uniform mixture has worst case $5\/3$. This game recurs in the ledger (#id[ST-M26], #id[ST-M41], #id[ST-M45], #id[ST-M47]) and is the running example below.

The assumptions are those of `docs/random-bit-price-shared-randomness.md`, Section 1:

/ (A1) Public seed.: A seed is observed by the encoder and every decoder before the source is observed, and it selects a column. Every column is zero error, so zero error is preserved.
/ (A2) Oblivious adversary.: The scenario is chosen without seeing the seed. A seed that induces column law $w in Delta$ therefore has payoff $f(w) = max_r (Gamma w)_r$, and $V^* = min_(w in Delta) f(w)$, with optimal set $cal(O)$, a nonempty rational polytope.
/ (A3) Resource models.: Fixed budget: $b$ independent fair bits and any deterministic map from them to columns (value $V_b$). Variable budget: an i.i.d. fair bit stream, an almost surely finite stopping time $tau$ of its natural filtration, and an output that is a function of the bits read. $L$-ary coin: $t$ independent uniform $L$-sided tosses and a deterministic map (value $V_(L, t)$).
/ (A4) Rationality.: The entries of $Gamma$ are rational with common denominator $D_Gamma$, and $V^* = p \/ Q$ in lowest terms.

#standard(id: "elementary", name: "Realizable laws")[
  With $b$ fair bits the realizable column laws are exactly $Delta_b = Delta inter 2^(-b) ZZ^J$; with $t$ uniform $L$-ary tosses, exactly $Delta inter L^(-t) ZZ^J$.
]

We refer to this as Lemma 0, as the repository does.

== Fixed budgets: a dichotomy and a two-sided rate

#theorem(id: "ST-T310", name: "Dyadic dichotomy")[
  $V^* <= V_(b+1) <= V_b$, and $V_b = V^*$ iff $cal(O)$ meets $Delta_b$. Hence $V^*$ is reached by finitely many fair bits iff some optimal mixture is dyadic, and then for all $b >= b_0$.
]

#theorem(id: "ST-T311", name: "Two-sided gap without nondegeneracy assumptions")[
  For every optimal $w^*$ with support $S$, $sigma = |S|$ and payoff spread $delta_S = max_r (max_(c in S) Gamma_(r c) - min_(c in S) Gamma_(r c))$,
  $ V_b - V^* <= delta_S floor(sigma/2) 2^(-b), $
  and whenever $V_b > V^*$, $V_b - V^* >= 1 \/ "lcm"(2^b D_Gamma, Q) >= 2^(-b) \/ (D_Gamma Q)$. So if $cal(O)$ contains no dyadic point,
  $ 2^(-b) / (D_Gamma Q) <= V_b - V^* <= delta_S floor(sigma/2) 2^(-b) quad "for every" b >= 0. $ <eq:twosided>
]
#proof[
  Upper bound: round $N w^*$ ($N = 2^b$) by largest remainders (Hamilton apportionment) inside $S$; the positive part of the error $e$ is at most $floor(sigma\/2)\/N$, and $(Gamma e)_r <= delta_S$ times it in every row. Lower bound: $V_b$ lies in $(2^b D_Gamma)^(-1) ZZ$ and $V^* = p\/Q$, so a positive difference is at least $1\/"lcm"(2^b D_Gamma, Q)$.
]

The lower constant is attained at even $b$ by the $K_3$ game and by the skew total-variation game of #id[ST-M91] (Section 5.4); the upper constant is not claimed tight. By the Shapley-Snow basic-solution theorem @shapley1950 there is an optimal $w^*$ with $sigma <= min(R, J)$, which gives a bound in terms of the payoff range. The classical sparse-strategy results of Althöfer @althofer1994 and Lipton and Young @lipton1994 give $N$-uniform $epsilon$-optimal strategies with $N = O(log R \/ epsilon^2)$, a gap of order $sqrt(ln R \/ 2^b)$ that is worse in $b$ but independent of $sigma$ and $J$; see also @lipton2003 @hubacek2016 on playing with limited randomness. The new content of #eqref(<eq:twosided>) is the exact $Theta(2^(-b))$ rate for a fixed rational game with no nondegeneracy assumption. Deciding whether $cal(O)$ contains a dyadic point is exact: for $L >= 2$, a rational polytope meets $ZZ[1\/L]^J$ iff its affine hull does (Lemma 2a of `docs/random-bit-price-shared-randomness.md`), which reduces to a finite congruence check.

== Variable budgets: the Knuth-Yao price

For $x in [0, 1]$ let $kappa(x) = sum_(t >= 0) "frac"(2^t x) 2^(-t)$, so $kappa(1) = 0$; for $x in [0, 1)$ with binary digits $x_j$ (the terminating expansion when $x$ is dyadic), $kappa(x) = sum_(j >= 1) j x_j 2^(-j)$. For a law $w$ let $rho_t (w) = sum_c "frac"(2^t w_c) 2^(-t)$.

#standard(id: [Knuth-Yao @knuth1976; reproved in the repository], name: "Optimal exact sampling")[
  Every exact sampler of $w$ from fair bits satisfies $P(tau > t) >= rho_t (w)$ for all $t$. The discrete distribution generating (DDG) tree attains this bound at every $t$, so it minimizes $EE[tau]$, with $EE^*[tau](w) = sum_c kappa(w_c)$, a rational number when $w$ is rational. Moreover $H(w) <= EE^*[tau](w) < H(w) + 2$ @cover2006.
]

The repository reproves the first two statements; the upper bound $H + 2$ is cited and checked numerically on 200 seeded random laws.

#theorem(id: "ST-T312", name: "The price of the value")[
  $V^*$ is attainable with an almost surely finite number of fair bits in every finite rational game. The infimum of the expected number of fair bits over samplers attaining $V^*$ equals $min_(w in cal(O)) sum_c kappa(w_c)$, and the minimum is attained. If $tau <= B$ almost surely then the induced law lies in $Delta_B$; so if $cal(O)$ has no dyadic point, no bounded-bit sampler attains $V^*$, and every sampler that does has $P(tau > t) >= min_(w in cal(O)) rho_t (w) > 0$ for every $t$.
]
#proof[
  Attaining $V^*$ means inducing a law in $cal(O)$; apply the Knuth-Yao statements and Lemma 0. The functions $kappa$ and $rho_t$ are lower semicontinuous and $cal(O)$ is compact.
]

Only the composition with the optimal set is claimed; when $cal(O)$ is not a singleton the minimum is attained but not computed in general.

#theorem(id: "ST-T313", name: "Coins with L sides")[
  For integers $L >= 2$, $V_(L, t) = V^*$ iff $cal(O)$ meets $L^(-t) ZZ^J$; $V^*$ is reached by finitely many $L$-ary tosses iff $cal(O)$ meets $ZZ[1\/L]^J$; and whenever $V_(L, t) > V^*$, $V_(L, t) - V^* >= 1 \/ (D_Gamma Q L^t)$.
]

Building a uniform $L$-ary coin from fair bits is itself priced by the Knuth-Yao theorem and is not free.

== Worked instances

#model(id: "ST-M90", name: [The $K_3$ value curve])[
  In the $K_3$ game,
  $ V_b = 2 - floor(2^b \/ 3) / 2^b, quad V_b - 5/3 = (2^b "mod" 3) / (3 dot 2^b) > 0, quad V_(2j) = V_(2j+1) = 5/3 + 1/(3 dot 4^j). $
  The sequence is $2, 2, 7/4, 7/4, 27/16, 27/16, 107/64, dots$: $V^* = 5/3$ is never reached, every odd-numbered bit is worthless, and for $j >= 1$ the $2j$-th bit is worth exactly $4^(-j)$.
]
#proof[
  $(Gamma w)_m = 2 - w_m$, so $f(w) = 2 - min_m w_m$; on $Delta_b$ the best minimum is $floor(2^b\/3)\/2^b$, and $2^b mod 3$ alternates between 1 and 2.
]

#figure(
  placement: top,
  image("figures/fig_bits.pdf", width: 100%),
  caption: [The fair-bit price of shared randomness. (a) Exact gaps $V_b - V^*$ for the $K_3$ game (#id[ST-M90]) and the skew TV game at radius $1\/2$ (#id[ST-M91]), each computed by exhaustive search over the $2^b$-grid, with the #id[ST-T311] envelopes shaded; the even-$b$ values sit on the lower envelope, and every odd-numbered bit is worthless. (b) For the uniform ternary law, the Knuth-Yao tail $P(tau > t) = (2^t "mod" 3)\/2^t$ equals the universal lower bound at every $t$ (checked to depth 40 in #id[ST-F61], plotted to 20) and never reaches zero; $EE[tau] = 8\/3$. (c) The DDG tree for the uniform ternary law: leaves A, B and C are the three outcomes, and each pair of levels decides three quarters of the remaining mass. (d) One public $L$-sided toss reaches $V^* = 5\/3$ exactly when $3 | L$, for both games (#id[ST-M93]). All values are exact rationals from `random_bit_price.py`.],
) <fig:bits>

#model(id: "ST-M91", name: "The skew total-variation game at radius one half")[
  For the $K_3$ graph with nominal prior $(4/5, 1/10, 1/10)$ and total-variation radius $1\/2$ (the game of #id[ST-M27], whose five rows are the vertices of the ball and whose three columns give the one-bit codeword to states 2, 1 and 3), $cal(O) = {(1/3, 1/3, 1/3)}$, $V^* = 5/3$, and
  $ V_b = 5/3 + (2^b "mod" 3) / (30 dot 2^b), $
  exactly one tenth of the $K_3$ gap. The gain over the deterministic value $17\/10$ is $floor(2^b\/3)\/(10 dot 2^b)$, zero for $b = 0$ and $b = 1$.
]

For radius at most $7\/15$ the deterministic code that gives the heavy state the one-bit codeword is already optimal (proved in `docs/random-bit-price-shared-randomness.md`, Section 4, and checked on the grid $r = k\/30$), so below the #id[ST-M27] threshold there is no randomization gain and nothing to pay for.

#model(id: "ST-M92", name: "Knuth-Yao prices of the committed instances")[
  In the reduced games (@tab:bits), the optimal set is the singleton uniform law for the $K_3$ game (#id[ST-M26], #id[ST-M45]) and for #id[ST-M27] at radius $1\/2$, so no fixed budget reaches $V^*$ and the least expected cost is $3 kappa(1\/3) = 8\/3$ fair bits. It is the singleton $(1\/2, 1\/2)$ law for #id[ST-M21] (minimax and regret) and for the shared-seed game on the #id[ST-M22] instance, so one bit suffices and is necessary. At radii $2\/5$ and $7\/15$ of #id[ST-M27] it contains a pure law, so no bits are needed.
]

The $8\/3$-bit cost of an exact uniform ternary choice is classical @knuth1976 @lumbroso2013; #id[ST-M92] identifies it as the exact coordination price of these games. The #id[ST-M22] instance has four pairwise-confusable states and two priors that put $7\/10$ on different states; its reduced shared-seed game has rows $(3\/2, 2, 21\/10)$ and $(21\/10, 2, 3\/2)$, deterministic value $2$ and $V^* = 9\/5$ at $(1\/2, 0, 1\/2)$. The two-scenario gain of #id[ST-M21], from $19\/10$ to $31\/20$ in worst-prior expected length, costs exactly one fair bit, fixed or expected.

#model(id: "ST-M93", name: [One $L$-sided toss])[
  One uniform $L$-ary public toss attains $V^*$ iff $3 | L$ for the $K_3$ game and for #id[ST-M27] at radius $1\/2$ (checked for $L <= 12$, and for the $K_3$ game also for all $L^t <= 1000$ with $3 divides.not L$), with one-toss $K_3$ value $V_(L, 1) = 2 - floor(L\/3)\/L$; and iff $2 | L$ for #id[ST-M21] and the #id[ST-M22] game ($L <= 12$). The general criterion is #id[ST-T313].
]

#figure(
  placement: auto,
  table(
    columns: (1.7fr, 1.05fr, 0.6fr, 0.75fr, 0.75fr),
    align: (left, left, center, center, center),
    inset: (x: 5pt, y: 3.5pt),
    table.hline(stroke: 0.6pt),
    table.header([*Instance*], [*Optimal law*#super[a]], [*Fixed $b$*], [*Expected bits*], [*$L$-ary toss*]),
    table.hline(stroke: 0.4pt),
    [$K_3$ game (#id[ST-M90]\; #id[ST-M26], #id[ST-M45])], [$(1/3, 1/3, 1/3)$, unique], [none], [$3 kappa(1/3) = 8/3$], [iff $3 | L$],
    [skew TV, $r = 1\/2$ (#id[ST-M91]\; #id[ST-M27])], [$(1/3, 1/3, 1/3)$, unique], [none], [$8/3$], [iff $3 | L$],
    [#id[ST-M21] (minimax and regret)], [$(1/2, 1/2)$, unique], [$b = 1$], [$1$], [iff $2 | L$],
    [#id[ST-M22] instance, shared seed], [$(1/2, 0, 1/2)$, unique], [$b = 1$], [$1$], [iff $2 | L$],
    [#id[ST-M27], $r in {2\/5, 7\/15}$], [contains a pure law], [$b = 0$], [$0$], [any $L$],
    table.hline(stroke: 0.6pt),
  ),
  caption: [Exact random-bit prices of the committed shared-randomness instances (model results #id[ST-M92] and #id[ST-M93], certified in #id[ST-F61]). The last row has no randomization gain. Columns: optimal law; least fixed budget $b$ with $V_b = V^*$; least expected number of fair bits attaining $V^*$; when one uniform $L$-ary toss attains $V^*$. #super[a]~In the reduced game, which merges payoff-identical columns and moves weakly dominated weight onto dominators; this changes none of the values (Lemma P of `docs/random-bit-price-shared-randomness.md`).],
) <tab:bits>


#fcheck(id: "ST-F61", name: "Exact certification of the bit price")[
  The $K_3$ game for $b <= 12$ by exhaustive enumeration; eight committed matrices for $b <= 10$ with an independent basis-enumeration solver and dual certificates, both gap bounds and the dyadic decision; 300 seeded random integer games ($b <= 6$; 219 dyadic and exact, 81 never exact); 200 seeded random rational laws for the Knuth-Yao identities; coin alphabets $L <= 12$; and cross-checks of seven matrices against the repository's own certificates.
]

= Limitations and nonclaims

*Interpretation.* Nothing in this paper is evidence for or against the hypothesis that reality is simulated. The results bound what restricted, declared models allow an observer to learn or to buy; reading a latent state as "simulated versus base" is an interpretation of the mixture model, not a finding.

*Scope of the fiber results.* Finite alphabets, $pi > 0$, $K$ of full row rank $k$, $k$ known, and exact population laws of the two views across independent world draws; an observer of a single draw never sees $T$. Alternatives with more than $k$ latent states are not classified (splitting a state into identical copies enlarges the set of consistent weights), and alternatives with fewer are impossible because $"rank" T = k$. There is no finite-sample estimator or confidence interval for $[L, U]$. Nothing for $k >= 3$ is sharp beyond the instance: the $k = 3$ numbers are exact values attained by fiber models, an exact floor attained on one instance, and an uncertified float estimate. Kruskal's three-view theorem and the Giacomini-Kitagawa limit are cited, not proved. Anchors in #id[ST-T303] refer to the true channel. The upper bound $1 - (k-1) ell$ is not claimed sharp.

*Scope of the cap.* #id[ST-T277] and #id[ST-T280] are standard; #id[ST-T277] bounds an expectation, not every transcript (that is #id[ST-T226]), is vacuous when $a$ is not absolutely continuous with respect to $b$, and does not limit learning which world is active. The policy must not depend on the hypothesis label. The #id[ST-T279] exponent is an upper bound, not shown tight, and needs distinct component laws.

*Scope of the bit price.* Fair, independent, public bits (or uniform $L$-ary tosses) are assumed; extracting them from a biased or physical source is not addressed @gossner2002, and no fairness of any real source is certified. The adversary is oblivious to the seed; if the scenario may depend on the realized seed, no number of bits helps. Private encoder randomness is not covered. Payoffs must be rational. The upper constant of #id[ST-T311] is not claimed tight; the minimum over a non-singleton $cal(O)$ is attained but not computed in general; approximate sampling under a bit budget is treated only through $V_b$ (for optimal fixed-precision approximate sampling see @saad2020). The congruence decision procedure is exact but bounded in the checker. Knuth-Yao's theorem and the $8\/3$-bit cost of a uniform ternary choice are classical, and the dyadic dichotomy #id[ST-T310] is elementary.

*Novelty.* In the fiber section, part (1) of #id[ST-T297] is in the repository already, the orthogonal form is the standard symmetric-NMF fact, part (a) of #id[ST-T300] is known, anchor sufficiency is known, and #id[ST-T304] is standard. The stochastic reparametrization, the closed form of the $k = 2$ interval, the floor $ell(T)$, product-gauge rigidity, the necessary condition #id[ST-T305] and the exact witnesses were not found stated in this form in the literature we checked. In the evidence section only the $(r_max \/ r_min - 1)$ factor and the mismatch term of #id[ST-T279] and the finite-$M$ ratio form of #id[ST-T278] are offered as new. In the randomness section, the exact two-sided rate without nondegeneracy assumptions, the composition of Knuth-Yao with the optimal set, and the exact curves of the committed instances are offered as new. No priority is claimed for any of them.

= Open problems

#openp(id: "ST-O07", name: [Point identification and sharp sets for $k >= 3$])[
  (1) Characterize point identification from two views exactly: it lies between pairwise-incomparable row supports (necessary, #id[ST-T305]) and the sufficiently scattered condition (sufficient @huang2014, which is NP-complete to check); see also @laurberg2008. (2) Describe the sharp sets ${(O s)^2 : O in O(k), O W >= 0}$, the orthonormal frames inside a polyhedral cone; on the $k = 3$ witness the float estimate of the largest label-free weight is about $0.746$ against the generic $0.948$ (compare the rotational-ambiguity literature @borgen1985). (3) Give finite-sample, uniformly valid confidence sets for $[L, U]$; the endpoints are min and max functionals, non-smooth at ties.
]

#openp(id: "ST-O02", name: "Second-order term of the evidence constant")[
  Is the remainder of #id[ST-T274] equal to $(1 - 2 beta)^2 \/ (24 n beta(1-beta)) + O(n^(-2))$ for interior $beta$? A formal moment expansion gives this and the numerics agree, but the dominated remainder bounds are not written, so it stays open.
]

Further questions are not registered as claims but are marked by nonclaims above: compute $min_(w in cal(O)) sum_c kappa(w_c)$ when the optimal set is a polytope rather than a point (#id[ST-T312] proves only that the minimum is attained); decide whether the Chernoff exponent of #id[ST-T279] is tight, and whether the upper constant $delta_S floor(sigma\/2)$ of #id[ST-T311] can be improved; and classify alternatives with more than $k$ latent states. The question that joins the two halves of this paper, also unaddressed by the ledger, is the fair-bit cost of reaching a target value in a game played against a whole identified set rather than a declared finite scenario list.

#heading(numbering: none)[Reproducibility]

#block[
#set par(justify: false)
All results are merged on the repository's main branch: PR \#72 (squash commit `0c77232`) and the attribution sweep PR \#73 (`aa61193`). Clone the repository @simtheory at `aa61193` and run `uv sync && uv run python -m simtheory verify`. The claim manifests are `claims/two-view-orthogonal-fiber-claims.json`, `claims/evidence-scaling-dichotomy-claims.json` and `claims/random-bit-price-claims.json`; the derivations are `docs/two-view-orthogonal-fiber.md`, `docs/evidence-scaling-dichotomy.md` and `docs/random-bit-price-shared-randomness.md`; the certificates are `src/simtheory/two_view_fiber.py`, `evidence_scaling.py` and `random_bit_price.py`; and the committed receipts are `receipts/two-view-orthogonal-fiber.txt`, `receipts/evidence-scaling-dichotomy.txt` and `receipts/random-bit-price-shared-randomness.txt`. The README at that commit records 465 claims in 60 manifests. For this paper the three certificate modules were rerun from that commit and reproduced their committed receipts byte for byte. Every figure is generated by `figures.py` (next to this paper's source) from those modules. The only non-exact plotted quantities are closed-form curves (the $k = 2$ curve and its arc endpoints in @fig:k2, and the #id[ST-T273] envelope in @fig:evidence) and the illustrative Haar scan in @fig:k3; all are labeled in the captions.
]

#counter(heading).update(0)
#set heading(numbering: "A.1")
= Relation to earlier ledger entries

The fiber, the cap and the bit price re-read several earlier ledger entries without changing any of them. Pull-request numbers refer to the repository history.

== Mixture results

- #id[ST-T254–ST-T258] (one-view gauge, PR \#63): the one-view gauge family ${A : A bb(1) = bb(1)}$ has dimension $k^2 - k$; the second view cuts it to $G(W)$, of dimension at most $k(k-1)\/2$, full-dimensional when $K > 0$ and possibly finite otherwise (#id[ST-M89]).
- #id[ST-T261], #id[ST-T263] (two-view rigidity, PR \#64) and P1-T7 of the companion paper @fixcompanion (PR \#69): correct as scoped; #id[ST-T299] identifies the scope as "nonnegative orthogonal matrices are permutations". #id[ST-T263] is correct but partial: two views shrink the fiber without collapsing it. Part (b) of #id[ST-T300] supplies the different-channel analogue that the P1-T7 nonclaims set aside.
- #id[ST-M77–ST-M79] and #id[ST-F47]: all boundary witnesses remain correct. #id[ST-M87] adds the first witness whose alternative channel is strictly positive; the existing boundary pair (PR \#64 and the PR \#68 audit) is an anchor (endpoint) model.
- #id[ST-T225–ST-T228], #id[ST-M66], #id[ST-M67] (persistent-latent ceilings, PR \#56): #id[ST-T277] is the expected (KL) form of the pointwise ceiling #id[ST-T226]\; #id[ST-T278] and #id[ST-T279] quantify the saturation of #id[ST-T227]\; the $N$-unit form is the KL form of #id[ST-T228] and, with #id[ST-T233], says evidence about mixing weights scales with independent world draws. #id[ST-T280] complements the #id[ST-T226] scope nonclaim about component distinguishability.

== Coding results

Read through #id[ST-M90], the earlier $K_3$ entries acquire exact finite-budget versions. The minimax regret of #id[ST-M45] with $b$ bits is $1 - floor(2^b\/3)\/2^b$, never $2\/3$. The coordination term $1\/3$ of #id[ST-M47] is realized as $floor(2^b\/3)\/2^b$, so one bit buys nothing. #id[ST-M41]'s public-randomness game is, by its declared scope (three point-mass $K_3$ models and a source-independent public signal), the $K_3$ game of #id[ST-M90], so its value $5\/3$ (between the no-signal value $2$ and the full-revelation value $1$) is reached by no bounded number of fair bits; this identification is by comparison of the two declared scopes, since the #id[ST-M90] manifest does not list #id[ST-M41]. The garbling $(1/3, 1/3, 1/3)$ in the repository's Blackwell separation note cannot be implemented with any bounded number of fair bits; its exact expected price is $8\/3$, and one ternary toss pays it (#id[ST-M93]).

*Which nonclaims are now priced.* For finite rational one-shot shared-codebook games satisfying (A1) to (A4), #id[ST-T310–ST-T312] price the non-dyadic seed generation left open by #id[ST-T95] ("does not price exact non-dyadic random-seed generation") completely for a fixed budget, and for a variable budget exactly when $cal(O)$ is a singleton (as an attained minimum in general). Against #id[ST-T109], which notes that support size is not the random-bit cost, support size enters only the rounding constant $floor(sigma\/2)$; the cost is governed by dyadicity of $cal(O)$ and by $kappa$. For the lanes #id[ST-T171], #id[ST-T174], #id[ST-T182] and #id[ST-T184] the repository records only a remark: _if_ the relevant public-mixing game satisfies (A1) to (A4) and its optimal set has no dyadic point, its value is attained by no bounded-bit seed. Those matrices were not rechecked, and the random-bit nonclaim of #id[ST-T152] is not closed.

#v(0.5em)
#set text(size: 9pt)
#bibliography("refs.bib", title: "References", style: "ieee")
