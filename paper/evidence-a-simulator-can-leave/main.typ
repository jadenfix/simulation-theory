// How much evidence can a simulator leave?
// Built from the merged simulation-theory repository only (see Appendix A).
// Compile: python figures.py && python build.py (see README.md)

#let ink = rgb("#1d232b")
#let ink2 = rgb("#52514e")
#let c-thm = rgb("#2a78d6")
#let c-model = rgb("#1baf7a")
#let c-finite = rgb("#eb6834")
#let c-open = rgb("#4a3aa7")
#let c-std = rgb("#7d828a")

#set document(title: "How much evidence can a simulator leave?", author: "simulation-theory contributors")
#set page(
  paper: "us-letter",
  margin: (x: 1in, top: 0.95in, bottom: 0.9in),
  numbering: "1",
  number-align: center,
  header: context {
    if counter(page).get().first() > 1 [
      #set text(size: 8pt, fill: ink2)
      How much evidence can a simulator leave? #h(1fr) simulation-theory, main at `aa61193`
      #v(-0.45em)
      #line(length: 100%, stroke: 0.4pt + rgb("#d8d6d0"))
    ]
  },
)
#set text(font: "New Computer Modern", size: 10.2pt, fill: ink, lang: "en", region: "us")
#set par(justify: true, leading: 0.6em, spacing: 0.95em)
#set heading(numbering: "1.1")
#show heading.where(level: 1): it => {
  v(0.9em)
  set text(size: 12.5pt, weight: "bold")
  block(it)
  v(0.25em)
}
#show heading.where(level: 2): it => {
  v(0.5em)
  set text(size: 10.6pt, weight: "bold")
  block(it)
  v(0.1em)
}
#set math.equation(numbering: "(1)")
#show figure.caption: it => {
  set align(left)
  set text(size: 8.6pt)
  set par(justify: true, leading: 0.52em)
  block(width: 100%, inset: (x: 0.2em))[#strong[#it.supplement #context it.counter.display(it.numbering).] #it.body]
}
#show figure: set block(spacing: 1.3em)
#set table(stroke: none)
#show link: set text(fill: rgb("#1f5fa8"))
#show ref: set text(fill: rgb("#1f5fa8"))

#let KL = math.op("KL")
#let BF = math.op("BF")
#let TV = math.op("TV")
#let EE = $bb(E)$
#let PP = $bb(P)$

// Result boxes are labeled by their claim IDs; there is no separate running number.
#let result(kind: "Theorem", ids: none, status: none, title: none, color: c-thm, breakable: false, body) = {
  block(
    width: 100%,
    inset: (left: 9pt, right: 7pt, top: 6pt, bottom: 6pt),
    stroke: (left: 1.5pt + color),
    fill: color.lighten(95%),
    breakable: breakable,
    above: 1.0em,
    below: 1.0em,
  )[
    #strong[#kind #ids]#if title != none [ (#title)].
    #if status != none [#h(0.25em)#text(size: 8.4pt, fill: color.darken(25%))[#status]]
    #linebreak()
    #body
  ]
}
#let theorem = result.with(kind: "Theorem", color: c-thm)
#let standard = result.with(kind: "Theorem", color: c-std)
#let model = result.with(kind: "Model result", color: c-model)
#let finite = result.with(kind: "Finite check", color: c-finite)
#let openp = result.with(kind: "Open problem", color: c-open)
#let proof(body) = block(above: 0.6em, below: 0.9em)[_Proof._ #body #h(1fr) $square$]
#let sketch(body) = block(above: 0.6em, below: 0.9em)[_Proof sketch._ #body #h(1fr) $square$]
#let remark(title, body) = block(above: 0.8em, below: 0.8em)[#emph[#(title).] #body]

// ------------------------------------------------------------------ title
#align(center)[
  #v(0.2em)
  #text(size: 19pt, weight: "bold")[How much evidence can a simulator leave?]
  #v(0.15em)
  #text(size: 11pt, fill: ink2)[Explicit evidence rates, a one-draw cap, and what the NIST beacon and Delft 2015 data do and do not show]
  #v(0.6em)
  #text(size: 10pt)[simulation-theory contributors]
  #v(0.05em)
  #text(size: 8.6pt, fill: ink2)[#link("https://github.com/jadenfix/simulation-theory")[github.com/jadenfix/simulation-theory] #h(0.6em) main at `aa61193` (results merged in PR \#72, `0c77232`) #h(0.6em) 18 October 2026]
]
#v(0.5em)
#block(width: 100%, inset: (x: 2.2em))[
  #set text(size: 9.2pt)
  #set par(leading: 0.55em)
  #strong[Abstract.] A simulator that reproduces the observable law of ordinary physics leaves no evidence: every test has power equal to its size and every Bayes factor equals one (ST-T01). We ask how much evidence a _restricted_ simulator can leave, using results stated with typed assumptions in a public claim ledger whose receipts and tests are re-run automatically. When the simulated law differs from the base law within a world, the expected log Bayes factor of the Krichevsky-Trofimov test against fair bits is $n KL(q || 1\/2) - 1\/2 ln n$ plus a constant that lies in an explicit window of width 1.47 nats for every $n$; a sufficient power frontier and a Le Cam converse bracket the detectable biases up to a $sqrt(ln n)$ factor. When two hypotheses differ only in the weights they put on one persistent world, no transcript yields more than $KL(a || b)$ nats in expectation, and the shortfall is an exact posterior-disagreement term. Under optional stopping, Kelly's ceiling and Wald's floor bound e-processes on the CHSH win indicator. On 131072 NIST beacon bits the composite test does not reject, and a fixed-$n$ test would have caught any IID bias $|q - 1\/2| >= 0.0087$ with probability at least 0.95. The 245 Delft 2015 trials give $S = 2.42 plus.minus 0.20$ and fixed-$n$ $p = 0.039$, but under anytime-valid inference no mixture of constant bets on the win indicator exceeds 7.78, against a threshold of 20. None of this is evidence for or against simulation.
]
#v(0.2em)
#block(width: 100%, inset: (x: 2.2em))[
  #set text(size: 8.4pt, fill: ink2)
  #strong[Reading the claim IDs.] ST-T: theorem (follows from its stated assumptions); ST-M: model result (exact inside one declared model); ST-F: finite check (reproducible computation on a bounded domain or fixed data set); ST-O: open problem. Each ID is a record in `claims/*.json` with scope, assumptions, evidence paths and nonclaims, and `uv run python -m simtheory verify` validates every record and re-runs its receipts and tests; the proofs themselves are written out in derivation documents and are not formally verified. Boxes are colored by type; gray boxes are standard or cited results restated for the simulator interface, and their status line names the source.
]

// ------------------------------------------------------------------ 1
= Introduction

The simulation hypothesis is usually argued with priors and reference classes @bostrom2003. A smaller literature asks for observable signatures: lattice artifacts in the highest-energy cosmic rays @beane2014, or outcome probabilities computed to finite precision @buniy2005 @palmer2020. Before asking whether a signature is present, a statistician asks a prior question: given the observable law a simulator would induce, how much evidence can that law carry, how fast does it accumulate, and how much of it survives when the analyst may stop whenever the data look interesting? This paper answers that question for the cleanest cases, using only results that are proved, or computed exactly on a bounded domain, and registered in the `simulation-theory` repository, and then applies the answers to two public data sets.

The starting point is a triviality with large consequences. If a simulator reproduces the base law exactly, every statistic has the same distribution under both hypotheses and the Bayes factor is identically one (ST-T01, @sec-boundary). The generic hypothesis "some external process generates our observations" is therefore not identifiable, and nothing in this paper is evidence that reality is or is not simulated. All of the content lies on the other side of the boundary, in _restricted_ simulators whose law is declared and differs from the base law. There the question becomes quantitative, and it splits into two regimes that turn out to behave very differently (@fig-evidence).

#figure(
  placement: auto,
  image("figures/fig_evidence.svg", width: 100%),
  caption: [The two regimes. *(a)* Per-world signal (@sec-sandwich). The additive constant $EE_q [ln BF_n] - n KL(q || 1\/2) + 1\/2 ln n$ of the Krichevsky-Trofimov Bayes factor against fair bits, for four sources. Every source stays in the shaded window of ST-T273 for every $n$; interior sources converge to the Clarke-Barron constant $1\/2 ln(2e\/pi)$ (ST-T274) and the boundary source $q = 0$ to $-1\/2 ln pi$. Evidence itself grows linearly at rate $KL(q || 1\/2)$. *(b)* Only the weights on one persistent world differ (@sec-cap). Exact transcript KL for three examples of the audit ST-F55 and ST-T280, computed with the repository's exact routine `persistent_audit`. With a shared kernel the evidence saturates at the cap $KL(a || b)$ (ST-T277), and stops short of it when two components share a law; only a difference in the per-world kernels lets it grow without bound, and then by at most the within-world divergence (dotted).],
) <fig-evidence>

