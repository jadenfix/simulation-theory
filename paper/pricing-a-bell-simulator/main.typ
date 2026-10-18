// Pricing a Bell simulator
// Source of truth: github.com/jadenfix/simulation-theory at commit aa61193.
// Compile: python figures.py && python build.py (see README.md)
// Every mathematical statement below cites a claim ID from that repository.

#let ink = rgb("#1d2733")
#let accent = rgb("#2b5c8a")
#let mute = rgb("#6b7482")
#let rule-col = rgb("#d5dae1")

#set document(title: "Pricing a Bell simulator", author: "Jaden Fix")
#set page(
  paper: "a4",
  margin: (x: 2.35cm, top: 2.4cm, bottom: 2.4cm),
  numbering: "1",
  number-align: center,
  header: context {
    if counter(page).get().first() > 1 [
      #set text(size: 8pt, fill: mute)
      Pricing a Bell simulator #h(1fr) J. Fix
      #v(-0.55em)
      #line(length: 100%, stroke: 0.4pt + rule-col)
    ]
  },
)
#set text(font: "New Computer Modern", size: 10.2pt, fill: ink, lang: "en")
#set par(justify: true, leading: 0.62em, spacing: 0.95em)
#set heading(numbering: "1.1")
#show heading.where(level: 1): it => {
  v(0.9em)
  set text(size: 12pt, weight: "bold")
  block(it)
  v(0.25em)
}
#show heading.where(level: 2): it => {
  v(0.5em)
  set text(size: 10.4pt, weight: "bold")
  block(it)
  v(0.1em)
}
#set math.equation(numbering: "(1)", supplement: [Eq.])
#show figure.caption: it => {
  set text(size: 8.6pt)
  set par(justify: true, leading: 0.55em)
  block(width: 100%, align(left, it))
}
#set figure(gap: 0.8em)
#show figure: set block(spacing: 1.4em)
#show link: set text(fill: accent)
#show ref: set text(fill: accent)
#set list(indent: 0.6em, spacing: 0.7em)
#show table: set par(justify: false, leading: 0.5em)
#set enum(indent: 0.6em, spacing: 0.7em)

// ---------------------------------------------------------------- claim and theorem helpers
#let cid(s) = text(font: "DejaVu Sans Mono", size: 7.6pt, fill: accent, s)
#let tag(s) = box(
  inset: (x: 3pt, y: 1.2pt),
  radius: 2pt,
  fill: rgb("#eef2f7"),
  text(size: 7.4pt, fill: mute, weight: "regular", s),
)
// Theorem-like environments are figures of custom kinds, so that they can carry labels and be
// referenced with @. Theorems and propositions share one counter; finite checks, negative results
// and model results have their own.
#let env-kind = (
  "Theorem": "thm",
  "Proposition": "thm",
  "Finite check": "fc",
  "Negative result": "nr",
  "Model result": "mr",
)
#let env(kind, ids, status, title, body) = figure(
  kind: env-kind.at(kind),
  supplement: kind,
  numbering: "1",
  outlined: false,
  [#if title != none [#text(weight: "bold")[(#title)]]#h(0.4em)#ids.map(cid).join(text(size: 7.6pt, fill: accent)[, ])#h(0.35em)#tag(status)#h(0.3em)
    #body],
)
#let env-show(it) = block(width: 100%, breakable: true, above: 1.0em, below: 1.0em, {
  set align(left)
  set par(justify: true)
  text(weight: "bold")[#it.supplement #context it.counter.display(it.numbering)]
  [ ]
  it.body
})
#show figure.where(kind: "thm"): set block(breakable: true)
#show figure.where(kind: "fc"): set block(breakable: true)
#show figure.where(kind: "nr"): set block(breakable: true)
#show figure.where(kind: "mr"): set block(breakable: true)
#show figure.where(kind: "thm"): env-show
#show figure.where(kind: "fc"): env-show
#show figure.where(kind: "nr"): env-show
#show figure.where(kind: "mr"): env-show
#let theorem(ids, status, title: none, body) = env("Theorem", ids, status, title, body)
#let proposition(ids, status, title: none, body) = env("Proposition", ids, status, title, body)
#let modelresult(ids, status, title: none, body) = env("Model result", ids, status, title, body)
#let finitecheck(ids, status, title: none, body) = env("Finite check", ids, status, title, body)
#let negative(ids, status, title: none, body) = env("Negative result", ids, status, title, body)
#let proofsketch(body) = block(width: 100%, above: 0.5em, below: 1.0em)[
  #text(style: "italic")[Proof sketch.] #body #h(1fr) $square$
]
#let statusnote(body) = block(width: 100%, above: 0.45em, below: 0.8em)[#text(style: "italic")[Status.] #body]
#let TV = math.op("TV")
#let KL = math.op("KL")
#let sgn = math.op("sgn")
#let reponote(body) = block(above: 0.4em, below: 0.8em, {
  set par(justify: false)
  set text(size: 8.4pt, fill: mute)
  body
})
#let dist = math.op("dist")
#let area = math.op("area")

// ---------------------------------------------------------------- title block
#align(center)[
  #v(0.6em)
  #text(size: 19pt, weight: "bold")[Pricing a Bell simulator]
  #v(0.25em)
  #text(size: 11pt, fill: mute)[Precision, memory, communication and noise costs of reproducing CHSH statistics,\ stated from typed, test-backed claims]
  #v(0.9em)
  #text(size: 10.5pt)[Jaden Fix]
  #v(0.1em)
  #text(size: 9pt, fill: mute)[Tempera #h(0.6em) #link("mailto:Jaden@Tempera.dev")[Jaden\@Tempera.dev]]
  #v(0.1em)
  #text(size: 8.5pt, fill: mute)[Repository #link("https://github.com/jadenfix/simulation-theory")[github.com/jadenfix/simulation-theory], commit `aa61193`, October 2026]
]

#v(0.8em)
#block(inset: (x: 1.6em))[
  #set text(size: 9.2pt)
  #set par(leading: 0.58em)
  #text(weight: "bold")[Abstract.]
  A simulator that reproduces every observable law exactly cannot be detected, so a simulation hypothesis becomes testable only after it is restricted. We restrict it to a classical renderer of the canonical CHSH Bell experiment and ask, for each resource the renderer might economize, how much of it must be spent to reproduce the statistics and how many trials it takes to notice when it was not. *Precision.* A renderer whose outcome probabilities lie on a $1\/D$ grid is untestable if it may dither. On any commensurable schedule, CHSH included, it is indistinguishable from the Werner family under unknown visibility once $4 | D$ and $D$ exceeds an explicit threshold. Settings $0$ and $pi\/4$ identify it with $Theta(D^4 log(1\/epsilon))$ trials for designs restricted to cosines in ${0, plus.minus 1, plus.minus 1\/sqrt(2)}$; known unit visibility and a $D$-adapted angle give $Theta(D log(1\/epsilon))$. *Memory.* An $epsilon$-accurate one-trial renderer needs at least $pi\/(A_w epsilon^2)$ states, with $A_w$ the area of a polar zonotope. The constant is exactly $pi\/32$ for CHSH; the regular three-direction schedule forces the most memory among schedules with at most three direction classes, and the regular four-direction schedule forces more. *Leaks.* Exact certificates reproduce the classical communication, measurement-dependence and detection frontiers. *Noise.* On the one-trial interface with equal correlation magnitudes $C$, a visibility-$lambda$ simulator has Le Cam deficiency $C(1-lambda)\/(2(2 - C lambda))$ under central post-processing, strictly below what any deterministic setting-preserving relabeling achieves for $0 < C < 1$ and $0 <= lambda < 1$. On the Delft 2015 data, a 5-bit renderer with $S = 5\/2$ lies inside the reported interval, and no constant-bet mixture on the CHSH win indicator reaches an e-value of 20 (maximum 7.78). Every mathematical result carries a typed claim ID; illustrations are labeled. None of it is evidence for or against simulation.
]

#v(0.6em)

= Introduction

