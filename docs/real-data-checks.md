# Real-data checks

This page connects two parts of the repository to public data. It addresses a
small piece of open problem 4 in [formal-results.md](formal-results.md#current-open-problems)
(sequential tests tied to concrete random-source architectures and real external
data). It does not test whether reality is simulated.

Both data sets are reduced to small committed summaries under `data/real/`.
Each summary records its source, license, and hashes, and
`python -m simtheory.real_data_fetch {delft,beacon}` downloads the source again,
reduces it, and compares the result with the committed file.

## 1. Delft 2015 Bell test

Source: B. Hensen et al., "Loophole-free Bell-inequality violation using
electron spins separated by 1.3 kilometres", Nature 526, 682-686 (2015),
doi:10.1038/nature15759. Data set: 4TU.ResearchData,
doi:10.4121/uuid:6e19e9b2-4a2d-40b5-8dd3-a660bf3c0a31, released under the 4TU
General Terms of Use (attribution required, non-commercial reuse).

The archive (`data.zip`, md5 `342f29f8288c46575818acd2acebd535`) holds 4746
heralding attempts. `simtheory.real_data.delft_valid_trials` is a
standard-library port of the authors' published valid-trial filter. It keeps
245 trials, which are committed with their timestamps, random inputs `a,b`, and
outcomes `x,y`.

Recomputed from those trials:

| quantity | recomputed | published |
| --- | --- | --- |
| valid trials n | 245 | 245 |
| CHSH-game wins k | 196 | |
| E(0,0), E(0,1), E(1,0), E(1,1) | 0.736, 0.595, 0.484, -0.608 | |
| S = E00 + E01 + E10 - E11 | 2.422 +- 0.204 | 2.42 +- 0.20 |
| P(Bin(n, xi) >= k), xi = 3/4 + 3(tau + tau^2), tau = 1.08e-5 | 0.0392 | 0.039 |

The p-value uses the paper's bound: any local model whose inputs are at most
`tau`-predictable wins each CHSH round with probability at most `xi`. The
bound `3/4` at `tau = 0` is checked by exhausting all 16 deterministic local
strategies.

The violation is modest. With 245 trials the standard error of S is about 0.2,
so a local model can reach S above 2 in a finite run by chance; the p-value,
not S alone, is the published test.

## 2. The Delft point on the canonical CHSH disk

The Delft settings (Alice 0, pi/2; Bob -3pi/4, +3pi/4; psi-minus heralding)
form the canonical CHSH schedule of
[canonical-chsh-disk-geometry.md](canonical-chsh-disk-geometry.md) with every
setting difference shifted by pi. The repository's singlet law
`E = -v cos(theta - phi)` then makes the measured correlations equal the
canonical correlations

```text
E00, E01, E10, E11 = r(-pi/4), r(pi/4), r(pi/4), r(3pi/4),   r(theta) = x cos(theta) + y sin(theta)
```

for a visibility-phase point `q = (x, y)` in the unit disk. The four unit
directions satisfy `sum s s^T = 2 I`, so the equal-weight least-squares point is

```text
x = (E00 + E01 + E10 - E11) / (2 sqrt 2) = S / (2 sqrt 2),
y = (-E00 + E01 + E10 + E11) / (2 sqrt 2).
```

For the Delft trials `q = (0.856, -0.094)`. The local bound `S <= 2` is the
chord `x <= 1/sqrt 2 = 0.707`, and Tsirelson's bound `S <= 2 sqrt 2` is the disk
edge `x <= 1`. By the exact identity `TV = ||q - q'||_inf / (2 sqrt 2)` (claim
ST-T12), the predictive total variation per trial between the fitted point and
the nearest chord point is `(S - 2) / 8 = 0.053`.

The disk is the visibility-phase quantum family. A local model need not be a
point of that family; the chord statement holds for any correlations because
`x = S / (2 sqrt 2)` by construction.

## 3. NIST Randomness Beacon bits

Source: NIST Randomness Beacon 2.0, chain 2, pulses 1987000 to 1987256
(2026-10-17 06:31 to 10:47 UTC), https://beacon.nist.gov/. Each pulse's
`localRandomValue` is 512 bits from NIST's hardware entropy sources,
conditioned by SHA-512. The committed file keeps 257 consecutive pulses, and
`verify_beacon_precommitments` checks that
`SHA-512(localRandomValue[i+1]) = precommitmentValue[i]` for all 256 links. It
does not check NIST's signatures. The first 256 values give 131072 bits, of
which 65461 are ones.

## 4. Composite Bayes factor for a biased simulator

Let the base hypothesis be fair IID bits. Let the restricted simulation
hypothesis be IID Bernoulli(q) bits with q unknown and prior Beta(1/2, 1/2).
The Bayes factor is the Krichevsky-Trofimov (KT) marginal over the fair law:

```text
BF_n = prod_t P_KT(x_t | x_<t) / (1/2),     P_KT(1 | k ones in t bits) = (k + 1/2) / (t + 1).
```

**Validity under the base law.** Under fair bits `BF_n` is a nonnegative
martingale with mean one, so by Ville's inequality
`P(sup_n BF_n >= 1/alpha) <= alpha`. If the simulation reproduces the fair law
exactly, then `P_sim = P_base` and every Bayes factor between them is 1
(ST-T01); `log BF_n` against a composite alternative drifts down only like
`-(1/2) ln n`.

**Detection rate (standard).** The KT regret bound
`log P_KT(x^n) >= max_q log q^n(x^n) - (1/2) ln n - ln 2` holds for every
sequence. It is classical: Krichevsky and Trofimov, IEEE Trans. Inf. Theory 27
(1981) 199-207; see also Willems, Shtarkov and Tjalkens, IEEE Trans. Inf.
Theory 41 (1995) 653-664. A self-contained proof is the upper half of ST-T272
([evidence-scaling-dichotomy](evidence-scaling-dichotomy.md#theorem-st-t272-pathwise-sandwich)).
ST-T271 is only its expectation and is not claimed as new. Taking expectations
under the true q,

```text
E_q[log BF_n] >= n KL(q || 1/2) - (1/2) ln n - ln 2.
```

So evidence grows linearly at the KL rate when the simulated source is biased.
The regret bound is checked on every count vector up to n = 12 and the
expectation bound exactly up to n = 16.

**Coarsened observation.** If the observer sees each bit through a binary
symmetric channel with flip probability f, the bias about 1/2 contracts by
exactly `1 - 2f`, the channel's Dobrushin coefficient (ST-M14), and the rate
becomes `KL(f + (1 - 2f) q || 1/2)`, which is smaller (ST-M83). The rate itself
is not multiplied by `1 - 2f`: near q = 1/2 it is about
`(1 - 2f)^2 KL(q || 1/2)`. The detection frontier widens by `1/(1 - 2f)`
(ST-M84). Lossy observation slows
detection; it cannot create it.

**Real-bit check.** On the 131072 beacon bits, `log BF_n` stays between -6.1
and 1.5 and never reaches the Ville threshold `ln 100` for alpha = 0.01. Its
final value, -6.03, is close to `-(1/2) ln 131072 = -5.9`.

## Scope

These are finite checks on fixed data. They reproduce one published Bell
statistic and show that one public random source behaves like fair bits under
one composite test. They are not evidence about simulation, and the beacon
check is not a randomness certification.