*Per-world signal.* If the simulated source has a different law in each world (a bias $q != 1\/2$ in a bit stream, say), expected evidence grows linearly with the number of trials at the Kullback-Leibler rate, minus a logarithmic penalty for not knowing $q$. We pin down that penalty to an explicit window valid for every $n$, identify its limit, and give a sufficient detection frontier and a converse, which do not match: they differ by a factor of order $sqrt(ln n)$ (@sec-sandwich).

*Weights over one world.* If two hypotheses share the per-world law and differ only in how often they would produce each world (the shape of most ensemble and anthropic arguments), then one persistent world can be observed forever and still yield at most $KL(a || b)$ nats of expected evidence about those weights (@sec-cap). We give the exact shortfall, its decay rate, and counterexamples to two tempting strengthenings.

*Optional stopping.* Fixed-$n$ $p$-values assume the sample size was fixed in advance. Test supermartingales do not, and Kelly's and Wald's classical bounds say how much they can grow and how long they must run (@sec-anytime).

*Real data.* The NIST randomness beacon shows no detectable bias: its final log Bayes factor is within one $chi_1^2 \/ 2$ fluctuation (about 0.6 standard deviations) of the fair-bit expectation (ST-T273, ST-T274), and the power frontier turns "did not reject" into an explicit statement about which IID biased sources were excluded. The Delft 2015 loophole-free Bell test violates the CHSH bound at fixed $n$ but carries little anytime-valid evidence: no constant-bet mixture on the win indicator gets past 7.78 at any prefix (@sec-data).

#figure(
  placement: auto,
  {
  set text(size: 8.2pt)
  set par(justify: false)
  table(
    columns: (auto, auto, 1.3fr, 1.1fr),
    align: (left, left, left, left),
    inset: (x: 4pt, y: 2.7pt),
    table.hline(stroke: 0.7pt),
    table.header([*Claim*], [*Type*], [*Statement*], [*Status*]),
    table.hline(stroke: 0.4pt),
    [ST-T01], [theorem], [equal laws give power = size and $BF = 1$], [elementary, not new],
    [ST-T272], [theorem], [pathwise KT sandwich for every $n$, $x$], [upper bound classical @kt1981 @wst1995; uniform lower bound stated, no priority claimed (cf. @freund1996 @xiebarron2000)],
    [ST-T273], [theorem], [expected sandwich of width 1.47 nats for every $n$, $q$], [expected upper bound new; lower bound is ST-T271],
    [ST-T274], [theorem], [limit constant $1\/2 ln(2e\/pi)$], [Clarke-Barron @clarkebarron1990, specialized],
    [ST-T275/276], [theorem], [sufficient power frontier; Le Cam two-point converse], [standard ingredients],
    [ST-M84], [model], [binary symmetric coarsening rescales the frontier], [extends ST-M83],
    [ST-T277], [theorem], [one-draw cap $KL(a K || b K) <= KL(a || b)$], [data processing, standard],
    [ST-T278], [theorem], [saturation identity; finite-$M$ zero-gap condition], [chain rule and Kullback-Leibler; only the ratio form is stated],
    [ST-T279], [theorem], [gap $<= (R-1) P_a ("err")$ + mismatch; Chernoff decay], [$(R-1)$ factor and mismatch term new],
    [ST-T281/285], [theorem], [betting e-processes; Kelly ceiling, Wald floor], [standard],
    [ST-T282/283], [theorem], [signaling and setting-dependence CHSH frontiers], [(b) Pironio @pironio2003, (d) Pütz et al. @putz2014; certificates new],
    [ST-T284], [theorem], [uniform-setting statistical strength $KL(w_v || 3\/4)$], [$v = 1$ value from @vandam2005],
    [ST-T286 to 289], [theorem], [finite precision: dithering boundary, non-identification, separation and sample-size rates], [ST-T286 is Madow's construction @madow1949; ST-T289(a) uses standard inequalities],
    [ST-T290 to 295], [theorem], [renderer memory: area converse, CHSH constant $pi\/32$, polar-area bounds], [packing and covering arguments classical @rogers1964 @lutwak1975; matching bounds for arbitrary emissions new],
    [ST-T297/301/304], [theorem], [two-view fiber; binary identified set; flat Bayes factors in a fiber], [ST-T301 specializes @hks2014; ST-T304 standard],
    [ST-T306/308], [theorem], [deficiency of a visibility-contracted simulator; risk transfer], [closed form only; ST-T308 standard],
    [ST-F52/53/54], [finite], [NIST beacon: Ville check, sandwich consistency, power frontier], [bounded],
    [ST-F50/51], [finite], [Delft 2015: $S = 2.42 plus.minus 0.20$, $p = 0.039$, disk point], [bounded],
    [ST-F56], [finite], [Delft anytime check: realized ceiling 7.78 < 20], [negative result],
    table.hline(stroke: 0.7pt),
  )},
  caption: [The claims used in this paper. The full map from claim IDs to code, tests and receipts is in Appendix A. "Standard" means the statement restates or specializes a known result, which the claim's nonclaims attribute.],
  kind: table,
) <tab-claims>

*What is new and what is not.* Most tools here are classical: data processing, the KL chain rule, the Clarke-Barron expansion, the Krichevsky-Trofimov regret bound, Le Cam's two-point method, Ville's inequality, Kelly's and Wald's bounds. The contribution is (i) explicit non-asymptotic constants: the expected upper bound of ST-T273, and the uniform pathwise lower regret bound of ST-T272, which is stated with an explicit constant but for which no priority is claimed, since two-sided pathwise KT and Jeffreys regret bounds appear in @freund1996 @xiebarron2000; (ii) the gap bound ST-T279 and the counterexamples recorded with it; (iii) exact frontiers and an exact negative check on real data; and (iv) a disciplined separation, claim by claim, of what is proved, what is computed on a bounded domain, what is cited and what is open (@tab-claims). Every number in this paper comes from the repository's receipts and derivation documents or from the figure script, which asserts agreement with the receipts (Appendix A).

*Notation.* $ln$ is the natural logarithm; $O(log n)$ is written only where the base is irrelevant. For numbers $p, f in [0, 1]$, $KL(p || f)$ is the divergence between Bernoulli laws. In @sec-sandwich, $q$ is the bias of a bit source, $n$ the number of bits and $k$ the number of ones. In @sec-cap, $a$ and $b$ are hypotheses (laws of a latent world $M$), $K$ is a Markov kernel with components $K_m = K(dot | m)$, and $T$ is a transcript length. In @sec-anytime and @sec-data, $k$ counts CHSH wins, $f$ bounds the conditional win probability, $u$ is a constant bet, $nu$ a mixing law over bets, $T_alpha$ a stopping time, $omega$ a resource level, $tau$ the Delft setting predictability and $z = (x, y)$ a point of the CHSH disk. $kappa$ is a binary-symmetric flip probability, and $pi$ is always the constant.

// ------------------------------------------------------------------ 2
= The indistinguishability boundary <sec-boundary>

Let $(cal(X), cal(F))$ be the observable space of one experiment, $P_B$ the law of a base physical model and $cal(S)$ a class of simulators, each $S in cal(S)$ inducing a law $P_S$ on $(cal(X), cal(F))$.

#standard(ids: "ST-T01", status: [elementary, not claimed as new], title: "unrestricted indistinguishability")[
  If $cal(S)$ contains a member $S^*$ with $P_(S^*) = P_B$, then every randomized test $phi: cal(X) -> [0, 1]$ satisfies $EE_(S^*) [phi] = EE_B [phi]$, so a level-$alpha$ test has power at most $alpha$ against $S^*$; and $BF_(S^* : B)(x) = p(x | S^*) \/ p(x | B) = 1$ wherever the ratio is defined, so posterior odds equal prior odds.
]
#proof[$EE_(S^*) [phi] = integral phi dif P_(S^*) = integral phi dif P_B$, and the densities coincide.]

The boundary is sharp in a quantitative sense. If the likelihood ratio is confined to $[e^(-epsilon), e^epsilon]$, Bayes' rule in log-odds form gives $|ln "posterior odds" - ln "prior odds"| <= epsilon$ (ST-T02, elementary). Evidence requires the laws to differ, and it is bounded by how much they differ.

The boundary reappears inside restricted, otherwise informative models, which is a useful warning about signature hunting:

- *Finite precision with free dithering.* If a renderer that stores outcome probabilities on a grid $(1\/D) bb(Z)$ may draw a fresh private index on every trial, it realizes every law exactly (systematic dithering, Madow's construction @madow1949), so finite precision is untestable unless a no-dithering restriction is declared (ST-T286). With private randomness of precision $J$ only the product $D J$ is observable.
- *Two views of a latent mixture.* Two conditionally independent views of one persistent latent, through a shared channel of full row rank with the number $k$ of latent states known, identify the prior only up to an orthogonal fiber (ST-T297). Inside a fiber every Bayes factor equals one for every data set (ST-T304, the standard fact that data do not update non-identified directions @kadane1974 @dawid1979 @poirier1998). For a binary latent the prior weight is set-identified with sharp, piecewise-rational endpoints (ST-T301); this closed form specializes the two-component bounds of Henry, Kitamura and Salanié @hks2014[Thm. 1] to a shared channel, the feasible-band mechanism goes back to Lawton and Sylvestre @lawton1971, and no priority is claimed.
- *Coarsening.* A binary symmetric channel with flip probability $1\/2$ erases every bias, an instance of ST-T01 at the endpoint $kappa = 1\/2$ of ST-M83.

#remark[Two ways to differ][Let a latent world $M$ take values in a standard Borel space, let hypotheses $a$ and $b$ be laws of $M$, and let a Markov kernel $K(dif y | m)$ generate the transcript $Y$, which may be of any length, randomly stopped or adaptive, provided the experimenter's policy does not depend on the hypothesis label. Write $a ⊗ K$ for the joint law of $(M, Y)$ and $a K$ for its $Y$-marginal, the transcript law $P_a^Y$. The hypotheses can differ in the _per-world law_ (different kernels $K^a != K^b$, or $a$ not absolutely continuous with respect to $b$), or only in the _world weights_ ($K^a = K^b$ and $KL(a || b) < infinity$). @sec-sandwich treats the first regime with a bit source, @sec-cap the second in general. The dividing line is not "fresh versus persistent" randomness: the alternative of @sec-sandwich also draws its bias $q$ once and then emits conditionally IID bits. Averaging it over $q$ gives $a = "Jeffreys"$ and $b = delta_(1\/2)$, for which $a$ is not absolutely continuous with respect to $b$ and the cap of @sec-cap is $+infinity$.]

// ------------------------------------------------------------------ 3
= Per-world signal: the sandwich, its constant and its converse <sec-sandwich>

Let $x in {0, 1}^n$ have $k$ ones and empirical frequency $hat(q) = k\/n$. The restricted simulation hypothesis says the bits are IID Bernoulli$(q)$ with $q$ unknown and Jeffreys prior $w(q) = 1\/(pi sqrt(q (1-q)))$; the base hypothesis says they are fair. The Bayes factor is the Krichevsky-Trofimov (KT) mixture @kt1981 against fair bits (its classical regret bound is in @kt1981 @wst1995),
$ BF_n (x) = 2^n integral_0^1 q^k (1-q)^(n-k) w(q) dif q = (binom(2k, k) binom(2n - 2k, n - k)) / (2^n binom(n, k)), $ <eq-bf>
exact in rational arithmetic (the receipt matches it against the sequential KT product on all 8190 sequences with $n <= 12$). Writing $rho_n (x) = ln[max_q P_q (x) \/ P_"KT" (x)]$ for the KT regret, $ln BF_n (x) = n KL(hat(q) || 1\/2) - rho_n (x)$ pathwise. Under fair bits $BF_n$ is a nonnegative martingale with mean one, so Ville's inequality @ville1939 makes "reject when $sup_n BF_n >= 1\/alpha$" a level-$alpha$ test under optional stopping.

#theorem(ids: "ST-T272", status: [upper regret bound classical @kt1981 @wst1995; uniform lower bound stated with an explicit constant, no priority claimed], title: "pathwise sandwich")[
  For every $n >= 1$ and every $x in {0, 1}^n$,
  $ 1/2 ln (pi n)/2 < rho_n (x) <= 1/2 ln n + ln 2, $
  equivalently $n KL(hat(q) || 1\/2) - 1\/2 ln n - ln 2 <= ln BF_n (x) < n KL(hat(q) || 1\/2) - 1\/2 ln n - 1\/2 ln(pi\/2)$. The upper regret bound is attained only at $n = 1$.
]
#sketch[Let $h(x) = ln Gamma(x + 1\/2) - x ln x + x - 1\/2 ln(2 pi)$. Its derivative $psi(x + 1\/2) - ln x = integral_0^infinity e^(-x t) (1\/t - 1\/(2 sinh(t\/2))) dif t$ is positive, and $h -> 0$, so $Gamma(x + 1\/2) < sqrt(2 pi) x^x e^(-x)$ and $h(x) >= h(1) = 1 - 3\/2 ln 2$ for $x >= 1$ (both inequalities are known; the proof is included for completeness). For $1 <= k <= n - 1$, $P_"KT" = Gamma(k + 1\/2) Gamma(n - k + 1\/2) \/ (pi n!)$; the first inequality with Robbins' lower Stirling bound @robbins1955 gives $P_"KT" < max_q P_q dot sqrt(2\/(pi n))$, the lower regret bound. The second, with Robbins' upper bound, gives $rho_n <= 1\/2 ln n + 0.347$ for $n >= 2$. The cases $k in {0, n}$ follow the same way, and $rho_1 = ln 2$. The receipt checks $"ratio"^2 <= 4n$ in exact rationals on every count vector with $n <= 128$; the minimum lower margin is 0.00195. Two-sided pathwise KT and Jeffreys regret bounds also appear in @freund1996 @xiebarron2000.]

#theorem(ids: "ST-T273", status: [expected upper bound new; lower half is ST-T271 (standard)], title: "non-asymptotic expected sandwich")[
  For every $q in [0, 1]$ and $n >= 1$, $EE_q [ln BF_n] = n KL(q || 1\/2) - R_n (q)$ with $R_n (q) = KL(P_q^n || P_"KT") >= 0$, and
  $ n KL(q || 1/2) - 1/2 ln n - ln 2 <= EE_q [ln BF_n] <= n KL(q || 1/2) - 1/2 ln n + 1 - 1/2 ln pi/2 . $ <eq-sandwich>
]
#proof[Write $EE_q [ln BF_n] = n KL(q || 1\/2) + EE_q [n KL(hat(q) || q)] - EE_q [rho_n]$; this holds because $KL(hat(q) || 1\/2) - KL(hat(q) || q)$ is affine in $hat(q)$ with mean $KL(q || 1\/2)$. Then $0 <= EE_q [n KL(hat(q) || q)] <= EE_q [n chi^2(hat(q) || q)] = n "Var"(hat(q)) \/ (q (1 - q)) = 1$ (checked exactly in Fractions), and ST-T272 bounds $rho_n$ on both sides.]

The upper constant is $1 - 1\/2 ln(pi\/2) approx 0.7742$, so the window in @eq-sandwich has width $1 + ln 2 - 1\/2 ln(pi\/2) approx 1.47$ nats, uniformly in $n$ and $q$. The window is explicit but not sharp; ST-T274 gives the limit. The pathwise window of ST-T272 has width $ln 2 - 1\/2 ln(pi\/2) approx 0.47$.

#standard(ids: "ST-T274", status: [Clarke-Barron expansion specialized; not new, re-derived self-containedly], title: "the constant")[
  For fixed $q in (0, 1)$, as $n -> infinity$,
  $ EE_q [ln BF_n] = n KL(q || 1/2) - 1/2 ln n + 1/2 ln (2e)/pi + o(1), quad 1/2 ln (2e)/pi = 0.274209 dots $
  and for $q in {0, 1}$, $EE_q [ln BF_n] = n ln 2 - 1\/2 ln n - 1\/2 ln pi + o(1)$. The $o(1)$ is pointwise in $q$, not uniform near the boundary.
]
Clarke and Barron @clarkebarron1990 @clarkebarron1994 give $R_n (q) = 1\/2 ln(n\/(2 pi e)) + 1\/2 ln I(q) + ln(1\/w(q)) + o(1)$; with the Bernoulli Fisher information and the Jeffreys prior, $1\/2 ln I + ln(1\/w) = ln pi$, which is the stated constant (see also @xiebarron1997 @xiebarron2000). The repository's re-derivation shows $EE_q [n KL(hat(q) || q)] -> 1\/2$ by uniform integrability and $EE_q [rho_n] = 1\/2 ln(pi n\/2) + o(1)$ by dominated convergence, using the bounds on $h$ from the proof of ST-T272; the boundary case is Wallis' formula. At $q = 1\/2$ the expected log Bayes factor is $-1\/2 ln n + 0.274 + o(1)$: a simulator that matches the fair law is penalized, slowly, by the composite alternative.

#finite(ids: "ST-F53", status: [bounded], title: "remainder table")[
  With 60-digit arithmetic, the remainder $Delta_n (q) = EE_q [ln BF_n] - [n KL(q || 1\/2) - 1\/2 ln n + 1\/2 ln(2e\/pi)]$ satisfies $|Delta_n| <= 6 times 10^(-5)$ at $n = 5000$ on $q in {1\/10, 1\/5, 1\/4, 1\/3, 2\/5, 1\/2}$, and @eq-sandwich holds strictly on every table entry. At beacon scale ($q = 1\/2$, $n = 131072$) the exact expectation is $-5.617542$, and the asymptotic formula agrees to $9.7 times 10^(-12)$.
]

#openp(ids: "ST-O02", status: [heuristically derived; remainder control not written])[
  Is $Delta_n (q) = (1 - 2q)^2 \/ (24 n q (1 - q)) + O(n^(-2))$ for interior $q$? At $n = 5000$, $n Delta_n$ is 0.2970, 0.0939, 0.0557, 0.0209 and 0.0070 at $q = 1\/10, 1\/5, 1\/4, 1\/3, 2\/5$; the conjectured values are 0.2963, 0.0938, 0.0556, 0.0208 and 0.0069.
]