The simulation argument @bostrom2003 has a well-known empirical difficulty. If a simulator reproduces the probability law of every experiment we can run, then every test accepts with the same probability under the simulated and the unsimulated world, and every Bayes factor between them equals one (#cid("ST-T01"), elementary and not claimed as new). Empirical work on the question therefore restricts the hypothesis before testing it. Beane, Davoudi and Savage asked what a lattice discretization of spacetime would leave in cosmic-ray spectra @beane2014. Separately, and not as simulation tests, Buniy, Hsu and Zee considered a discrete Hilbert space @buniy2005 and Palmer a discretized Bloch sphere @palmer2020. Each identifies a resource that a simulator might economize, and one can ask whether the economy is visible.

This paper asks that question for one experiment where the bookkeeping can be made exact: the CHSH test @chsh1969 @bell1964. We treat a hypothetical simulator as a classical renderer that must emit, trial by trial, outcomes whose statistics match a declared quantum family, and we price four resources: the arithmetic precision of its outcome probabilities, the number of internal states it keeps, the classical leaks (communication, measurement dependence, detection loss) it would need to fake a Bell violation, and the visibility noise it can hide by post-processing. We restrict to classical renderers because Bell's theorem makes CHSH the cleanest experiment in which classical reproduction must cost something; a quantum renderer pays none of these prices. The same accounting applies to any classical device that tries to spoof a CHSH test, the adversary of device-independent certification @brunner2014. For each resource we ask for a *price* (the least resource that reproduces the statistics to a given accuracy) and a *detection cost* (the number of trials a referee needs to tell the renderer from the family). @tab:prices summarizes both. The classical communication and loophole costs of Bell correlations are an established subject @brassard1999 @toner2003 @pironio2003 @garg1987 @putz2014 @brunner2014; our contribution there is a set of exact, replayable certificates. Precision, memory and noise are less studied in this form, and most of the new mathematics is there.

The results come from an open repository @repo in which every claim is a typed record (theorem, model result, finite check or open problem) with assumptions, nonclaims, evidence paths and tests; at commit `aa61193` it holds 465 claims in 60 manifests. "Typed" and "test-backed" mean executable tests and exact-arithmetic receipts, not formal proofs in a proof assistant. This paper states only what those records prove and cites each by ID. Proofs are sketched; full proofs are in the repository documents named in each section. Every finite check is either a committed receipt compared byte for byte by a test or, for the Delft checks #cid("ST-F50") and #cid("ST-F51"), asserted by tests against committed data. Each result carries status tags from a closed list: _new_ (no earlier statement found, with the caveat that literature searches were not exhaustive), _new as applied_ (a classical argument applied to this setting), _elementary_ (a short verification, not claimed as new), _standard_ (known, restated for completeness), _cited_ (used, not proved in the repository), _reproduces_ followed by an author (a known result, re-derived or re-certified here), and _finite check_ (a bounded exact computation). When parts of a result differ in status, the tag lists the terms and a status note after the statement assigns them. Statements without a claim ID are illustrations and are labeled as such.

#figure(
  text(size: 8.6pt, table(
    columns: (7.6em, 1.45fr, 1.5fr, auto),
    stroke: none,
    inset: (x: 4pt, y: 3.2pt),
    align: (left, left, left, left),
    table.hline(stroke: 0.6pt),
    table.header([*Resource*], [*Price of reproduction*], [*Cost of detection*], [*Claims*]),
    table.hline(stroke: 0.4pt),
    [Precision $D$], [any $D$ suffices with private dithering; any $D$ with $4 | D$ above a threshold on CHSH under unknown $v$], [$Omega(D log(1\/epsilon))$ for every fixed-horizon design; $Theta(D^4 log(1\/epsilon))$ with settings $0, pi\/4$ (cosines in ${0, plus.minus 1, plus.minus 1\/sqrt(2)}$); $Theta(D log(1\/epsilon))$ with known unit visibility ($v = 1$) and $cos theta = 1 - 2\/D$], [T286–T289],
    [Memory $N$], [$N_w (epsilon) epsilon^2 -> pi\/A_w$ (two or three direction classes), $pi\/32$ for CHSH; $>= pi\/(A_w epsilon^2)$ otherwise], [not derived (one-trial accuracy only)], [T290–T296],
    [Communication\ $c$], [win $<= 3\/4 + c\/2$ (free silence), $<= 3\/4 + c\/4$ ($s$-blind flag)], [Wald floor $ln(1\/alpha)\/d(p || f(c))$ for e-processes], [T281, T282, T285],
    [Setting\ dependence $ell$], [win $<= 1 - ell$], [Wald floor $ln(1\/alpha)\/d(p || 1 - ell)$], [T283, T285],
    [Detection $eta$], [local model iff $eta <= 2\/(1 + sqrt(2))$], [not derived; not tested on Delft (event-ready)], [M85],
    [Visibility $lambda$], [one-trial deficiency $C(1-lambda)\/(2(2 - C lambda))$ (equal magnitudes, central post-processing)], [not derived; risk transfer $2 delta norm(L)_infinity$], [T306–T309],
    table.hline(stroke: 0.6pt),
  )),
  caption: [The price list. Claim IDs omit the prefix `ST-`; $d(p || f)$ is the Bernoulli Kullback–Leibler divergence and $p$ the true win probability. Each row is made precise, with its assumptions, in the section indicated by the claim range.],
) <tab:prices>

*Contributions.* (i) A finite-precision theory for Bell renderers (@sec:precision): a dithering boundary, non-identifiability on commensurable schedules with an explicit threshold and a counterexample to the unconditional version, and sharp trial counts whose constants are governed by Pell approximations and by the binary digits of $sqrt(2)$. (ii) Sharp renderer-memory constants on the Bell disk (@sec:memory): an area converse for arbitrary emissions, the exact CHSH constant $pi\/32$, a proof that the regular three-direction schedule forces the most memory (largest $pi\/A_w$) among schedules with at most three direction classes, and the observation that the regular four-direction schedule forces more. (iii) Exact certificates for the classical communication, measurement-dependence and detection frontiers, packaged as nulls for anytime-valid tests (@sec:frontiers). (iv) The exact one-trial Le Cam deficiency of a noisy Bell simulator and a strict gap to deterministic disguises (@sec:noise). (v) Illustrations on the Delft 2015 loophole-free data @hensen2015 @delftdata, including a negative result (@sec:delft).

= The CHSH disk <sec:disk>

#reponote[Repository: `docs/canonical-chsh-disk-geometry.md`, `docs/quantum-phase-predictive-bounds.md`, `docs/real-data-checks.md`; modules `quantum_phase_geometry.py`, `real_data.py`; tests `tests/test_quantum_phase_geometry.py`, `tests/test_real_data.py`.]

*Family.* A trial draws a setting pair $j$ from a public schedule $w$ (a probability vector, the same under every hypothesis). The pair has setting difference $theta_j$, cosine $c_j = cos theta_j$ and unit direction $u_j = (cos theta_j, sin theta_j)$. Outcomes are $a, b in {plus.minus 1}$. The visibility-phase family (#cid("ST-T11")) indexes states by $q = (x, y) = (v cos phi, v sin phi)$ in the closed unit disk $bb(D)$:
$ P_q (j, a, b) = w_j (1 - a b thin u_j dot q) \/ 4. $ <eq:family>
The letters $x, y$ denote these disk coordinates only. At $phi = 0$, @eq:family is the Werner (singlet) family with visibility $v$ (#cid("ST-T09")) @werner1989, with conditional law $P_v (a, b | j) = (1 - a b thin v c_j)\/4$; this sign convention is used throughout. For one setting, the total variation between $(1 - a b r)\/4$ and $(1 - a b r')\/4$ is $abs(r - r')\/2$, so the joint (setting, outcome) law satisfies exactly
$ TV(P_q, P_(q')) = h_Z (q - q'), quad h_Z (z) = sum_j w_j abs(u_j dot z) \/ 2. $ <eq:tv>
$h_Z$ is the support function of the zonotope $Z = sum_j (w_j\/2)[-u_j, u_j]$; it is a norm exactly when the schedule has at least two non-parallel direction classes (#cid("ST-T15")). We call such schedules *rank-2*.

#theorem(("ST-T12",), "elementary", title: "canonical CHSH metric")[
  For the canonical CHSH schedule (setting differences $-pi\/4, pi\/4, pi\/4, 3pi\/4$ with equal weight),
  $ TV(P_q, P_(q')) = norm(q - q')_infinity \/ (2 sqrt(2)). $
  Consequently the $epsilon$-ball around a state is an axis-parallel square of half-side $2 sqrt(2) thin epsilon$, and the polar body $Z^circle.small = {h_Z <= 1}$ is the square $[-2 sqrt(2), 2 sqrt(2)]^2$ of area 32.
] <thm:metric>
#proofsketch[Substitute the four directions into @eq:tv and use $abs(alpha + beta) + abs(alpha - beta) = 2 max(abs(alpha), abs(beta))$.]

*The local polytope and the disk.* In the CHSH game, input bits $s, t in {0, 1}$ are uniform and the outputs, read as bits, win iff $a xor b = s t$. The CHSH value and the average win probability $overline(p)$ satisfy $S = 8 overline(p) - 4$. Every local model is a mixture of the 16 deterministic strategies, which are the vertices of the local polytope. The certificate of #cid("ST-T283") shows that each of them loses an odd number of input pairs (8 lose one and 8 lose three), so every local model with uniform, independent inputs wins with probability at most $3\/4$, that is $S <= 2$. On the disk, the canonical CHSH expression of a family member is $S = 2 sqrt(2) thin x$, so the local face is the chord $x = 1\/sqrt(2)$ and Tsirelson's bound $S <= 2 sqrt(2)$ @tsirelson1980 (cited) is the boundary point $x = 1$ (@fig:disk). Local models need not lie in the family. For arbitrary correlators we define $x$ as the equal-weight least-squares disk coordinate; then $x = S\/(2 sqrt(2))$ identically (#cid("ST-F51")), so the chord statement compares $S$ alone. We do not need, and the repository does not compute, the full intersection of the local polytope with the family.

#finitecheck(("ST-F50", "ST-F51"), "finite check", title: "Delft 2015 on the disk")[
  A standard-library port of the published valid-trial filter keeps $n = 245$ of the 4746 released heralding attempts @delftdata, with $k = 196$ CHSH wins, correlators $(E_(00), E_(01), E_(10), E_(11)) = (0.736, 0.595, 0.484, -0.608)$, $S = 2.422 plus.minus 0.204$, and $P(op("Bin")(245, xi) >= 196) = 0.0392$ with $xi = 3\/4 + 3(beta + beta^2)$, where $beta = 1.08 times 10^(-5)$ is the published bound on the bias of the setting generators, reproducing the published values @hensen2015. The Delft settings are the canonical schedule with every setting difference shifted by $pi$, and the equal-weight least-squares disk point is $q = (0.856, -0.094)$. By @thm:metric its predictive distance to the nearest chord point is $(S - 2)\/8 = 0.053$ per trial (@fig:disk b).
] <fc:delft>

#figure(
  placement: auto,
  image("figures/fig1_disk.svg", width: 100%),
  caption: [The canonical CHSH disk. *(a)* States $q = (x, y) = (v cos phi, v sin phi)$ of the visibility-phase family. The shaded strip $abs(x) <= 1\/sqrt(2)$ is where the canonical CHSH expression satisfies $abs(S) <= 2$; Tsirelson's bound is the boundary point $x = 1$. Gold ticks mark the Werner states ($phi in {0, pi}$) whose outcome laws lie on the $1\/32$ grid, $x = m sqrt(2)\/8$ with $abs(m) <= 5$ (@sec:precision). *(b)* Zoom. The Delft 2015 least-squares point $q = (0.856, -0.094)$ (#cid("ST-F51")) with a $1 sigma$ ellipse (nearly circular) computed by `figures.py` from the per-setting binomial variances $(1 - E^2)\/n_(s t)$, the same approximation as the error on $S$ in #cid("ST-F50")\; the ellipse is an illustration, not a repository claim. The square is the TV ball of radius $(S - 2)\/8$, which just reaches the chord. The gold point is the $D = 32$ renderer of @prop:chsh ($v = 5 sqrt(2)\/8$, $S = 5\/2$).],
) <fig:disk>

= Precision <sec:precision>

#reponote[Repository: `docs/finite-precision-renderer-identifiability.md`; module `src/simtheory/finite_precision_renderers.py`; tests `tests/test_finite_precision_renderer_identifiability.py`.]

Write $tau_j = -E[A B | j]$ for the correlator at setting $j$, so that under the Werner law $P_v (a, b | j) = (1 - a b thin v c_j)\/4$ we have $tau_j = v c_j$. Visibility $v in [v_min, v_max]$ is a nuisance parameter and *the cosines are known exactly*. The precision $D$ is declared in advance.

*Stationary finite precision* $H_D$: trials are conditionally independent given the settings, and for every setting there is one fixed law $Q_j$ on ${plus.minus 1}^2$ with every entry in $(1\/D) ZZ$. The law $Q_j$ is the effective per-trial law after all internal randomness is marginalized; it need not be Werner-shaped. A *dithered* renderer instead draws a fresh private index on each trial and emits one of several grid laws.

#theorem(("ST-T286",), "standard", title: "dithering boundary")[
  (a) For every law $p$ on four outcomes and every $D >= 1$ there are at most four $D$-grid laws, each within $1\/D$ of $p$ in every coordinate, whose mixture is exactly $p$. Hence a dithered renderer with unrestricted private randomness reproduces every Werner law for every design and every number of trials, and its Bayes factor against the base model is 1. (b) If the dithering weights lie in $(1\/M) ZZ$, the set of effective laws is exactly $H_(D M)$: only the product $D M$ is observable.
] <thm:dither>
#proofsketch[Systematic sampling @madow1949: partition $[0, r)$ into intervals of lengths equal to the fractional parts of $D p$ and round up the coordinates hit by $U, U + 1, dots$ for $U$ uniform. Part (b) splits a $D M$-grid count vector into $M$ blocks of $D$.]

So finite precision is testable only under a declared no-dithering restriction (or a bound on private randomness, which reduces to $H_(D M)$). Under that restriction, the arithmetic of the setting cosines decides everything.

#theorem(("ST-T287",), "new", title: "commensurable schedules cannot identify")[
  Suppose every setting cosine is a rational multiple of one number, $c_j = (a_j \/ b) c$ with integers $a_j$, $b >= 1$ and $c > 0$. Let $4 | D$. Then $P_v in H_D$ whenever $v c in (4 b \/ D) ZZ$, and such a $v$ exists in $[v_min, v_max]$ whenever $c (v_max - v_min) >= 4 b\/D$. For such $v^*$ the stationary renderer $Q = P_(v^*)$ has the same transcript law as the base model at $v^*$, for every design and every $n$, so every level-$alpha$ test of the Werner family has power at most $alpha$ at $Q$.
] <thm:commens>
#proofsketch[A Werner law is a $D$-grid law iff $D$ is even and $tau_j = v c_j in L_D = {(4k - D)\/D : k = 0, dots, D\/2}$ (direct count, brute-forced for $D <= 40$). With $v c = 4 b m\/D$, each $tau_j = 4 a_j m \/ D$ lies in $L_D$.]

#proposition(("ST-T287",), "new", title: "canonical CHSH")[
  Every CHSH setting has $abs(c_j) = 1\/sqrt(2)$. For every $D$ divisible by 4 with $D (v_max - v_min) >= 4 sqrt(2)$, no CHSH data set of any size separates $H_D$ from the Werner family with unknown visibility. Example: $D = 32$ and $tau = 5\/8$ give $v = 5 sqrt(2)\/8 approx 0.884$. At a setting with $c_j = +1\/sqrt(2)$ the Werner law is then the 32-grid law $(3\/32, 13\/32, 13\/32, 3\/32)$ on $(+ +, + -, - +, - -)$, at the setting with $c_j = -1\/sqrt(2)$ it is the reflected law $(13\/32, 3\/32, 3\/32, 13\/32)$, and $abs(S) = 4 tau = 5\/2$.
] <prop:chsh>