== Which biases are detectable

#theorem(ids: "ST-T275", status: [elementary; uses binary Pinsker and Hoeffding @hoeffding1963], title: "pathwise rejection region and power frontier")[
  Fix $alpha, beta in (0, 1)$ and let
  $ d_n = sqrt((ln(1\/alpha) + 1\/2 ln n + ln 2) / (2n)), quad e_n = sqrt((ln(1\/alpha) + 1\/2 ln(pi n\/2)) / (4n)), quad t_n = sqrt(ln(1\/beta) / (2n)). $
  (i) If $|hat(q) - 1\/2| >= d_n$ then $BF_n >= 1\/alpha$. (ii) If $BF_n >= 1\/alpha$ then $|hat(q) - 1\/2| >= e_n$. (iii) If $|q - 1\/2| >= d_n + t_n$ then $PP_q (BF_n >= 1\/alpha) >= 1 - beta$. Under fair bits the test has level $alpha$ even with optional stopping.
]
#proof[(i) combines the lower half of ST-T272 with $KL(p || 1\/2) >= 2 (p - 1\/2)^2$; (ii) combines the upper half with $KL(p || 1\/2) <= chi^2 = 4 (p - 1\/2)^2$; (iii) if the test fails to reject then $hat(q) < 1\/2 + d_n <= q - t_n$, an event of probability at most $exp(-2 n t_n^2) = beta$ by Hoeffding.]

#standard(ids: "ST-T276", status: [Le Cam two-point method with Pinsker and Bretagnolle-Huber; not new], title: "converse")[
  Let $phi$ be any randomized test on $n$ IID bits with $EE_(1\/2) phi <= alpha$ and $EE_q phi >= 1 - beta$. Then $|q - 1\/2|$ is at least the largest of $(1 - alpha - beta)\/sqrt(2n)$ (if $alpha + beta < 1$) and $sqrt(ln(1\/(2(alpha + beta)))\/(4n))$ (if $alpha + beta < 1\/2$). Sequential tests that stop by time $n$ are covered.
]
#proof[$KL(P_q^n || P_(1\/2)^n) <= 4 n (q - 1\/2)^2$. Pinsker: $1 - alpha - beta <= TV <= sqrt(KL\/2)$. Bretagnolle-Huber @bretagnollehuber1979: $alpha + beta >= integral min(dif P_(1\/2), dif P_q) >= e^(-KL) \/ 2$. See @lecam1973 and @tsybakov2009[Lemma 2.6].]

The converse is of order $1\/sqrt(n)$ while the sufficient KT frontier carries an extra $sqrt(ln n)$; they do not match, and the exact Neyman-Pearson power is the sharp benchmark against a single alternative (computed at beacon scale in @sec-beacon).

#model(ids: "ST-M84", status: [extends ST-M83], title: "coarsened observation")[
  If every bit passes independently through a known binary symmetric channel with flip probability $kappa in [0, 1\/2)$, the observed bits are IID Bernoulli$(q_kappa)$ with $q_kappa - 1\/2 = (1 - 2 kappa)(q - 1\/2)$, so ST-T272 to ST-T276 apply to $q_kappa$: the frontier and the converse in $q$ both scale by $1\/(1 - 2 kappa)$, and for $kappa > 0$ even $q in {0, 1}$ maps to an interior $q_kappa$, so the interior constant replaces the boundary one. The rate contraction $KL(q_kappa || 1\/2) <= KL(q || 1\/2)$ is ST-M83; at $kappa = 1\/2$ nothing is detectable (ST-T01).
]

// ------------------------------------------------------------------ 4
= Weights over one world: the cap and its saturation <sec-cap>

Now let both hypotheses share the kernel $K$ and differ only in the law of the latent world, as in the remark of @sec-boundary.

#standard(ids: "ST-T277", status: [data-processing inequality @kullbackleibler1951 @coverthomas2006 @polyanskiywu2024; applied to world-level weights], title: "one-draw cap")[
  For every transcript design (any length, stopping rule or label-independent adaptive policy),
  $ KL(a K || b K) <= KL(a || b), $ <eq-cap>
  and for $N$ independent world draws with any common kernel from $(M_1, dots, M_N)$ to $Y$ the transcript KL is at most $N KL(a || b)$, with equality to the sum of per-unit KLs when units and their transcripts are independent. The bound is finite only when $a << b$.
]
#proof[Decompose $KL(a ⊗ K || b ⊗ K)$ by the chain rule in two orders. Conditioning on $M$ first gives $KL(a || b) + EE_a KL(K(dot|M) || K(dot|M)) = KL(a || b)$. Conditioning on $Y$ first gives $KL(a K || b K) + EE_(a K) KL(a(dot|Y) || b(dot|Y)) >= KL(a K || b K)$. Both hold in $[0, +infinity]$.]

The two sides are _not_ infinite together. With $a = (1\/2, 1\/2)$, $b = (1, 0)$ and identical components, $KL(a || b) = +infinity$ while every transcript KL is 0; only "transcript KL infinite implies $KL(a || b)$ infinite" holds. The cap controls an expectation. The pointwise companion is the identity $P_a (y) \/ P_b (y) = sum_m w_m (y) a_m \/ b_m$ with $w_m (y) = P_b (M = m | y)$ (ST-T225), which gives
$ min_m a_m / b_m <= (P_a (y)) / (P_b (y)) <= max_m a_m / b_m quad "for every transcript" y $ <eq-pointwise>
when $b_m > 0$ wherever $a_m > 0$ (ST-T226), with the extremes attained by mutually singular components (ST-T227). Since $KL(a || b) = EE_a ln(a_M \/ b_M) <= ln max_m (a_m \/ b_m)$, the cap @eq-cap replaces the maximum in the logarithm of @eq-pointwise by an $a$-average. Expected evidence about world-level weights scales with the number of independent world draws, not with transcript length.

#standard(ids: "ST-T278", status: [KL chain rule; the zero-gap condition specializes the Kullback-Leibler sufficiency condition @kullbackleibler1951; only the finite-$M$ ratio form and the counterexamples below are offered], title: "saturation identity")[
  If $KL(a || b) < infinity$ then
  $ KL(a || b) - KL(a K || b K) = EE_(Y tilde a K) [KL(a(dot | Y) || b(dot | Y))]. $ <eq-gap>
  For finite $M$ with component densities $K_m (y)$ (with respect to a common dominating measure), ratios $r_m = a_m \/ b_m$ and $S_b (y) = {m : b_m K_m (y) > 0}$, the gap is zero if and only if, for $a K$-almost every $y$, $r$ is constant on $S_b (y)$. If $M$ is almost surely a function of $Y$ under $b ⊗ K$, the gap is zero; the converse holds when the ratios $r_m$ are pairwise distinct on the support of $b$, and fails in general.
]

The failure of the converse is not hypothetical. With $a = (1\/4, 1\/4, 1\/2)$, $b = (1\/8, 1\/8, 3\/4)$, components 1 and 2 sharing the law $(1\/2, 1\/2, 0)$ on a ternary alphabet and component 3 the law $(0, 0, 1)$, the transcript KL equals $KL(a || b) = 0.143841$ at $T = 1, 3, 6$: the gap is zero although $M$ is not a function of $Y$, because the two components that $Y$ cannot separate have the same ratio $r_1 = r_2 = 2$. A second, deterministic counterexample is in the receipt (ST-F55).

#theorem(ids: "ST-T279", status: [$(R - 1)$ factor and mismatch term new; MAP-error Chernoff exponent classical @chernoff1952 @leangjohnson1997], title: "gap bound and decay")[
  Let $M$ be finite with $a << b$, $S = "supp"(a)$, $Z = "supp"(b) without S$, $R = max_(m, m' in S) r_m \/ r_(m')$, and let $P_a ("err") = EE_(a K) [1 - max_m a(m | Y)]$ be the Bayes error of the MAP rule under prior $a$. For any $s_(m m') in (0, 1]$ chosen separately for each pair,
  $ "gap" <= (R - 1) P_a ("err") + sum_(m in S, m' in Z) a_m / s_(m m') (b_(m') / b_m)^(s_(m m')) rho_(s_(m m')) (K_m, K_(m')), quad rho_s (P, Q) = integral p^(1-s) q^s dif mu. $
  For conditionally IID transcripts of length $T$, $limsup_(T -> infinity) 1/T ln "gap"_T <= - min C_(m m')$ over the relevant pairs (pairs within $S$ when $R > 1$, and pairs in $S times Z$), where $C_(m m')$ is the Chernoff information between the one-step laws of components $m$ and $m'$. The gap therefore decays at least as fast as $exp(-T min C_(m m') + o(T))$ when every relevant pair has distinct laws; the exponent is not shown to be tight.
]
#sketch[Fix $y$ and write $alpha, beta$ for the two posteriors. Then $KL(alpha || beta) = {EE_alpha ln r + ln EE_alpha [1\/r]} + ln(1 + p_b^Z \/ p_b^S)$. With $epsilon = 1 - max_m alpha_m$, the braced term is convex in the ratio at the MAP component and is at most $epsilon (R - 1)$; integrating gives $(R - 1) P_a ("err")$. The mismatch term follows from $ln(1 + x) <= x^s \/ s$, and the decay from $min(u, v) <= u^(1-s) v^s$.]