#negative(("ST-T287",), "finite check", title: "the threshold is needed")[
  The unconditional statement "for every $D$ divisible by 4 some $v in [v_min, 1]$ gives $P_v in H_D$" is false. For CHSH and $v in [9\/10, 1]$, $L_4 = {-1, 0, 1}$ misses $[0.636, 0.708]$; among $D equiv 0 med (mod 4)$ in $[4, 400]$, exactly $D in {4, 8, 16, 20, 28, 32, 44}$ fail. For $v in [1\/2, 1]$ only $D = 4$ fails.
] <nr:threshold>

The obstruction to identification is commensurability, and an irrational cosine ratio removes it (@fig:precision a).

#theorem(("ST-T288",), "new", title: "settings 0 and π/4")[
  Let the schedule contain a setting with $c = 1$ (index 1) and a setting with $c = 1\/sqrt(2)$ (index 2), let $v_min > 0$, and write $Delta_1 = tau_1 (Q) - v$, $Delta_2 = tau_2 (Q) - v\/sqrt(2)$.
  + (Separation.) For every $D >= 1$, $Q in H_D$ and $v$: $abs(Delta_1) + abs(Delta_2) >= min(v_min, 1\/((2 + sqrt(2)) D^2))$ and $max(abs(Delta_1), abs(Delta_2)) >= g_* (D) := min(v_min, 1\/((3 + 2 sqrt(2)) D^2))$. We write $g_D$ for the exact minimum of $max(abs(Delta_1), abs(Delta_2))$ over $Q in H_D$ and $v in [v_min, v_max]$, so $g_D >= g_* (D)$. With setting weights $w$, $TV(Q, P_v) >= (min(w_1, w_2)\/2) min(v_min, 1\/((2 + sqrt(2)) D^2))$.
  + (Attainment.) If every cosine lies in ${0, plus.minus 1, plus.minus 1\/sqrt(2)}$, $4 | D$ and $D >= 4\/(v_max - v_min)$, a renderer built from Pell approximations of $sqrt(2)$ achieves $max(abs(Delta_1), abs(Delta_2)) < 144 thin v_max \/ (sqrt(2) (v_max - v_min)^2 D^2)$. The separation is $Theta(1\/D^2)$.
  + (Trials.) A fixed-count design with $n >= 8 (3 + 2 sqrt(2))^2 D^4 ln(4\/epsilon) approx 271.8 thin D^4 ln(4\/epsilon)$ trials per setting has both errors at most $epsilon$, uniformly over $H_D$ and the Werner family (once $D^2 v_min >= 1\/(3 + 2 sqrt(2))$). Conversely, under the conditions of item 2, every design over cosines in ${0, plus.minus 1, plus.minus 1\/sqrt(2)}$, adaptive or not, needs $E_Q [n_"irr"] >= ((v_max - v_min) D \/ 12)^4 ln(1\/(4 epsilon)) \/ v_max^2$ trials at the settings with $abs(c) = 1\/sqrt(2)$. The order $D^4 log(1\/epsilon)$ is sharp for such designs.
  For any pair whose cosine ratio is a quadratic irrational, the $Omega(1\/D^2)$ separation still holds; no matching upper bound is claimed.
] <thm:pi4>
#proofsketch[Write $tau_i (Q) = m_i\/D$. If $(m_1, m_2) != 0$ then $m_1^2 - 2 m_2^2$ is a nonzero integer, so $abs(m_1 - sqrt(2) m_2) >= 1\/((1 + sqrt(2)) D)$, and the $v$-free identity $tau_1 \/ sqrt(2) - tau_2 = Delta_1\/sqrt(2) - Delta_2$ transfers this to the $Delta$'s. Attainment uses Pell pairs $(P_k, Q_k)$ with $P_k^2 - 2 Q_k^2 = plus.minus 1$. The converse is the KL chain rule with $KL <= chi^2 <= 2 Delta^2$ and the Bretagnolle–Huber inequality @bretagnolle1979; achievability is Hoeffding @hoeffding1963.]

#theorem(("ST-T289",), "new; standard", title: "universal converse and known unit visibility")[
  (a) For any family and angles, any adaptive design with a fixed horizon (or an almost surely bounded stopping time), $K$-outcome trials and $D > K\/4$: per-setting largest-remainder rounding gives $Q in H_D$ with Bhattacharyya coefficient at least $1 - K\/(4D)$, so both errors at most $epsilon < 1\/4$ require $n >= (4D\/K - 1) ln(1\/(4 epsilon))\/2$, which is $(D - 1) ln(1\/(4 epsilon))\/2$ for Bell trials. (b) With $v = 1$ known exactly and the angle set exactly to $cos theta_D = 1 - 2\/D$, every $Q in H_D$ has $TV(Q, P_1) >= 1\/D$ for even $D$, and a rare-outcome test with $n = 16 D ln(3\/epsilon)$ trials has both errors at most $epsilon$: the count is $Theta(D log(1\/epsilon))$. (c) At the fixed angle $pi\/4$ with $v = 1$ known and $D = 2^k$, $k >= 3$, the minimal TV is $TV_k = 2^(1-k) dist(2^(k-3) sqrt(2), ZZ)$, and the least trial count $n_k$ satisfies $(2 - sqrt(2)) ln(1\/(4 epsilon))\/(32 TV_k^2) <= n_k <= 8 ln(8\/epsilon)\/TV_k^2$.
] <thm:known>
#statusnote[Part (a) is standard; (b) and (c) are new. Part (b) needs $v = 1$ exactly: with $v_max < 1$ there are no rare outcomes and the mechanism disappears.]
#proofsketch[(a) assembles standard inequalities: optimal rounding (Hamilton apportionment), $H^2 <= ell_1$ for the squared Hellinger distance, Bhattacharyya tensorization and $1 - TV >= op("BC")^2\/2$ @lecam1964. (b) The adapted angle gives each rare outcome probability $1\/(2D)$, so the squared Hellinger distance is of order $1\/D$ rather than $TV^2 approx 1\/D^2$. (c) Optimal (largest-remainder) rounding applied to $D p = 2^(k-2) minus.plus 2^(k-3) sqrt(2)$.]