Without distinct component laws the gap need not vanish. In the non-identifying example $theta = (1\/4, 1\/4, 3\/4)$, $a = (1\/2, 1\/3, 1\/6)$, $b = (1\/6, 1\/3, 1\/2)$, the transcript KL never exceeds the merged-class value 0.242586, while $KL(a || b) = 0.366204$ (@fig-evidence b, orange). For a continuous latent, Jeffreys versus uniform priors on a coin's bias have cap $ln(4\/pi) = 0.2416$, and the exact transcript KL reaches 0.2035 at $n = 256$.

#standard(ids: "ST-T280", status: [chain rule plus data processing; standard], title: "different kernels")[
  If the hypotheses use kernels $K^a$ and $K^b$, then
  $ KL(a K^a || b K^b) <= KL(a || b) + integral KL(K^a (dot|m) || K^b (dot|m)) a(dif m). $
  For conditionally IID transcripts the second term is linear in $T$; only the first is world-level. No matching lower bound is claimed.
]
In the example $theta^a = (1\/3, 2\/3)$, $theta^b = (2\/5, 3\/5)$ with the binary weights of @fig-evidence b, the transcript KL passes the world-level cap 0.5493 by $T = 64$ and reaches 2.9727 at $T = 256$, within $10^(-6)$ of the bound. This is the link between the regimes: linear growth requires a per-world difference, and its excess over the cap is at most the within-world divergence.

#finite(ids: "ST-F55", status: [bounded exact-law audit], title: "persistent audit")[
  Exact Fraction laws over sufficient count vectors, with 60-digit logarithms, for binary, ternary, support-mismatch, ternary-emission and non-identifying latents up to $T = 64$: monotonicity in $T$, $KL_T <= KL(a || b)$, the identity @eq-gap against an independent computation to $10^(-30)$, the bound of ST-T279 and its Bhattacharyya relaxation, additivity over two independent world draws, and the counterexamples above.
]

// ------------------------------------------------------------------ 5
= Anytime validity: e-processes and the Wald floor <sec-anytime>

The bounds above concern expectations at a fixed $n$. Real analyses peek. A nonnegative supermartingale $E_n$ with $E_0 = 1$ under every member of the null is a _test supermartingale_ (a special case of an e-process). It satisfies Ville's inequality $PP(sup_n E_n >= 1\/alpha) <= alpha$ @ville1939, so $1\/sup_n E_n$ is a $p$-value valid under any stopping rule @shafer2011 @shafer2021 @ramdas2023 @grunwald2024. The KT Bayes factor of @sec-sandwich is one; the Bernoulli likelihood-ratio martingale of Wald's sequential test @wald1945 is another, valid also under a one-sided composite null (ST-T08, standard).

For Bell tests the natural null is relaxed and conditional. Let $W_i$ be the CHSH win indicator of trial $i$ @chsh1969 and $cal(F)_(i-1)$ everything that happened before it. A resource level $omega$ of a classical simulator (a communication budget, a setting-dependence floor) yields a number $f(omega)$ and the null
$ H(f): quad PP(W_i = 1 | cal(F)_(i-1)) <= f quad "almost surely, for every" i. $ <eq-hf>

#standard(ids: "ST-T281", status: [conditional-null extension of ST-T08; Bell test supermartingales are standard @gill2003 @gill2014 @zgk2011; beta-mixture closed forms are standard @robbins1970 @shafer2011 @howard2021 @waudbysmith2024; only the closed form below is new], title: "betting e-processes")[
  Fix $f in (0, 1)$ and bets $u in [f, 1]$ with factors $e(u, 1) = u\/f$ and $e(u, 0) = (1-u)\/(1-f)$. Under $H(f)$, $EE[e(u, W_i) | cal(F)_(i-1)] = 1 + (p_i - f)(u - f)\/(f (1 - f)) <= 1$, so for any data-independent mixing law $nu$ on $[f, 1]$, and for any predictable bets, $E_n = integral product_(i <= n) e(u, W_i) nu(dif u)$ is a test supermartingale, and $C_alpha = {omega : sup_n E_n^((omega)) < 1\/alpha}$ covers the true level $omega^*$ with probability at least $1 - alpha$ whenever the data satisfy $H(f(omega^*))$. For the uniform mixture, with $k$ wins, $m$ losses, $n = k + m$ and $f = A\/B$ in lowest terms,
  $ E_n = (k! m! sum_(j=0)^k binom(n+1, j) A^j (B - A)^(n+1-j)) / ((n+1)! A^k (B - A)^(m+1)), $
  an exact rational.
]

#standard(ids: "ST-T285", status: [Kelly @kelly1956 and Wald @wald1945 @hoeffding1960 bounds; standard], title: "growth ceiling and sample-size floor")[
  (a) Let $Q = "Bern"(f)^n$, which belongs to $H(f)$, and $P = "Bern"(p)^n$. Every nonnegative $E$ with $EE_Q [E] <= 1$ has $EE_P [ln E] <= n KL(p || f)$.
  (b) Let $E_n$ be an e-process on the win filtration that is a supermartingale under $"Bern"(f)^infinity$, and $T_alpha = inf{n : E_n >= 1\/alpha}$. If under $P = "Bern"(p)^infinity$ we have $P(T_alpha < infinity) = 1$ and $EE_P [T_alpha] < infinity$, then $EE_P [T_alpha] >= ln(1\/alpha) \/ KL(p || f)$.
]
#proof[(a) $EE_P [ln E] - KL(P || Q) = EE_P [ln(E dif Q \/ dif P)] <= ln EE_Q [E] <= 0$ by Jensen. (b) On ${T_alpha = n}$, $dif P\/dif Q = "LR"_n$; optional stopping and Fatou give $EE_P [E_(T_alpha) \/ "LR"_(T_alpha)] <= 1$, Jensen gives $EE_P [ln E_(T_alpha)] <= EE_P [ln "LR"_(T_alpha)]$, Wald's identity gives $EE_P [ln "LR"_(T_alpha)] = EE_P [T_alpha] KL(p || f)$, and $ln E_(T_alpha) >= ln(1\/alpha)$.]

The same structure appears in @sec-sandwich: by ST-T272, $ln BF_n$ is the hindsight-optimal log growth $n KL(hat(q) || 1\/2)$ minus a regret between $1\/2 ln(pi n\/2)$ and $1\/2 ln n + ln 2$, the price of mixing over unknown bets; the repository records the same $O(log n)$ penalty for the uniform betting mixture below. For the Bell game the ceiling rate is a statistical strength.

#theorem(ids: "ST-T284", status: [the $v = 1$ value reproduces van Dam, Gill and Grünwald @vandam2005; only the $v$-family and the data-processing proof are new], title: "uniform-setting statistical strength")[
  For $v in [0, 1]$ let $P_v$ be the isotropic CHSH law with uniform settings and $P(W = 1 | x y) = w_v = (1 + v\/sqrt(2))\/2$. Over all local laws $L$ with uniform settings independent of the hidden variable,
  $ min_L KL(P_v || L) = KL(w_v || 3\/4) "if" v >= 1\/sqrt(2), quad "and" 0 "otherwise". $
  At $v = 1$ this is $KL(cos^2(pi\/8) || 3\/4) = 0.032074586$ nats $= 0.046273847$ bits.
]
#sketch[The win indicator is a function of the record, so data processing gives $KL(P_v || L) >= KL(w_v || L("win"))$, and every such $L$ wins with probability at most $3\/4$ (ST-T283 at $ell = 1\/4$); $KL(w || u)$ is nonincreasing in $u <= w$. The uniform mixture $L^*$ of the eight one-loss deterministic strategies attains the bound exactly. For $v <= 1\/sqrt(2)$, $P_v$ is a mixture of $L^*$ and the uniform box.]

Consequently, at $f = 3\/4$ and uniform settings, betting on the win indicator loses nothing in growth rate against the isotropic law relative to full-data e-processes: replacing $Q$ in ST-T285 by the IID law of $L^*$ and using ST-T284 gives the same floor for e-processes on settings and outcomes when the truth is IID $P_v$. The repository proves this extension only at $f = 3\/4$, not at $f = xi$ (`docs/bell-escape-route-frontiers.md`, remark after ST-T285); compare the asymptotic optimality results of @zgk2011. Wald's floor then converts strength into trials: at $alpha = 0.05$ and $f = xi$ (the Delft local bound defined in @sec-delft), a power-one e-process on the win indicator needs at least $ln 20 \/ KL(cos^2(pi\/8) || xi) = 93.5$ trials in expectation at the Tsirelson rate, and at least 428.4 if the true IID win rate were $0.8$ (@fig-frontiers c).

// ------------------------------------------------------------------ 6
= Real data <sec-data>

Both data sets are reduced to small committed summaries under `data/real/`, each with its source, license and hashes; `verify --online` downloads the sources again and checks the reduction.

== The NIST beacon: no rejection, and what it excludes <sec-beacon>

The data are the `localRandomValue` fields of NIST Randomness Beacon 2.0, chain 2, pulses 1987000 to 1987255 (17 October 2026), with pulse 1987256 used only to verify the last precommitment @nist8213. The check confirms all 256 SHA-512 precommitment links; this is internal consistency, not authenticity, since NIST's signatures are not verified. The 131072 bits contain $k = 65461$ ones, so $|hat(q) - 1\/2| = 5.7 times 10^(-4)$.

#figure(
  placement: auto,
  image("figures/fig_beacon.svg", width: 100%),
  caption: [The NIST beacon bits. *(a)* The running KT log Bayes factor (blue) stays between $-6.1$ and $1.5$ and never approaches the Ville threshold $ln 100$ (ST-F52). It ends at $-6.03$, about 0.6 standard deviations of the $chi_1^2 \/ 2$ fluctuation below the exact fair-bit expectation $-5.62$; dashed: the fair-bit asymptote $-1\/2 ln n + 0.274$ (ST-T274). *(b)* The regret residual $ln BF_n - n KL(hat(q)_n || 1\/2) + 1\/2 ln n = 1\/2 ln n - rho_n$ on every prefix, against the band $[-ln 2, -1\/2 ln(pi\/2))$ of ST-T272 (shaded). The band holds for every binary sequence, so this panel checks the computation, not the source. *(c)* Exact power at $n = 131072$, $alpha = 0.01$, as a function of the simulator bias. Vertical lines: the Le Cam converse (ST-T276; no level-0.01 test reaches power 0.95 to its left, shaded), the 0.95 crossings of the optimal one-sided Neyman-Pearson test and of the fixed-$n$ KT test (ST-F54), and the closed-form sufficient frontier of ST-T275. The dashed curve is the KT test seen through a binary symmetric channel with $kappa = 1\/10$ (ST-M84).],
) <fig-beacon>

#finite(ids: "ST-F52, ST-F53", status: [bounded; not a randomness certification], title: "beacon evidence")[
  The running $ln BF_n$ stays between $-6.1$ and $1.5$ and never reaches $ln 100$ ($alpha = 0.01$), so the composite test does not reject fair bits under any stopping rule. What the data show is this non-rejection and $n KL(hat(q) || 1\/2) = 0.085831$. The final value $ln BF_n = -6.031714$ lies in the pathwise sandwich $[-6.4991, -6.0317]$, within $2 times 10^(-6)$ of its upper end, because $k$ and $n - k$ are both large, so the lower regret bound of ST-T272 is nearly tight (gap about $1\/(24 k) + 1\/(24(n - k)) + 1\/(12 n)$). The sandwich holds for every sequence, so this is a consistency check of the computation, not evidence about the source. The exact fair expectation is $-5.617542$ (ST-F53); the difference $-0.41$ is about 0.6 standard deviations of the $chi_1^2 \/ 2$ fluctuation, whose standard deviation is about 0.71.
]

#finite(ids: "ST-F54", status: [bounded; exact 60-digit powers on the grid $q = (65536 + i)\/n$], title: "beacon power frontier")[
  At $n = 131072$, $alpha = 1\/100$, $beta = 1\/20$:
  #align(center)[
    #set text(size: 9pt)
    #table(
      columns: (auto, auto),
      align: (left, left),
      inset: (x: 5pt, y: 3pt),
      table.hline(stroke: 0.5pt),
      [*bias* $|q - 1\/2|$], [*meaning*],
      table.hline(stroke: 0.3pt),
      [$< 0.002011$], [no fixed-$n$ level-0.01 test has power $>= 0.95$ (ST-T276)],
      [0.005478 to 0.005486], [the exact randomized one-sided Neyman-Pearson test crosses power 0.95],
      [0.008667 to 0.008675], [the exact KT test crosses 0.95 (it rejects iff $|k - n\/2| >= 839$)],
      [$>= 0.009914$], [closed form $d_n + t_n = 0.006534 + 0.003381$ of ST-T275 guarantees 0.95],
      table.hline(stroke: 0.5pt),
    )
  ]
]

So the "did not reject" of ST-F52 has explicit content. Any IID biased source with $|q - 1\/2| >= 0.0087$ would have been caught by the fixed-$n$ KT test with probability at least 0.95, and the sequential test rejects at least as often. Seen through a known binary symmetric channel with $kappa = 1\/10$ the closed-form frontier and the converse move to 0.012393 and 0.002514, and with $kappa = 2\/5$ to 0.049570 and 0.010055 (ST-M84). Sources with $|q - 1\/2| < 0.002011$ are neither shown to exist nor shown not to exist, and nothing here bears on simulators that reproduce the fair law exactly.

== Delft 2015: a violation at fixed $n$, weak evidence anytime <sec-delft>

The Delft 2015 experiment @hensen2015 is a loophole-free Bell test with electron spins separated by 1.3 km. Its released archive @hensen2015data holds 4746 heralding attempts; a standard-library port of the authors' valid-trial filter keeps 245 trials, committed with their timestamps, random inputs and outcomes, with the trial digest pinned in code.

#finite(ids: "ST-F50, ST-F51", status: [bounded; reproduces the published statistic], title: "Delft recomputation and disk placement")[
  The 245 trials contain $k = 196$ CHSH wins. The four correlations are $(E_(00), E_(01), E_(10), E_(11)) = (0.736, 0.595, 0.484, -0.608)$, so $S = 2.422 plus.minus 0.204$ (published: $2.42 plus.minus 0.20$). With the paper's local win bound $xi = 3\/4 + 3(tau + tau^2)$ for setting predictability $tau = 1.08 times 10^(-5)$, $P("Bin"(245, xi) >= 196) = 0.0392$ (published: 0.039). On the canonical CHSH disk, where the visibility-phase family has the exact predictive metric $TV = ||z - z'||_infinity \/ (2 sqrt(2))$ (ST-T12), the equal-weight least-squares point is $z = (0.856, -0.094)$, and its predictive TV to the local chord $x = 1\/sqrt(2)$ is $(S - 2)\/8 = 0.053$.
]

#figure(
  placement: auto,
  image("figures/fig_chsh_disk.svg", width: 100%),
  caption: [The canonical CHSH disk. *(a)* The visibility-phase family $z = (v cos phi, v sin phi)$ in the unit disk; the CHSH value of a point is $S = 2 sqrt(2) x$, so the local bound $S <= 2$ is the chord $x = 1\/sqrt(2)$ and Tsirelson's bound @tsirelson1980 is the point $(1, 0)$. *(b)* Zoom. The Delft 2015 point (ST-F51) with $1 sigma$ and $2 sigma$ regions from the same per-setting binomial error model that gives $S plus.minus 0.204$ (a visualization, not a claim). The green point is the 5-bit grid law $(3\/32, 13\/32, 13\/32, 3\/32)$ with $|S| = 5\/2$: a stationary renderer of precision $D = 32$ that coincides exactly with the Werner law at $v = 5 sqrt(2) \/ 8$. Specialized to CHSH, where every setting cosine has modulus $1\/sqrt(2)$, ST-T287 says that for $D$ divisible by 4 with $D (v_max - v_min) >= 4 sqrt(2)$ no CHSH data set of any size separates the grid laws $H_D$ from the Werner family with unknown visibility in $[v_min, v_max]$ (Corollary 1 of `docs/finite-precision-renderer-identifiability.md`). The fitted point is a least-squares summary, not a maximum-likelihood state, and local models need not lie in the family; only $x = S\/(2 sqrt(2))$ is compared with the chord.],
) <fig-disk>

The fixed-$n$ statement needs the sample size to have been fixed independently of the data; the published 0.039 is itself martingale-based @elkousswehner2016 and is valid against memory-ful local models at fixed $n$. Whether $n = 245$ was fixed in advance is not verified here. To ask what the data say without that assumption, and about simulators that cheat with a leak rather than none, we need the resource frontiers $f(omega)$ of @eq-hf.