Part (c) ties the detection cost to an open problem in Diophantine approximation (@fig:precision c). An effective Liouville bound gives $n_k = O(16^k log(1\/epsilon))$; Ridout's $p$-adic Thue–Siegel–Roth theorem @ridout1957 (cited) gives $n_k <= c_e 4^((1 + e) k) log(1\/epsilon)$ for every $e > 0$, ineffectively; and $n_k = O(4^k log(1\/epsilon))$ holds iff $inf_m dist(2^m sqrt(2), ZZ) > 0$, that is iff the binary expansion of $sqrt(2)$ has bounded runs of equal digits, which is open @bugeaud2012 (#cid("ST-O04")).

#finitecheck(("ST-F57",), "finite check", title: "digits and constants")[
  With exact integer-square-root branch decisions and 80-digit arithmetic, for $k = 3, dots, 64$: $min_k 2^k TV_k = 0.01198$ (at $k = 32$) and $max = 0.994$; brute force over all grid laws confirms the formula for $k <= 5$. On a declared grid of 110 values of $D <= 10^4$ and $v in [1\/2, 1]$, $D^2 g_D >= 0.8368$ for $D >= 8$ (at $D = 200$), against the proved constant $1\/(3 + 2 sqrt(2)) approx 0.1716$ (@fig:precision b).
] <fc:digits>

For scale (illustration only; a 53-bit fixed-point grid, which IEEE-754 doubles are not): with $D = 2^53$ and $epsilon = 0.05$, any fixed-horizon design needs at least $7.2 times 10^15$ trials and the adapted design of @thm:known (b) suffices with $5.9 times 10^17$; with the ${0, pi\/4}$ schedule and $v in [1\/2, 1]$ the count lies between $3.2 times 10^58$ (necessary for such designs) and $7.8 times 10^66$ per setting (sufficient).

#figure(
  placement: auto,
  image("figures/fig2_precision.svg", width: 100%),
  caption: [Finite precision. *(a)* Correlator pairs $(tau_1, tau_2) = (m_1, m_2)\/D$ reachable by $H_(32)$ (small dots) and the pairs realized by Werner-shaped grid laws, $L_(32)^2$ (grey squares). The Werner image of the CHSH pair (both cosines $1\/sqrt(2)$) is a diagonal segment that passes through grid laws at $tau_1 = tau_2 in {3\/8, 1\/2, 5\/8}$ (filled circles), so the two hypotheses meet (#cid("ST-T287")); the image of the ${0, pi\/4}$ pair has irrational slope and misses every grid point (#cid("ST-T288")). *(b)* The scaled separation $D^2 g_D$, with $g_D$ the exact separation of @thm:pi4 between the grid and the ${0, pi\/4}$ segment for $v in [1\/2, 1]$, on the repository's declared grid; squares mark $D = 4P$ along Pell numerators. The dashed line is the proved constant $1\/(3 + 2 sqrt(2))$. *(c)* At the fixed angle $pi\/4$ with $v = 1$ known, $2^k TV_k = 2 dist(2^(k-3) sqrt(2), ZZ)$ follows the binary digits of $sqrt(2)$ (#cid("ST-F57")); whether it is bounded away from zero is open.],
) <fig:precision>

*Scope.* $D$ must be declared: the union of all $H_D$ contains every rational law and is dense, so with $D$ undeclared only non-uniform, eventually-correct procedures exist @cover1973 @dembo1994. A calibration uncertainty $kappa$ in the cosines voids the identifiability results once $kappa >= 144\/(sqrt(2) (v_max - v_min)^2 D^2)$ (@thm:pi4) or $kappa >= 2\/D$ (@thm:known (b), (c)). For odd $D$, or $D$ below the threshold, $H_D$ and the Werner family can be disjoint, and no separation rate is claimed there. Renderers that also discretize measurement angles, as in Palmer's proposal @palmer2020, and the finite-precision measurement models of Meyer and Kent @meyer1999 @kent1999 are outside scope; so are IEEE-754 renderers, non-stationary renderers and deterministic time-varying (sigma-delta) schedules, which may be nearly indistinguishable from the base law. The number-theoretic mechanism of @thm:pi4 (rational versus irrational cosines) is the same one Palmer uses @palmer2020; the novelty claimed is its application to $H_D$ under a visibility nuisance and the rates.

= Memory <sec:memory>

#reponote[Repository: `docs/bell-disk-renderer-memory.md`; module `src/simtheory/bell_disk_zonoid.py`; tests `tests/test_bell_disk_renderer_memory.py`.]

A *renderer state* emits one fixed law on (settings) $times {plus.minus 1}^2$; it need not belong to the family, need not have setting marginal $w$ and may even be signaling. $N_w (epsilon)$ is the least number of states such that every $q in bb(D)$ has a state within TV $epsilon$ of $P_q$; $N_w^"fam" (epsilon)$ requires each emission to be some $P_p$. The base-2 logarithm of $N_w$ lower-bounds the memory of any one-trial $epsilon$-accurate renderer. Let $A_w = area(Z^circle.small)$ be the area of the polar body of @eq:tv. Cauchy's formula gives $op("per")(Z) = 2$ for every schedule.

#theorem(("ST-T290",), "new as applied", title: "area converse")[
  For every rank-2 schedule and every $epsilon > 0$, $N_w (epsilon) >= pi \/ (A_w epsilon^2)$.
] <thm:area>
#proofsketch[For every sign vector $sigma in {plus.minus 1}^J$, testing $P_q$ against an arbitrary emission $Q$ with the function $sigma_j a b$ shows that $Q$ serves only states in $A_c = {q : sum_j (w_j\/2) abs(u_j dot q - c'_j) <= epsilon}$ for some real vector $c'$ determined by $Q$. The termwise triangle inequality gives $(A_c + (-A_c))\/2 subset epsilon Z^circle.small$, and planar Brunn–Minkowski (Brunn's central-section principle @schneider2014) gives $area(A_c) <= epsilon^2 A_w$. Count. The covering argument and Brunn's principle are classical; only the application to off-family Bell renderers is new.]

#theorem(("ST-T291",), "new; new as applied", title: "canonical CHSH")[
  With $G(epsilon)$ the number of grid squares of side $4 sqrt(2) epsilon$ meeting $bb(D)$,
  $ pi\/(32 epsilon^2) <= N_"CHSH" (epsilon) <= G(epsilon) <= pi (1 + 8 epsilon)^2 \/ (32 epsilon^2), $
  and, for $epsilon <= 1\/8$, the in-family count satisfies
  $ N^"fam"_"CHSH" (epsilon) <= pi (1 + 8 epsilon)^2\/(32 epsilon^2) + 3 pi \/ epsilon. $
  Hence $log_2 N_"CHSH" (epsilon) = 2 log_2 (1\/epsilon) + log_2 (pi\/32) + O(epsilon)$, for arbitrary and for in-family emissions.
] <thm:chsh-mem>
#statusnote[The upper bounds are new. The lower bound is @thm:area (new as applied); the lower constant $pi\/32$ also follows from the packing argument of #cid("ST-T05") with the square tiling.]
#proofsketch[Each grid square is a TV ball of radius $epsilon$. Squares that stick out of the disk emit the *clipped* law with correlators $op("clamp")(u_j dot z, -1, 1)$ at the square's center $z$, which is valid and, because clamping is 1-Lipschitz and fixes $u_j dot q$ for $q in bb(D)$, still within $epsilon$ of every state in the square. The in-family version splits boundary squares into quarters.]

The earlier constructive packing of #cid("ST-T13") gives $N >= ceil(1\/(4 epsilon))^2 approx epsilon^(-2)\/16$. What @thm:chsh-mem adds is the matching upper bound; the gain from $1\/16$ to $pi\/32 approx 0.09817$ over the #cid("ST-T13") construction is asymptotic: at finite $epsilon$ the valid lower bound is the larger of the two (at $epsilon = 3\/25$ the packing bound 9 exceeds $pi\/(32 epsilon^2) approx 6.82$). @fig:zonoid c compares the exact grid counts with these bounds.

#theorem(("ST-T292",), "standard", title: "universal ceiling")[
  For every finite schedule $A_w > pi^3$ strictly. Hence the area converse never exceeds $epsilon^(-2)\/pi^2$.
] <thm:ceiling>
#proofsketch[$A_w = (1\/2) integral_0^(2pi) h_Z^(-2) d theta$ and Jensen with $op("per")(Z) = 2$. This is the polar-area/perimeter inequality $area(K^circle.small) >= 4 pi^3 \/ op("per")(K)^2$, equivalent to Lutwak's planar dual mixed-volume inequality @lutwak1975; not new.]