#theorem(ids: "ST-T282, ST-T283", status: [frontier (b) reproduces Pironio @pironio2003; (d) is the Pütz et al. bound @putz2014; (a) possibly known; new: exact dual certificates and attaining models], title: "escape-route frontiers")[
  Parts (a) to (c) assume uniform settings independent of the shared randomness and of the past; in (d) the setting law may depend on the hidden variable $lambda$.
  (a) If Alice may send a message whose silent symbol is free and informative, at expected non-silent rate $c$, then $PP("win") <= 3\/4 + c\/2$ on $[0, 1\/2]$ and $<= 1$ beyond, so $S <= 2 + 4c$;
  (b) if the decision to communicate cannot depend on Alice's setting, $PP("win") <= 3\/4 + c\/4$, so $S <= 2 + 2c$;
  (c) one always-sent bit reproduces every behavior whose Alice marginal is free of Bob's setting;
  (d) if outputs are local but the setting law may depend on $lambda$ with $p(x, y | lambda) >= ell$, then $PP("win") <= 1 - ell$, attained with uniform observed settings, so $S <= 4 - 8 ell$ under uniform observed settings.
  All bounds are attained.
]
The detection-efficiency threshold $eta^* = 2\/(1 + sqrt(2))$ for local reproduction of the maximal-entanglement law is certified exactly in $bb(Q)(sqrt(2))$ (ST-M85, a model result for one fixed behavior; Garg and Mermin @gargmermin1987, Larsson @larsson1998); it is not tested on Delft, which is event-ready. Related frameworks include @tonerbacon2003 for communication and @hall2010 for relaxed measurement independence.

#figure(
  placement: auto,
  image("figures/fig_frontiers.svg", width: 100%),
  caption: [Frontiers and floors. *(a, b)* Maximum CHSH win probability of a classical simulator with a signaling budget $c$ (ST-T282: silence free, or with a setting-independent send flag) or a setting-dependence floor $ell$ (ST-T283). Horizontal lines: the local bound $3\/4$, the Tsirelson rate $cos^2(pi\/8)$, and the Delft empirical win rate $196\/245$ with one binomial standard error. Every frontier has $f(omega) >= 3\/4$, which is what makes the Delft check below uniform over resource levels. *(c)* Wald's floor (ST-T285(b), for power-one e-processes with $EE[T_alpha] < infinity$) on the expected number of trials for any e-process on the win indicator to reach 20 against $xi$, as a function of visibility. It diverges where $w_v = xi$, at $v = sqrt(2)(2 xi - 1) approx 0.7072$, just above the local point $1\/sqrt(2)$ (dotted). At the Delft rate the floor is 428.4 trials, against a sample of 245: a heuristic comparison of an expectation with one run, not a pathwise impossibility.],
) <fig-frontiers>

#finite(ids: "ST-F56", breakable: true, status: [negative result; covers constant-bet mixtures on the win indicator only], title: "Delft anytime check")[
  On the 245 trials in timestamp order, with exact rational e-values:
  #align(center)[
    #table(
      columns: (auto, auto, auto),
      inset: (x: 6pt, y: 3pt),
      table.hline(stroke: 0.5pt),
      [*quantity*], [$f = 3\/4$], [$f = xi$],
      table.hline(stroke: 0.3pt),
      [uniform-mixture $E_245$], [1.369782], [1.366934],
      [running $sup_n E_n$ (at $n = 6$, six straight wins)], [2.782089], [2.781599],
      [anytime-valid $p = 1 \/ sup_n E_n$], [0.359], [0.360],
      [fixed bet $u = 17\/20$: $E_245$ / running sup], [0.607 / 2.119], [0.606 / 2.119],
      [hindsight best constant bet at $n = 245$], [5.5595], [5.5478],
      table.hline(stroke: 0.5pt),
    )
  ]
  For any mixing law $nu$ on $[f, 1]$, $E_n^nu (f) <= C_n (f) := sup_(u in [f, 1]) product_i e(u, W_i)$, which equals $exp(n KL(hat(p)_n || f))$ if $hat(p)_n > f$ and 1 otherwise, and is nonincreasing in $f$. On the Delft data $max_(n <= 245) C_n (3\/4) = 7.7797$, at $n = 241$ with $k = 194$ (exact comparison with 20). Every escape-route frontier has $f(omega) >= 3\/4$, so for every constant-bet mixture fixed independently of the data and every resource level, $sup_n E_n < 7.78$. At $alpha = 0.05$ the confidence sets built from this class are the full ranges $c in [0, 1\/2]$ for (a), $c in [0, 1]$ for (b) and $ell in [0, 1\/4]$ for (d), and they stay full for every $alpha < 1\/7.7797 = 0.1285$.
]

#figure(
  placement: auto,
  image("figures/fig_delft_eprocess.svg", width: 100%),
  caption: [Anytime-valid evidence in the Delft 2015 trials (ST-F56). The shaded region is the realized ceiling $C_n (3\/4)$, which bounds every constant-bet mixture at every resource level $f >= 3\/4$; its maximum, 7.78 at $n = 241$, stays below the Ville threshold 20. The default uniform mixture (blue) peaks at 2.78 after six straight wins (anytime $p approx 0.36$). The predictable KT plug-in bet (green) is an exploration of adaptive bets, not a bound over them. The orange square is $1\/p = 25.5$ for the fixed-$n$ binomial tail. It equals the all-or-nothing e-value $bb(1){K >= 196} \/ P_xi (K >= 196)$ only if both the threshold and $n$ had been fixed in advance. The threshold was not, and whether $n$ was is not verified here.],
) <fig-delft>

The uniform mixture is a default, data-independent choice made after the data were public; it was not preregistered, and its $p approx 0.36$ is illustrative. The negative conclusion does not depend on it, because the ceiling holds uniformly over all constant-bet mixtures. Two predictable plug-in bets on the win sequence (Laplace and KT rules) reach running suprema 1.65 and 1.90 in the receipt; this is an exploration, not a proof for adaptive bets. Not covered at all are e-processes valid only for the narrower escape-route classes, full-data test factors such as those of @zgk2013, and predictable adaptive bets in general; ST-T285 still bounds their expected log growth. Earlier reanalyses of these data and related betting framings are @elkousswehner2016, @gill2022 and @nomura2026.

One reading, which is heuristic and not a theorem, is that Delft 2015 is evidence-limited rather than loophole-limited. The fixed-$n$ $p = 0.039$ requires $n$ to have been fixed independently of the data; the anytime-valid statement requires no such assumption and delivers far less. An earlier draft in the repository expected nontrivial anytime-valid lower bounds on the signaling budget $c$ and the dependence floor $ell$; at $alpha = 0.05$ that expectation is false for constant-bet mixtures, and the negative result is what is recorded. As context only, with no inferential claim, the setting counts are 53, 79, 62 and 51 (a fixed-$n$ chi-square of 7.98 on 3 degrees of freedom against uniform settings); the independence of the random-number generators is assumed through $tau$, not tested.

// ------------------------------------------------------------------ 7
= Discussion <sec-discussion>

== What the two regimes say about the simulation question

The dichotomy of Sections 3 and 4 separates two questions that are often merged. Whether the law of _our_ world deviates from a declared base law is a per-world question; if it does, evidence can grow linearly with data at a rate set by the deviation (ST-T272 to ST-T276). How often a hypothetical ensemble of simulators would produce worlds like ours is a question about weights over worlds; with one persistent world and a shared per-world law, no amount of observation of that world yields more than $KL(a || b)$ nats in expectation, or more than $ln max_m a_m \/ b_m$ on any transcript (@eq-cap, @eq-pointwise). Learning _which_ world is active is not limited by the cap; learning how often such worlds occur is. This is the evidential counterpart of the identification problems treated in the repository's companion paper on anthropic Bayes @fix2026anthropic. The interpretation is ours; the theorems say only what they state.

== Where per-world signals come from

Restricted simulators produce per-world deviations through resource limits, and the repository prices several of them on the Bell disk (@fig-renderers, @tab-claims). They feed the per-world regime of @sec-sandwich: once a resource limit fixes the per-world law, @sec-sandwich and @sec-anytime say how much evidence it can leave. A companion manuscript @fix2026pricing treats these lanes in detail; here each gets one or two sentences.

#figure(
  placement: auto,
  image("figures/fig_renderers.svg", width: 100%),
  caption: [Resource limits that force a per-world signal. *(a)* Correlator pairs $(zeta_1, zeta_2)$ available to a stationary renderer of precision $D = 16$ at setting angles $0$ and $pi\/4$, against the Werner segment $v (1, 1\/sqrt(2))$, $v in [1\/2, 1]$. The irrational slope keeps every grid point off the segment; the inset shows the closest one at $ell_infinity$ distance $g_16$. *(b)* $D^2 g_D$ computed with the repository's 80-digit routine `grid_segment_separation` at sampled $D$ divisible by 4 (markers only; no interpolation is implied): it stays above the lower bound $1\/(3 + 2 sqrt(2))$ of ST-T288 and, on this range, below 3, consistent with the $Theta(1\/D^2)$ order (a bounded computation, not a proof). *(c)* Excess polar area $A_w - pi^3$ of the CHSH (two-direction), regular three-direction and regular four-direction schedules; the polar bodies themselves differ too little to be told apart at plotting scale. A renderer that is $epsilon$-accurate in one-trial TV needs at least $pi\/(A_w epsilon^2)$ states (ST-T290), so a smaller polar area forces more memory; $A_w > pi^3$ for every finite schedule (ST-T292, Lutwak's dual mixed-volume inequality @lutwak1975), and isotropic schedules approach $pi^3$.],
) <fig-renderers>