#theorem(("ST-T293",), "new as applied", title: "tiling schedules are exact")[
  If $w$ has exactly two or three direction classes, $Z^circle.small$ is a parallelogram or a centrally symmetric hexagon, and $pi\/(A_w epsilon^2) <= N_w (epsilon) <= pi\/(A_w epsilon^2) + 2 op("per")(Z^circle.small)\/(A_w epsilon) + 4$. Thus $N_w (epsilon) epsilon^2 -> pi\/A_w$, and $N^"fam"_w$ has the same limit.
] <thm:tiling>
#proofsketch[Parallelograms and centrally symmetric hexagons tile the plane by translation @gruber2007; count tiles meeting the disk with Steiner's formula and emit clipped centers.]

#theorem(("ST-T294",), "new", title: "most memory with at most three classes")[
  (i) For two classes with weights $w_1, w_2$ at angle $alpha$, $A_w = 8\/(w_1 w_2 sin alpha) >= 32$, with equality iff the schedule is CHSH up to rotation. (ii) For three classes, $A_w >= 18 sqrt(3)$, with equality iff the weights are equal and the directions are $60 degree$ apart. (iii) Among rank-2 schedules with at most three classes, the largest memory constant $lim N_w epsilon^2 = pi\/A_w$ (the most memory forced) is $pi\/(18 sqrt(3)) approx 0.10077$, attained uniquely (up to rotation, as a law on classes) by the regular three-direction schedule.
] <thm:three>
#proofsketch[(i) Every parallelogram has Mahler product 8. (ii) A shoelace closed form, a substitution through the triangle with side lengths $sin$ of the three gaps (law of sines, Ravi substitution and Heron), and a polynomial inequality proved by a Lagrange analysis on the simplex and Schur's inequality. Every algebraic identity is checked exactly on random rational instances; 62468 rational grid cases give $min A approx 31.17919 > 18 sqrt(3) approx 31.17692$.]

The regular three-class law is realized when Alice and Bob each choose uniformly from ${0, pi\/3, 2pi\/3}$; that schedule contains a CHSH sub-test with $abs(S) = 5v\/2$ at $phi = 0$. The constants depend only on the law on direction classes, not on whether a realization admits a Bell violation.

#theorem(("ST-T295",), "new; new as applied; cited", title: "the hexagon does not force the most memory")[
  For every rank-2 schedule,
  $ pi\/A_w <= liminf N_w epsilon^2 <= limsup N_w epsilon^2 <= lim N^"fam"_w epsilon^2 <= theta_L (Z^circle.small) pi\/A_w <= 2\/(sqrt(27) pi) approx 0.12252, $
  where $theta_L$ is the lattice covering density; the in-family limit exists, and equals $theta_T (Z^circle.small) pi \/ A_w$ with $theta_T <= theta_L$ the translative covering density, by the asymptotic covering theorem @rogers1964. The regular four-direction schedule has $A_4 = 384 sqrt(2) - 512 approx 31.0580$, strictly between $pi^3$ and $18 sqrt(3)$ (certified with rational enclosures), so its lower constant $pi\/A_4 approx 0.10115$ exceeds the hexagon's exact constant. The supremum over finite schedules of $liminf N_w epsilon^2$ lies in $[1\/pi^2, 2\/(sqrt(27) pi)] = [0.10132, 0.12252]$.
] <thm:hexagon>
#statusnote[The lower end is @thm:area (new as applied). The upper end is classical and cited: the asymptotic covering theorem (Rogers) and Fejes Tóth's lattice covering bound. New: $A_4 < 18 sqrt(3)$, so the regular four-direction schedule forces more memory than the hexagon.]
#proofsketch[Lattice coverings of the plane by $Z^circle.small$, with clipped centers. The last inequality is L. Fejes Tóth's bound $theta_L (K) <= 2 pi\/sqrt(27)$ for centrally symmetric convex discs, with equality only for ellipses @fejestoth1950 @fejestoth1972 (cited; compare Kershner's disk covering density @kershner1939). The regular $m$-direction schedules have $A_m = 4 m^3 tan^2(pi\/(2m)) sin(pi\/m) -> pi^3$.]

#proposition(("ST-T296",), "elementary", title: "local and global rankings differ")[
  The center Fisher information is $I(0) = sum_j w_j u_j u_j^T$, of trace 1. CHSH and every regular $m$-direction schedule attain $I(0) = I\/2$ and are therefore simultaneously E-, A- and D-optimal at the center, yet their memory constants differ: $pi\/32 < pi\/(18 sqrt(3)) < pi\/A_4 <= liminf N_4 epsilon^2$, where $N_4$ is the count for the regular four-direction schedule. Local Fisher optimality does not rank schedules for memory forcing.
] <prop:fisher>

#figure(
  placement: auto,
  image("figures/fig3_zonoid.svg", width: 100%),
  caption: [Renderer memory. *(a)* Polar bodies $Z^circle.small$ of the CHSH, regular three- and four-direction schedules and the isotropic limit (a disk of radius $pi$). Their nearly equal areas $32 > 18 sqrt(3) > 384 sqrt(2) - 512 > pi^3$ order the area-converse constants $pi\/A_w$. *(b)* Constants for $N_w (epsilon) epsilon^2$, each a limit or a bound: the constructive packing of #cid("ST-T13") (a lower bound), the exact CHSH and hexagon limits (#cid("ST-T291"), #cid("ST-T294")), the certified lower bound $pi\/A_4$ for the regular four-direction schedule, the ceiling $1\/pi^2$ of the area converse (#cid("ST-T292")) and the upper bound from the cited Fejes Tóth bound (#cid("ST-T295")). The shaded interval contains the supremum over finite schedules of $liminf N_w epsilon^2$. *(c)* Exact CHSH grid counts at $epsilon = 1\/n$ from the receipt of #cid("ST-F58"), multiplied by $32 epsilon^2\/pi$: clipped-center covers $G$ and in-family covers $G + 3 G_"bd"$, where $G_"bd"$ is the number of grid squares that meet the disk without lying inside it. Both converge to 1. Dashed: the upper bound $(1 + 8 epsilon)^2$ of @thm:chsh-mem.],
) <fig:zonoid>

*Open problems.* The exact constant for arbitrary (off-family) emissions on non-tiling schedules, including whether the limit exists, is open (#cid("ST-O05")); the in-family constant is the classical translative covering density. @thm:three suggests a discrete dual-isoperimetric inequality $op("per")(P)^2 area(P^circle.small) >= 2 n^3 tan^2(pi\/n) sin(2 pi\/n)$ for convex $n$-gons containing the origin, of which (i) and (ii) are the centrally symmetric $n = 4, 6$ cases (#cid("ST-O06"), unproved; float experiments found no violation). If true, the regular four-direction schedule would minimize $A_w$, that is, maximize the area-converse constant, among schedules with at most four classes; since that schedule does not tile, this would not by itself give its memory constant.

= Communication, measurement dependence and detection <sec:frontiers>

#reponote[Repository: `docs/bell-escape-route-frontiers.md`; module `src/simtheory/bell_escape_routes.py`; tests `tests/test_bell_escape_route_frontiers.py`.]

This section is mostly an exact re-certification of known frontiers (@fig:frontiers); its purpose is to put them in a common form that a sequential test can use. A resource level $r$ indexes a class of classical simulators, and $f(r)$ bounds their per-trial CHSH win probability. The relaxed null is $cal(H)(f)$: $P(W_i = 1 | cal(F)_(i-1)) <= f$ almost surely for every trial $i$. Unless stated otherwise, the input bits $s, t$ are uniform and independent of the shared randomness and of the past, and budgets hold per trial conditionally on the past. Strategies are mixtures of deterministic ones, and cost and win probability are both linear in the mixture, so a linear inequality verified on every deterministic strategy is a dual certificate.

#figure(
  placement: top,
  image("figures/fig4_frontiers.svg", width: 100%),
  caption: [Classical escape routes for CHSH. *(a)* Exactly enumerated (cost, win) points of deterministic one-way signaling strategies (points with win $>= 0.45$ shown) and the two frontiers of #cid("ST-T282"). The Tsirelson rate $cos^2(pi\/8)$ costs $c = (sqrt(2) - 1)\/2$ with free silence and $c = sqrt(2) - 1$ with an $s$-blind send flag, Pironio's value. *(b)* Measurement-dependence frontier $1 - ell$ (#cid("ST-T283")); the Tsirelson rate needs $ell <= 1 - cos^2(pi\/8) approx 0.146$, the Delft empirical win rate $ell <= 0.2$. *(c)* The CH functional on the efficiency-$eta$ Tsirelson behavior; it is positive, and no local model exists, exactly above $eta^* = 2\/(1 + sqrt(2))$ (#cid("ST-M85")).],
) <fig:frontiers>

#theorem(("ST-T282",), "reproduces Pironio; new", title: "one-way signaling")[
  (a) If Alice may stay silent for free and the cost $c$ is the probability of a non-silent message, then $P("win") <= 3\/4 + c\/2$ on $[0, 1\/2]$ (so $S <= 2 + 4c$) and the bound is attained. (b) If the decision to communicate cannot depend on $s$, then $P("win") <= 3\/4 + c\/4$ ($S <= 2 + 2c$), attained; this is Pironio's bound, under which $sqrt(2) - 1$ bits are necessary and sufficient for the Tsirelson correlations @pironio2003. (c) One always-sent bit reproduces every binary-input behavior whose Alice marginal does not depend on $t$, including the PR box. Under the accounting of (a), letting silence stand for one of the two values (chosen with shared randomness) brings the expected cost to $c = 1\/2$, the endpoint of the (a) frontier; under the accounting of (b) the bit costs $c = 1$. One bit is the worst-case cost only.
] <thm:signal>
#statusnote[Part (b) is Pironio's bound. For part (a) we found no earlier statement, but it is the same game under a different accounting and may well be known. Part (c) is a trivial finite analogue of Toner and Bacon @toner2003.]
#proofsketch[(a) Per shared-randomness value, a strategy is either silent for both values of $s$ (local, win $<= 3\/4$, cost 0) or costs at least $1\/2$. All 2304 deterministic ternary-alphabet strategies are enumerated; the upper hull has vertices $(0, 3\/4), (1\/2, 1), (1, 1)$, and the dual inequality is tight on 128 and 64 strategies. A 4-symbol alphabet (16384 strategies) gives the same frontier. The gap between (a) and (b) is the information carried by the timing of silence. Related frameworks: worst-case cost @brassard1999 and one bit for continuous settings @toner2003.]