- *Precision.* With unrestricted private dithering, finite precision is untestable (ST-T286). Without it, commensurable-cosine schedules, canonical CHSH included, still cannot identify a stationary precision $D$ under unknown visibility once $4 | D$ and the visibility range is wide enough (ST-T287; for CHSH with $v in [9\/10, 1]$ the value $D = 4$ fails, a recorded negative result), while settings at angles $0$ and $pi\/4$ separate the grid laws from the Werner family at order $1\/D^2$ with exactly known cosines (ST-T288; a cosine uncertainty of order $1\/D^2$ voids it, and the Pell attainment is classical continued-fraction theory), and with known visibility a $D$-adapted angle needs $Theta(D ln(1\/epsilon))$ trials (ST-T289).
- *Memory.* For canonical CHSH the minimum number of renderer states is $pi\/(32 epsilon^2)$ to leading order (ST-T291). The lower constant also follows from packing (ST-T05), the in-family covering limit is classical (Rogers @rogers1964; see @gruber2007), and the new part is the matching upper bound for arbitrary emissions. Among schedules with two or three direction classes, the regular three-direction class law uniquely minimizes the polar area, $18 sqrt(3)$ (ST-T294, with no priority asserted, since the discrete isoperimetric literature was not searched exhaustively); the optimum is a law on direction classes, which the $3 times 3$ trine product schedule realizes and no $2 times 2$ product schedule does. It is not the global optimum: the regular four-direction schedule has polar area $384 sqrt(2) - 512 approx 31.058$ and a strictly larger certified lower constant (ST-T295).
- *Noise.* A simulator that contracts visibility by a known factor $mu$ has exact one-trial Le Cam deficiency @lecam1964 $delta = C (1 - mu) \/ (2 (2 - C mu))$ relative to the physical experiment when all correlation magnitudes equal $C$ and the post-processing is central (ST-T306; a deficiency between Bernoulli dichotomies in Torgersen's sense @torgersen1991, and only the closed form is new). It bounds every one-trial decision-risk gap by $2 delta ||L||$ for bounded losses $L$ (ST-T308, standard). For canonical CHSH at $mu = 1\/2$, $delta = 0.10737$. The optimal post-processing is central, not Bell-local.

== What would count as evidence

Evidence must favor a declared restricted simulator over serious physical, measurement, selection and intervention alternatives. A useful proposal declares in advance the null and alternative laws, the nuisance parameters, the measurement and selection channels, the query protocol, the inferential rule (likelihood, e-process or confidence sequence), its calibration, power and stopping behavior, how ordinary-physics alternatives are excluded, and which broader simulator classes remain untouched. The beacon and Delft checks follow this template for very small simulator classes, which is exactly why their conclusions are narrow.

== Limitations and nonclaims

- Nothing here is evidence for or against simulation. A simulator that reproduces the base law is invisible (ST-T01); quantization, randomness and Bell violation occur in ordinary physics.
- ST-T274 is pointwise in $q$, not uniform near $q in {0, 1}$; ST-O02 is open. The sandwich concerns the KT (Jeffreys) composite alternative only, and IID bits under each hypothesis; dependent, adaptive or adversarial sources are not covered.
- ST-T277 bounds an expected log Bayes factor about world-level weights. It does not bound a single transcript beyond @eq-pointwise, does not limit learning which world is active, and is vacuous when $a$ is not absolutely continuous with respect to $b$. The ST-T279 exponent is an upper bound on the gap's exponent and is not shown tight.
- The beacon frontier concerns IID biased sources and one composite test. It is not a randomness certification, and NIST's signatures are not checked. That the beacon's log Bayes factor lies inside the pathwise sandwich is true of every sequence and is not a finding about the beacon.
- The Delft ceiling covers mixtures of constant bets on the win indicator against the relaxed null @eq-hf, at budgets that hold per trial conditionally on the past. It does not cover full-data test factors, e-processes valid only for the narrower model classes, adaptive bets, or budgets that hold only on average over a run. It assumes the paper's $tau$ model and RNG independence. Whether $n = 245$ was fixed in advance is not verified.
- The renderer results concern one-trial predictive TV on a declared two-parameter coplanar family; they say nothing about whether a parent substrate stores classical bits.

== Open problems

ST-O02 (second-order KT remainder); ST-O03 (Shannon-entropy communication frontier for CHSH); ST-O04 (open rates for finite-precision identification); ST-O05 (the renderer constant for arbitrary off-family emissions on non-tiling schedules); ST-O06 (a discrete dual-isoperimetric inequality for convex $n$-gons); ST-O07 (sharp two-view identified sets for $k >= 3$); ST-O08 (setting-preserving schedule-averaged deficiency with unequal magnitudes). Beyond the ledger: a joint frontier for signaling, setting dependence and RNG bias with $f(c, ell, tau)$ derived rather than bounded below by $3\/4$, and Azuma-type versions for budgets that hold only on average over a run.

// ------------------------------------------------------------------ appendix
#pagebreak(weak: true)
#counter(heading).update(0)
#set heading(numbering: "A.1")

= Reproducing this paper

Everything in this paper comes from a fresh clone of `origin/main` of #link("https://github.com/jadenfix/simulation-theory")[github.com/jadenfix/simulation-theory] at commit `aa61193`, which contains the seven new result lanes merged in PR \#72 (merge commit `0c77232`) and a follow-up that narrowed README claims and credited classical results (PR \#73). The full check is

#block(inset: (left: 1.2em))[`uv sync && uv run python -m simtheory verify`]

which byte-compiles the sources, validates every claim manifest (schema, unique IDs, evidence paths and anchors, `file.py:symbol` references), recomputes the Delft statistic from the committed trials against the digest and published values pinned in code, checks the beacon hash chain, compares the deterministic experiment suite with its receipt, runs the tests, and reports for every claim that each test file it cites has passed. It does not verify the proofs formally; those are in the derivation documents. At this commit the ledger holds 465 claims in 60 manifests (304 theorems, 93 model results, 60 finite checks, 8 open problems).

The figures are produced by `figures.py` in this paper's directory, which imports the repository's modules and committed data and asserts agreement with the receipts before drawing (for example the KT and Neyman-Pearson crossing brackets of ST-F54, recomputed in floating point, the pathwise sandwich on all 131072 beacon prefixes, the Delft ceiling 7.779688 at $n = 241$, the transcript KL values of ST-F55 and the three polar areas). It uses `matplotlib` for plotting and `numpy` for float recomputations that are asserted against the receipts.

A note on terminology: the evidence-scaling receipt labels the setting of @sec-sandwich "fresh draws"; the repository reserves "fresh redraw" for a latent redrawn on every trial (ST-M67), which the $N$-unit form of ST-T277 covers.

#figure(
  {
  set text(size: 8.4pt)
  set par(justify: false)
  show raw: set text(size: 7.4pt)
  table(
    columns: (auto, 1.15fr, 1fr),
    align: left,
    inset: (x: 4pt, y: 2.8pt),
    table.hline(stroke: 0.7pt),
    table.header([*Claims*], [*Derivation and manifest*], [*Code and receipt*]),
    table.hline(stroke: 0.4pt),
    [ST-T01, T02, T08], [`docs/formal-results.md`, `claims/claims-v1.json`], [`inference.py`, `sequential.py`],
    [ST-T225 to T228], [`docs/persistent-latent-prior-evidence-ceilings.md`], [`persistent_latent_priors.py`],
    [ST-F50 to F52, T271, M83], [`docs/real-data-checks.md`, `claims/real-data-claims.json`], [`real_data.py`, `data/real/`],
    [ST-T272 to T280, M84, F53 to F55, O02], [`docs/evidence-scaling-dichotomy.md`], [`evidence_scaling.py`, `receipts/evidence-scaling-dichotomy.txt`],
    [ST-T281 to T285, M85, F56, O03], [`docs/bell-escape-route-frontiers.md`], [`bell_escape_routes.py`, `receipts/bell-escape-route-frontiers.txt`],
    [ST-T286 to T289, F57, O04], [`docs/finite-precision-renderer-identifiability.md`], [`finite_precision_renderers.py`],
    [ST-T290 to T296, F58, O05, O06], [`docs/bell-disk-renderer-memory.md`], [`bell_disk_zonoid.py`],
    [ST-T297 to T305, M86 to M89, F59, O07], [`docs/two-view-orthogonal-fiber.md`], [`two_view_fiber.py`],
    [ST-T306 to T309, F60, O08], [`docs/le-cam-deficiency-bell-simulator.md`], [`le_cam_deficiency.py`],
    [ST-T12, T13], [`docs/canonical-chsh-disk-geometry.md`], [`quantum_phase_geometry.py`],
    table.hline(stroke: 0.7pt),
  )},
  caption: [Where each claim used here lives. Code paths are under `src/simtheory/`; every lane also has a test file under `tests/` that its claims cite.],
  kind: table,
) <tab-map>

#v(0.6em)
#set text(size: 9pt)
#bibliography("refs.bib", title: "References", style: "ieee")