#theorem(("ST-T283",), "reproduces Pütz et al.", title: "measurement dependence")[
  If outputs are local and the input law may depend on the hidden variable $omega$ subject to $p(s, t | omega) >= ell$ for all $s, t, omega$, then $P("win") <= 1 - ell$, attained by a model whose observed input marginal is uniform; under uniform observed inputs $S <= 4 - 8 ell$ @putz2014. If each input bit has bias at most $beta$ given $omega$ and the other bit, $ell >= (1\/2 - beta)^2$ and the local bound $3\/4 + beta - beta^2$ is below the Delft $xi$.
] <thm:md>
#proofsketch[Every deterministic local strategy loses on at least one pair (parity), so $P("win" | omega) <= 1 - p(s_0, t_0 | omega)$. The attaining model mixes four strategies, each losing one pair, and puts mass $ell$ on its losing pair. The exact 16-strategy dual certificate and the attaining model are the new content; the bound is due to Pütz et al. @putz2014 (see also @putzgisin2016; Hall @hall2010 @hall2011 for other dependence measures; and @koh2012 for setting bias).]

#modelresult(("ST-M85",), "reproduces Garg and Mermin", title: "detection efficiency")[
  For the Tsirelson behavior with independent symmetric detection efficiency $eta$ and a no-click outcome, a local model exists iff $eta <= eta^* = 2\/(1 + sqrt(2)) approx 0.8284$ @garg1987 @larsson1998. The CH functional is at most 0 on all 81 deterministic three-outcome strategies and equals $eta^2 (1 + sqrt(2))\/2 - eta$ on the behavior; an explicit 17-strategy local model reproduces all 36 entries at $eta^*$ exactly in $QQ(sqrt(2))$.
] <mr:det>
This threshold is for the maximally entangled state; non-maximally entangled states lower it to $2\/3$ @eberhard1993 (cited, not treated here).

Write $d(p || f) = p ln(p\/f) + (1 - p) ln((1 - p)\/(1 - f))$ for the Bernoulli Kullback–Leibler divergence and $KL(dot || dot)$ for the general one.

#theorem(("ST-T284",), "new; reproduces van Dam, Gill and Grünwald", title: "statistical strength")[
  Under uniform inputs let $P_v$ win each pair with probability $p_v = (1 + v\/sqrt(2))\/2$. Over all local laws $L$ with uniform inputs, $min_L KL(P_v || L) = d(p_v || 3\/4)$ for $v >= 1\/sqrt(2)$ and 0 otherwise. At $v = 1$ this is $0.032074586$ nats $= 0.046273847$ bits @vandam2005.
] <thm:strength>
#statusnote[The value at $v = 1$ is that of van Dam, Gill and Grünwald @vandam2005; the visibility family and the data-processing proof are new.]
#proofsketch[Data processing onto the win indicator gives the lower bound with $L("win") <= 3\/4$; the uniform mixture of the eight strategies that lose exactly one pair attains it.]

#theorem(("ST-T281", "ST-T285"), "standard", title: "anytime-valid tests and their limits")[
  For $f in (0, 1)$ and bets $q in [f, 1]$, the factor $e(q, 1) = q\/f$, $e(q, 0) = (1 - q)\/(1 - f)$ has conditional mean at most 1 under $cal(H)(f)$, so data-independent mixtures over $q$ (and predictable bets) are test supermartingales, and $1\/sup_n E_n$ is an anytime-valid p-value by Ville's inequality @ville1939 @shafer2011 @howard2021 @ramdas2023. The uniform mixture has an exact rational closed form. Now let the truth $P$ be IID with win probability $p$ per trial, and let $E$ be an e-variable on $n$ trials that is valid at least against IID Bernoulli($f$), which $cal(H)(f)$ contains. Then $E_P [log E] <= n thin d(p || f)$ (Kelly @kelly1956 @grunwald2024). If an e-process rejects at $T = inf{n : E_n >= 1\/alpha}$ and $T$ is almost surely finite with finite mean under $P$, then $E_P [T] >= ln(1\/alpha) \/ d(p || f)$ (Wald @wald1945).
] <thm:anytime>

Test supermartingales for Bell experiments are standard @gill2014 @zhang2011, and the published Delft analysis is itself martingale based @elkouss2016. The point of stating them here is the composition: every frontier above has $f(r) >= 3\/4$, which is what @sec:delft exploits.

= Noise: the Le Cam deficiency of a Bell simulator <sec:noise>

#reponote[Repository: `docs/le-cam-deficiency-bell-simulator.md`; module `src/simtheory/le_cam_deficiency.py`; tests `tests/test_le_cam_deficiency_bell_simulator.py`.]

A simulator that renders visibility $lambda v$ instead of $v$ is a different experiment. How well can it be disguised by post-processing? One trial: a public setting $j$ is announced and the outcome law is the Werner law $P_v (a, b | j) = (1 - v a b thin c_j)\/4$ of @sec:disk, with $v in [0, 1]$. Assume equal magnitudes $abs(c_j) = C$ (CHSH has $C = 1\/sqrt(2)$); only the magnitudes enter the results. Write $sigma_j = -sgn(c_j)$, so that the event $a b = sigma_j$ has probability $(1 + v C)\/2$. The physics experiment is $cal(E) = {P_v}$, the simulator experiment $cal(F) = {P_(lambda v)}$, and the deficiency is $delta(cal(F), cal(E)) = inf_K sup_v "err"(K, v)$ over Markov kernels $K$, with error the TV of the joint (setting, outcome) law ("avg") or the worst setting ("max"). The reverse direction is free: the depolarizing kernel maps $P_v$ to $P_(lambda v)$ exactly, so $delta(cal(E), cal(F)) = 0$ @blackwell1951. The framework is Le Cam's @lecam1964. After the endpoint and sufficiency reductions in the proof below, the value is a deficiency between Bernoulli dichotomies, which is governed by Torgersen's dichotomy theory @torgersen1970 @torgersen1991 (see also @strasser1985); what is new is the closed form for this family and the deterministic gap (@fig:lecam).

#figure(
  placement: auto,
  image("figures/fig5_lecam.svg", width: 100%),
  caption: [Disguising visibility loss. *(a)* For canonical CHSH, the exact deficiency (#cid("ST-T306")) lies strictly between the two-point bound and the identity kernel; deterministic setting-preserving relabelings (#cid("ST-T309")) do strictly worse, whether errors are taken at the worst setting (line) or averaged over the schedule (exact values from `det_values`, circles). The band is the arithmetic range $lambda = S\/(2 sqrt(2))$ over the Delft $plus.minus 1 sigma$ interval (@sec:delft). *(b)* Error pairs at $lambda = 1\/2$. Deterministic relabelings are dominated by $R_1$, $R_2$, $R_3$; averaging across settings stays on the segment $R_1 R_3$, whose best point is $(1\/6, 1\/6)$. The one-parameter family of kernels that mix the identity with the overwrite inside one setting traces the V-shaped curve and reaches the diagonal at $delta$ (star).],
) <fig:lecam>

#theorem(("ST-T306", "ST-T307"), "new; standard", title: "exact one-trial deficiency")[
  Under equal magnitudes and central post-processing (the kernel sees both settings and both outcomes), for every full-support schedule and both aggregations,
  $ delta(cal(F), cal(E)) = (C (1 - lambda)) / (2 (2 - C lambda)). $ <eq:deficiency>
  Under "avg" the value is unchanged if kernels act on the whole record, so it is the Le Cam deficiency of the joint-record experiments. For canonical CHSH at $lambda = 1\/2$ it equals $1\/62 + (2\/31) sqrt(2) approx 0.10737$. For $0 < lambda < 1$ and $0 < C <= 1$, $C(1 - lambda)\/4 < delta < C(1 - lambda)\/2$: strictly above the two-point lower bound and strictly below the identity kernel. All three quantities vanish at $lambda = 1$. With unequal magnitudes and worst-setting aggregation, the deficiency is $V(max_j abs(c_j))$ with $V$ the right side of @eq:deficiency.
] <thm:deficiency>
#statusnote[The closed form is new; the framework and the reduction to Bernoulli dichotomies are standard (Le Cam; Torgersen).]
#proofsketch[Primal: keep the data with probability $1 - gamma$ and otherwise overwrite $b$ by $sigma_j a$, with $gamma = C(1 - lambda)\/(2 - C lambda)$; the errors at $v = 0$ and $v = 1$ are both $gamma\/2$, and convexity in $v$ reduces the supremum to the endpoints. Dual: a two-point Bayes problem with weight $rho = (1 - lambda C)\/(2 - lambda C)$ on $v = 0$ and the event $a b = sigma_j$ as test; the bound is linear in $K$, and its minimum over all kernels on the 16-cell joint record equals the formula exactly on both checked schedules.]

#theorem(("ST-T308",), "standard", title: "risk transfer")[
  For every bounded loss $L$ and decision rule $psi$, running $psi$ on the simulator's record after the optimal kernel changes the risk by at most $2 delta norm(L)_infinity$ at every $v$; under equal magnitudes this is tight for $norm(L)_infinity <= 1$. This is the easy direction of Le Cam's randomization criterion @lecam1964 @torgersen1991.
] <thm:risk>

#theorem(("ST-T309",), "new", title: "deterministic disguises are worse")[
  Restrict to deterministic setting-preserving kernels (a relabeling of $(a, b)$ chosen per setting). (a) Every one of the 256 relabelings of a setting has error pair $(e(0), e(1))$ dominated by one of $R_1 = (0, C(1-lambda)\/2)$, $R_2 = (1\/4, (1 - lambda C)\/4)$, $R_3 = (1\/2, (1 - C)\/2)$, for all $C, lambda in [0, 1]$. (b) The worst-setting deterministic value is $min(C(1 - lambda)\/2, 1\/4)$. (c) The schedule-averaged deterministic value is at least $(1 - lambda)\/(2(2 - lambda))$ if $1 - C < C(1 - lambda)$ and $C(1 - lambda)\/2$ otherwise. (d) For $0 < C < 1$ and $0 <= lambda < 1$ both deterministic values exceed $delta$ strictly.
] <thm:det>
#statusnote[The dominating-set step (a) is a computer-assisted exact proof.]
#proofsketch[(a) For fixed relabeling $g$, $e(1)$ minus the target is linear on each cell of an arrangement of at most four break lines in the triangle ${0 <= lambda C <= C <= 1}$, so nonnegativity at the 786 arrangement vertices, checked in exact rational arithmetic over all 256 maps, proves it everywhere. (c) Averaging error pairs across settings stays in the convex hull of ${R_1, R_2, R_3}$, which is the segment $R_1 R_3$ since $(R_1 + R_3)\/2 = R_2$. Mixing laws inside one setting cancels errors before the TV is taken; mixing error pairs across settings cannot.]

#finitecheck(("ST-F60",), "finite check", title: "canonical CHSH")[
  At $lambda = 1\/2$: $delta = 0.107369$, hull bound $1\/6$, exact averaged deterministic value $0.169194$, worst-setting deterministic value $0.176777$. Primal, dual and formula agree exactly on the grid $lambda in {0, 1\/8, dots, 1}$ for canonical CHSH and for a rational schedule ($C = 3\/5$, weights $1\/2, 1\/4, 1\/8, 1\/8$).
] <fc:lecam>

*Locality and scope.* The optimal kernel is a central post-processing: it sees both settings and both outcomes and writes $b := sigma_j a$, which is a signaling operation, not a Bell-local one. The deficiency under Bell-local post-processing is at least $delta$ and is not computed (a float LP probe recorded in the repository gave $0.1367$ against $0.1074$ at canonical $lambda = 1\/2$; it is not a certificate; compare the resource theory of nonlocality under wirings @gallego2012). Deterministic maps that may also relabel the setting are not covered by @thm:det; on the rational schedule of @fc:lecam they can beat the hull bound ($23\/160 < 3\/14$ at $lambda = 1\/4$), and whether they reach $delta$ is open. The $n$-trial deficiency and the averaged closed form for unequal magnitudes (#cid("ST-O08")) are open.

= Delft 2015 illustrations <sec:delft>

These are arithmetic illustrations on one data set under declared models. They are not claims about the Delft apparatus, and they are not evidence about simulation.

*A 5-bit renderer.* By @prop:chsh, the stationary renderer equal to the Werner law at $v^* = 5 sqrt(2)\/8$, that is, the law $(3\/32, 13\/32, 13\/32, 3\/32)$ on $(+ +, + -, - +, - -)$ at the three settings with $c_j = 1\/sqrt(2)$ and $(13\/32, 3\/32, 3\/32, 13\/32)$ at the setting with $c_j = -1\/sqrt(2)$, has $abs(S) = 4 tau = 5\/2$. This lies inside the reported interval $S = 2.42 plus.minus 0.20$ (#cid("ST-F50")\; @fig:delft a), and no CHSH data set of any size can separate this renderer from the Werner family with unknown visibility (#cid("ST-T287")). The CHSH schedule cannot see 5-bit precision. The ${0, pi\/4}$ schedule can, at a price: with $v in [1\/2, 1]$ and $epsilon = 0.05$, the sufficient count of @thm:pi4 is about $271.8 times 32^4 times ln 80 approx 1.2 times 10^9$ trials per setting, while its proved necessary count at $D = 32$ is only about 5 trials. The order $D^4$ is sharp only asymptotically, and the constants are far apart. The Delft fit lies in the visibility-phase family (#cid("ST-F51")), where adding the phase as a nuisance, if anything, makes non-identifiability easier (a remark in the repository, not a registered claim).

*Anytime-valid evidence.* The anytime-valid counterpart of the published fixed-$n$ p-value is much weaker, as the next check shows (@fig:delft b).

#finitecheck(("ST-F56",), "finite check", title: "Delft 2015, constant-bet mixtures, negative")[
  On the 245 valid trials in timestamp order, the uniform-mixture e-process against $f = 3\/4$ ends at $E_245 = 1.370$ and peaks at $2.782$ ($n = 6$, six straight wins), an anytime-valid $p = 0.36$; against $f = xi$ the values are $1.367$ and $2.782$. More strongly, every mixture of constant bets is bounded by the realized ceiling $U_n (f) = exp(n thin d(hat(p)_n || f))$ (or 1 when $hat(p)_n <= f$), which decreases in $f$; on the Delft data $max_(n <= 245) U_n (3\/4) = 7.7797$ (at $n = 241$, exact rational comparison). Since every frontier of @sec:frontiers has $f(r) >= 3\/4$, no constant-bet mixture on the win indicator rejects any resource level at $alpha = 0.05$: the confidence sets are the full ranges $c in [0, 1\/2]$, $c in [0, 1]$ and $ell in [0, 1\/4]$, and stay so for every $alpha < 0.1285$.
] <fc:anytime>

The contrast with the published $p = 0.039$ ($1\/p = 25.5$; this is not an e-value: the threshold e-variable $bb(1){K >= 196}\/P_xi (K >= 196)$ attains 25.5 only if the threshold had been fixed in advance, which it was not) is the price of optional stopping. The fixed-$n$ statement needs $n = 245$ to have been fixed independently of the data, which is not verified here, while the anytime statement needs no such assumption and delivers much less evidence. The negative result covers one test class only. It does not cover full-data test factors @zhang2011, tests valid only for the narrower escape-route classes, or predictable adaptive bets (tested plug-in bets reached running suprema of 1.65 and 1.90, and explorations of other adaptive bets reached at most 4.47; these are not a bound). Detection efficiency is not tested, since the experiment is event-ready. @thm:anytime gives a heuristic scale: at $alpha = 0.05$ against $xi$, any power-one e-process on the win indicator needs at least 93.4 trials in expectation at the Tsirelson rate and 428.3 at an IID win rate of 0.8, against $n = 245$. A chi-square test of uniform setting frequencies on the counts $(53, 79, 62, 51)$ gives 7.98 on 3 degrees of freedom ($p = 0.046$, fixed $n$). The frontiers of @sec:frontiers assume uniform settings; we do not adjust for this, and RNG independence enters only through $beta$.

*Visibility.* Reading $lambda = S\/(2 sqrt(2))$ in @eq:deficiency gives $lambda approx 0.856$ and $delta approx 0.036$, and the $1 sigma$ range of $S$ gives $delta in [0.019, 0.053]$ (@fig:lecam a). A renderer at that visibility could be post-processed to within that TV of ideal visibility-$v$ physics, uniformly in $v$, on the one-trial interface, and no post-processing could do better. The optimal post-processing is central, however: a float LP probe over Bell-local post-processing recorded in the repository returned the identity value $0.0509$ at $lambda = 0.856$ (not a certificate), so on that probe local post-processing gains nothing over doing nothing. This reading is an illustration, not a data claim; the Delft data are not modeled as this family.

#figure(
  placement: auto,
  image("figures/fig6_delft.svg", width: 100%),
  caption: [Delft 2015. *(a)* Running CHSH value with its $1 sigma$ band (repository `running_chsh`), against the local bound, the 5-bit renderer of @prop:chsh and Tsirelson's bound. *(b)* Anytime-valid e-processes on the CHSH win indicator (#cid("ST-F56")): the uniform mixture against $f = 3\/4$ and $f = xi$, and the realized ceiling $U_n (3\/4)$ that bounds every constant-bet mixture for every $f >= 3\/4$. The ceiling peaks at 7.78 and never reaches $1\/alpha = 20$. The $f = xi$ curve coincides with the $f = 3\/4$ curve at this scale. The cross marks $1\/p = 25.5$, shown for scale; it is neither an e-value nor anytime-valid.],
) <fig:delft>

= What the prices do and do not say <sec:limits>

*What is established.* For the declared CHSH family, precision and the communication and setting-dependence leaks have both a price and a detection cost; memory and visibility have one-trial prices only (memory exactly for schedules with at most three direction classes, and bracketed otherwise). A renderer that may dither cannot be seen at any precision. For $4 | D$ above the threshold, commensurable schedules, CHSH included, cannot see precision either; the ${0, pi\/4}$ pair sees it at order $D^4 log(1\/epsilon)$ for designs restricted to cosines in ${0, plus.minus 1, plus.minus 1\/sqrt(2)}$, and known unit visibility with an adapted angle sees it at order $D log(1\/epsilon)$. Memory is forced at rate $epsilon^(-2)$ with a schedule-dependent constant that local Fisher information does not detect. The communication and setting-dependence frontiers are linear and are unconstrained on Delft by constant-bet mixtures; detection is a threshold and is not tested there.

*Nonclaims.* We list them because each is easy to overread.
- Nothing here is evidence for or against the hypothesis that the world is simulated (#cid("ST-T01")): every result concerns declared restricted renderers, and a Bell violation is not evidence for simulation (#cid("ST-T09"), #cid("ST-F50")).
- Internal states and grid denominators are representational resources of a hypothetical renderer, not claims about the hardware of a parent universe (#cid("ST-T13"), #cid("ST-M03")); no claim is made that physical probabilities are or are not rational.
- All precision rates assume a declared $D$ and exactly known cosines; IEEE-754 floating point, non-stationary renderers, deterministic dithering schedules and angle discretization are outside scope. For odd $D$, or $D$ below the threshold, no separation rate is claimed.
- Memory results are one-trial bounds for the two-parameter coplanar family; they say nothing about $n$-trial, adaptive or transcript-level renderers, and clipped emissions need not be quantum-realizable.
- The escape-route frontiers assume per-trial budgets and (except for measurement dependence) uniform independent inputs; budgets that hold only on average need an Azuma-type argument that is not given. The Delft negative result concerns constant-bet mixtures on the win indicator only.
- The Delft setting counts give a fixed-$n$ chi-square $p = 0.046$ against uniform setting frequencies. The frontiers assume uniform settings, and nothing in @sec:delft adjusts for this.
- The deficiency is relative to the one-trial interface with central post-processing and equal magnitudes; Bell-local and $n$-trial deficiencies are not computed.
- Several numbers quoted as context (Bell-local LP values, adaptive-bet explorations) are float probes recorded in the repository and are labeled there as such; they are not certificates.
- Finite checks corroborate proofs on bounded instances; they are not proofs of asymptotic statements.
- Prior-art searches were not exhaustive; where we write "new" the claim is that no earlier statement was found.

= Open problems <sec:open>

+ *Binary digits of $sqrt(2)$* (#cid("ST-O04")). At the fixed angle $pi\/4$ with known unit visibility, is $n_k = O(4^k log(1\/epsilon))$? Equivalently, is $inf_m dist(2^m sqrt(2), ZZ) > 0$? Borel's normality conjecture would imply a negative answer @bugeaud2012.
+ *Free angles under unknown visibility* (#cid("ST-O04")). The minimax trial count lies between $Omega(D log(1\/epsilon))$ and $O(D^4 log(1\/epsilon))$. With $v_max < 1$ there are no rare outcomes, and $Theta(D^2 log(1\/epsilon))$ is plausible but unproved; with $v_max = 1$ the adapted-angle mechanism may give order $D$. For $J$ settings with simultaneously badly approximable cosine ratios, a separation of order $D^(-1 - 1\/(J-1))$ is expected and not proved.
+ *Off-family memory constants* (#cid("ST-O05")). Find $lim N_w epsilon^2$ (or show it exists) for non-tiling schedules, including the isotropic one, where only $[1\/pi^2, 2\/(sqrt(27) pi)]$ is known.
+ *A discrete dual-isoperimetric inequality* (#cid("ST-O06")). Prove or refute $op("per")(P)^2 area(P^circle.small) >= 2 n^3 tan^2(pi\/n) sin(2 pi\/n)$ for convex $n$-gons containing the origin.
+ *Entropy-cost communication frontier* (#cid("ST-O03")): the largest win probability given $H(M) <= h$ or $I(M; s) <= h$. No literature search for such frontiers was done.
+ *Joint leak frontier* (not registered as a claim): a frontier $f(c, ell, beta)$ for simultaneous signaling, setting dependence and RNG bias, derived rather than bounded below by $3\/4$. A joint measurement-dependence and detection-efficiency frontier with Hall's measure was posted by Alai (arXiv:2608.18886, 2026; unrefereed, not checked here); it uses a different dependence measure.
+ *Deficiency beyond one trial* (#cid("ST-O08")). The closed form under schedule averaging with unequal magnitudes; the $n$-trial deficiency; the deficiency under Bell-local post-processing; and whether deterministic maps that relabel settings can reach $delta$.

#v(0.4em)
*Reproducibility.* Every claim cited here is a record in `claims/*.json` of the repository @repo with its assumptions, nonclaims, evidence and tests; `uv sync && uv run python -m simtheory verify` validates all 465 claims, the real-data receipts and the per-claim tests; the 103 tests behind the claims cited here pass on the clone used for this paper. The six figures are produced by `figures.py` in this paper's directory, which imports the repository's own modules and committed Delft data. The references were resolved against Crossref (DataCite for the Delft data set) and their DOIs recorded in `refs.bib`, except for three older works that have none. This manuscript was drafted with AI assistance from the repository's claim records; every mathematical statement was checked against those records.

#v(0.6em)
#set text(size: 8.3pt)
#set par(spacing: 0.7em, leading: 0.5em)
#bibliography("refs.bib", title: "References", style: "ieee")

#pagebreak()
#set text(size: 10.2pt)
#set par(spacing: 0.95em, leading: 0.62em)
#heading(numbering: none)[Appendix: claim ledger]
#set text(size: 8.2pt)
Status terms are those of the Introduction; _context_ marks claims cited but not restated here, and _open_ marks open problems.
#v(0.3em)
#table(
  columns: (auto, auto, 1.5fr, 1fr),
  stroke: none,
  inset: (x: 4pt, y: 2.4pt),
  table.hline(stroke: 0.6pt),
  table.header([*ID*], [*Type*], [*Content in this paper*], [*Status*]),
  table.hline(stroke: 0.4pt),
  [ST-T01], [theorem], [equal observable laws give Bayes factor 1], [elementary],
  [ST-T05], [theorem], [approximate predictive-state packing (lower constant $pi\/32$ via square tiling)], [context],
  [ST-T09], [theorem], [Werner predictive-law TV geometry; its nonclaims exclude Bell violation as evidence for simulation], [context],
  [ST-T11], [theorem], [exact TV geometry of the visibility-phase family, @eq:tv], [elementary],
  [ST-T12], [theorem], [canonical CHSH metric $norm(dot)_infinity\/(2 sqrt(2))$ (@thm:metric[Thm])], [elementary],
  [ST-T13], [theorem], [constructive packing $ceil(1\/(4 epsilon))^2$], [context],
  [ST-T15], [theorem], [$h_Z$ is a norm iff the schedule is rank-2], [context],
  [ST-M03], [model result], [Bell visibility predictive-memory bound; bits are representational], [context],
  [ST-F50], [finite check], [Delft $n = 245$, $S = 2.422 plus.minus 0.204$, $p = 0.0392$ (@fc:delft[FC])], [finite check],
  [ST-F51], [finite check], [Delft disk point $(0.856, -0.094)$; $x = S\/(2 sqrt(2))$ (@fc:delft[FC])], [finite check],
  [ST-T286], [theorem], [dithering boundary (@thm:dither[Thm])], [standard],
  [ST-T287], [theorem], [commensurable schedules; CHSH; threshold counterexamples (@thm:commens[Thm], @prop:chsh[Prop], @nr:threshold[NR])], [new; finite check],
  [ST-T288], [theorem], [${0, pi\/4}$: $Theta(1\/D^2)$ separation, $Theta(D^4 log(1\/epsilon))$ trials (@thm:pi4[Thm])], [new],
  [ST-T289], [theorem], [universal converse; $Theta(D log(1\/epsilon))$ at $v = 1$ with adapted angle; $sqrt(2)$ digits (@thm:known[Thm])], [new; standard],
  [ST-F57], [finite check], [digit and constant tables (@fc:digits[FC])], [finite check],
  [ST-O04], [open problem], [rates for finite precision (open problems 1 and 2)], [open],
  [ST-T290], [theorem], [area converse $pi\/(A_w epsilon^2)$ (@thm:area[Thm])], [new as applied],
  [ST-T291], [theorem], [CHSH constant $pi\/32$; matching upper bound (@thm:chsh-mem[Thm])], [new; new as applied],
  [ST-T292], [theorem], [$A_w > pi^3$ (@thm:ceiling[Thm])], [standard],
  [ST-T293], [theorem], [tiling schedules exact (@thm:tiling[Thm])], [new as applied],
  [ST-T294], [theorem], [most memory with two or three classes (@thm:three[Thm])], [new],
  [ST-T295], [theorem], [bracket; regular four beats hexagon (@thm:hexagon[Thm])], [new; new as applied; cited],
  [ST-T296], [theorem], [Fisher isotropy ties (@prop:fisher[Prop])], [elementary],
  [ST-F58], [finite check], [exact zonoid audit, grid counts (@fig:zonoid c)], [finite check],
  [ST-O05, O06], [open problems], [off-family constant; $n$-gon inequality], [open],
  [ST-T281], [theorem], [conditional-null betting e-process (@thm:anytime[Thm])], [standard],
  [ST-T282], [theorem], [signaling frontiers (@thm:signal[Thm])], [reproduces Pironio; new],
  [ST-T283], [theorem], [measurement dependence (@thm:md[Thm])], [reproduces Pütz et al.],
  [ST-M85], [model result], [Garg–Mermin threshold certificate (@mr:det[MR])], [reproduces Garg and Mermin],
  [ST-T284], [theorem], [statistical strength $d(p_v || 3\/4)$ (@thm:strength[Thm])], [new; reproduces van Dam, Gill and Grünwald],
  [ST-T285], [theorem], [Kelly ceiling, Wald floor (@thm:anytime[Thm])], [standard],
  [ST-F56], [finite check], [Delft anytime negative result (@fc:anytime[FC])], [finite check],
  [ST-O03], [open problem], [entropy-cost frontier], [open],
  [ST-T306, T307], [theorem], [exact one-trial Le Cam deficiency (@thm:deficiency[Thm])], [new; standard],
  [ST-T308], [theorem], [risk transfer (@thm:risk[Thm])], [standard],
  [ST-T309], [theorem], [deterministic gap (@thm:det[Thm])], [new],
  [ST-F60], [finite check], [exact deficiency audit (@fc:lecam[FC])], [finite check],
  [ST-O08], [open problem], [averaged deficiency, unequal magnitudes], [open],
  table.hline(stroke: 0.6pt),
)
