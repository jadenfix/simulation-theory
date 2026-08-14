# Noisy relational consistency and predictive rate distortion

## Scope

The exact cat-state and stabilizer constructions show that information can live
entirely in relationships: every proper local record can be uninformative while
a completed distributed transcript is constrained by a parity law.

The natural next question is not whether those exact identities survive noise
unchanged. They do not. The useful question is:

> How does declared local noise attenuate relational evidence, predictive-state
> separation, and the memory required for consistent online continuation?

This note answers that question for independent binary readout flips. The model
is deliberately bounded and explicit. It does not claim that all physical noise
is independent, that a hypothetical simulator would use this architecture, or
that internal predictive bits equal parent-universe hardware bits.

---

## 1. Noisy phase-labeled cat block

For a block of \(\ell\ge2\) qubits, let

\[
|\mathrm{Cat}_z\rangle
=
\frac{|0^\ell\rangle+(-1)^z|1^\ell\rangle}{\sqrt2},
\qquad z\in\{0,1\}.
\]

Under ideal local \(X\)-basis measurements, the outcomes
\(x_i\in\{-1,+1\}\) are uniform subject to

\[
\prod_{i=1}^{\ell}x_i=(-1)^z.
\]

Now let every recorded outcome be independently multiplied by a noise sign
\(e_i\), where

\[
P(e_i=-1)=p,
\qquad
P(e_i=+1)=1-p,
\qquad
0\le p\le\frac12.
\]

The observed outcome is

\[
y_i=x_ie_i.
\]

### Parity attenuation

The observed global parity is

\[
\prod_i y_i
=
(-1)^z\prod_i e_i.
\]

Since the noise signs are independent,

\[
E\left[\prod_i e_i\right]
=
\prod_iE[e_i]
=(1-2p)^\ell.
\]

Define the surviving parity visibility

\[
\boxed{c_\ell(p)=(1-2p)^\ell.}
\]

If \(q_\ell(p)\) is the probability that an odd number of local flips occurs,
then

\[
1-2q_\ell(p)=c_\ell(p),
\]

hence

\[
\boxed{
q_\ell(p)
=
\frac{1-(1-2p)^\ell}{2}.
}
\]

The code checks this closed form against the explicit odd-binomial sum

\[
\sum_{j\text{ odd}}\binom\ell j p^j(1-p)^{\ell-j}.
\]

---

## 2. Exact complete-transcript law

Let

\[
\pi(y)=\prod_{i=1}^{\ell}y_i.
\]

Conditioned on the observed parity, all strings are equally likely. The
probability of the target parity is \(1-q_\ell\), and the probability of the
opposite parity is \(q_\ell\). Therefore

\[
P_z^{(p)}(y)
=
\begin{cases}
2^{-(\ell-1)}(1-q_\ell),&\pi(y)=(-1)^z,\\
2^{-(\ell-1)}q_\ell,&\pi(y)=-(-1)^z.
\end{cases}
\]

Using \(c_\ell=1-2q_\ell\), this becomes

\[
\boxed{
P_z^{(p)}(y)
=
2^{-\ell}
\left[1+(-1)^z c_\ell(p)\pi(y)\right].
}
\]

This one-line Fourier form exposes three important facts.

### Proper marginals remain exactly blind

Take any proper subset \(S\subsetneq\{1,\ldots,\ell\}\). Summing over at least
one omitted sign cancels the parity term because

\[
\sum_{y_j\in\{-1,+1\}}y_j=0.
\]

Thus

\[
\boxed{
P_z^{(p)}(y_S)=2^{-|S|}
}
\]

for every phase \(z\), every declared \(p\), and every proper subset \(S\).
Noise weakens the global relation but does not make the phase appear in lower-
order local marginals.

### Exact phase distance

For opposite phases,

\[
P_0^{(p)}(y)-P_1^{(p)}(y)
=
2^{1-\ell}c_\ell(p)\pi(y).
\]

Taking absolute values and summing over all \(2^\ell\) strings gives

\[
\boxed{
\operatorname{TV}
\left(P_0^{(p)},P_1^{(p)}\right)
=c_\ell(p)
=(1-2p)^\ell.
}
\]

### Parity is sufficient

The likelihood ratio between the two phases depends on \(y\) only through
\(\pi(y)\). Therefore the full \(\ell\)-bit transcript contains exactly the
same phase information as one noisy parity bit:

\[
z\longrightarrow \pi(y)
\]

is a binary symmetric channel with crossover \(q_\ell(p)\).

This is easy to miss when counting raw transcripts. There are \(2^\ell\)
possible local records, but only one relational sufficient statistic matters
for phase inference.

---

## 3. The locality-robustness tradeoff

The noiseless construction becomes more nonlocal as \(\ell\) grows: every
proper subset remains blind, so one must aggregate all \(\ell\) outcomes to see
the phase.

Under fixed independent readout noise, however,

\[
c_\ell(p)=(1-2p)^\ell
\]

decays exponentially in \(\ell\) whenever \(p>0\). For small \(p\),

\[
\log c_\ell(p)
=
\ell\log(1-2p)
\approx -2p\ell,
\]

so

\[
c_\ell(p)\approx e^{-2p\ell}.
\]

This yields a first-principles tradeoff:

- increasing \(\ell\) hides the relation from larger local subsets;
- the same increase exponentially attenuates the observable parity signal under
  independent local noise.

To retain phase distance at least \(c_0\in(0,1)\), the block size must satisfy

\[
\boxed{
\ell
\le
\frac{\log c_0}{\log(1-2p)}.
}
\]

Both logarithms are negative. This is a model-specific robustness limit, not a
universal law of entanglement.

---

## 4. Repeating the noisy parity experiment

Let

\[
q=q_\ell(p),
\qquad
c=1-2q.
\]

Suppose the same phase is prepared independently \(r\) times and one parity
bit is recorded per preparation. Under phase zero, the number \(K\) of negative
parities has probability

\[
P_0(K=k)
=
\binom rk q^k(1-q)^{r-k},
\]

while under phase one,

\[
P_1(K=k)
=
\binom rk (1-q)^kq^{r-k}.
\]

Hence the exact repeated-sample total variation is

\[
\boxed{
\operatorname{TV}_r(q)
=
\frac12
\sum_{k=0}^{r}
\binom rk
\left|
q^k(1-q)^{r-k}
-(1-q)^kq^{r-k}
\right|.
}
\]

With equal priors, the Bayes-optimal phase error is

\[
\boxed{
P_{e,r}^{\star}
=
\frac{1-\operatorname{TV}_r(q)}{2}.
}
\]

The repository calculates both quantities exactly for finite \(r\).

### KL/Pinsker necessary samples

For one parity sample,

\[
D_{\mathrm{KL}}
\left(
\operatorname{Bern}(q)
\middle\|
\operatorname{Bern}(1-q)
\right)
=
(1-2q)
\log\frac{1-q}{q}.
\]

Call this \(D(q)\). Independent repetition gives KL \(rD(q)\). Pinsker's
inequality gives

\[
\operatorname{TV}_r(q)
\le
\sqrt{\frac{rD(q)}{2}}.
\]

Therefore reaching target separation \(\delta\) requires

\[
\boxed{
r
\ge
\frac{2\delta^2}{D(q)}.
}
\]

This is necessary, not sufficient.

### Bhattacharyya sufficient samples

The one-sample Bhattacharyya coefficient is

\[
B(q)=2\sqrt{q(1-q)}.
\]

For \(r\) products it is \(B(q)^r\), and

\[
P_{e,r}^{\star}
\le
\frac12B(q)^r.
\]

Thus a sufficient count for target error \(\alpha<1/2\) is

\[
\boxed{
r
\ge
\frac{\log(2\alpha)}{\log B(q)}
}
\]

when \(0<B(q)<1\), with the integer ceiling understood.

### Weak-signal scaling

Write \(q=(1-c)/2\). Then

\[
D(q)
=
c\log\frac{1+c}{1-c}
=2c^2+O(c^4).
\]

Therefore fixed target distinguishability requires on the order of

\[
\boxed{r=\Omega(c^{-2})}
\]

samples in the weak-signal regime. Since \(c=(1-2p)^\ell\), the sample burden
can grow like

\[
(1-2p)^{-2\ell}.
\]

This is the quantitative cost of recovering a relation that has been hidden
across a large noisy block.

---

## 5. Noisy online checkpoint geometry

Return to \(m\) independent cat blocks after \(\ell-1\) observed outcomes have
already been emitted in every block. In the noiseless model, each block has a
required final sign \(s_b\in\{-1,+1\}\).

Under the complete noisy transcript law, the conditional final outcome is

\[
P(Y_b=y\mid s_b)
=
\frac{1+ycs_b}{2},
\]

where \(c=1-2q\) is the surviving block-parity visibility. Equivalently, the
required sign passes through \(\operatorname{BSC}(q)\).

If future block \(b\) is selected with weight \(w_b\), two checkpoint
signatures \(s,t\in\{-1,+1\}^m\) satisfy

\[
\boxed{
\operatorname{TV}(P_s,P_t)
=
c
\sum_{b=1}^{m}w_b\mathbf 1\{s_b\ne t_b\}.
}
\]

For uniform queries,

\[
\boxed{
\operatorname{TV}(P_s,P_t)
=
c\frac{d_H(s,t)}{m}.
}
\]

The code checks the closed form against explicit joint distributions over block
index and final outcome.

---

## 6. Sharp worst-query memory threshold

Suppose an adversary may choose any future block after seeing which two hidden
checkpoint signatures are under comparison.

Distinct signatures disagree on some block. On that block, the two Bernoulli
laws have total variation \(c\). If one renderer state approximated both within
\(\epsilon\), the triangle inequality would require

\[
c\le2\epsilon.
\]

Therefore, when

\[
\epsilon<\frac c2,
\]

no two of the \(2^m\) signatures can be merged. The renderer needs at least
\(2^m\) predictive states, or \(m\) bits.

Conversely, the unbiased distribution \(P(+1)=P(-1)=1/2\) lies at distance
\(c/2\) from either sign law. When \(\epsilon\ge c/2\), one state that predicts
an unbiased outcome for every block approximates every signature.

Thus this one-step worst-query model has an exact phase transition:

\[
\boxed{
B_{\mathrm{worst}}(m,q,\epsilon)
=
\begin{cases}
m,&\epsilon<(1-2q)/2,\\
0,&\epsilon\ge(1-2q)/2.
\end{cases}
}
\]

This all-or-nothing result depends on the worst-query interface. Average-query
memory behaves more gradually.

---

## 7. Finite uniform-query coding bound

Under a uniform future block query, a code
\(C\subseteq\{-1,+1\}^m\) with minimum Hamming distance \(d\) has minimum
predictive distance

\[
c\frac dm.
\]

It is a valid \(2\epsilon\)-separated packing whenever

\[
\frac{cd}{m}>2\epsilon.
\]

The smallest integer distance satisfying the strict inequality is

\[
\boxed{
d_\epsilon
=
\left\lfloor\frac{2\epsilon m}{c}\right\rfloor+1.}
\]

Using the finite Gilbert argument,

\[
\boxed{
|C|
\ge
\left\lceil
\frac{2^m}
{\sum_{j=0}^{d_\epsilon-1}\binom mj}
\right\rceil.
}
\]

Therefore an \(\epsilon\)-accurate renderer on the code family needs at least

\[
\boxed{
\left\lceil\log_2|C|\right\rceil
}
\]

internal bits. If \(c=0\), all checkpoint laws coincide and the lower bound is
zero.

---

## 8. Exact average predictive rate-distortion lower bound

The coding bound above is worst-case over a selected family. A different and
more general question averages over all hidden signatures.

Let

\[
Z=(Z_1,\ldots,Z_m)
\sim\operatorname{Unif}\{-1,+1\}^m.
\]

An encoder maps \(Z\) to an internal predictive state \(M\), possibly using
randomization. For query \(i\), the decoder may output any Bernoulli law with
bias

\[
b_i(M)\in[-1,1].
\]

The target law has bias \(cZ_i\). The one-query total variation loss is

\[
d(Z_i,b_i(M))
=
\frac{|cZ_i-b_i(M)|}{2}.
\]

Assume the average distortion satisfies

\[
\frac1m\sum_{i=1}^{m}
E\left[
\frac{|cZ_i-b_i(M)|}{2}
\right]
\le D.
\]

### Conditional-median reduction

Fix \(M=m_0\) and one coordinate. Let

\[
\eta=P(Z_i=+1\mid M=m_0).
\]

The conditional expected loss of a proposed bias \(b\) is

\[
L(b)
=
\frac12
\left[
\eta|c-b|+(1-\eta)|-c-b|
\right].
\]

Absolute loss is minimized by a conditional median of the two-point posterior:

\[
b^\star
=
\begin{cases}
+c,&\eta>1/2,\\
-c,&\eta<1/2,\\
\text{any }b\in[-c,c],&\eta=1/2.
\end{cases}
\]

The minimum loss is

\[
L(b^\star)
=c\min(\eta,1-\eta).
\]

Thus allowing arbitrary real-valued predicted biases does not improve expected
performance over decoding one binary sign and then outputting the corresponding
physical bias \(\pm c\). The predictive problem reduces exactly to Hamming
distortion scaled by \(c\).

### Information lower bound

Let \(e_i\) be the Bayes error for decoding \(Z_i\) from \(M\). Conditional
median optimality gives

\[
\frac1m\sum_i e_i\le\frac Dc.
\]

Binary Fano bounds and entropy subadditivity give

\[
\begin{aligned}
I(Z;M)
&=m-H(Z\mid M)\\
&\ge m-\sum_iH(Z_i\mid M)\\
&\ge m-\sum_iH_2(e_i)\\
&\ge m\left[1-H_2\left(\frac Dc\right)\right].
\end{aligned}
\]

Consequently

\[
\boxed{
I(Z;M)
\ge
m\left[1-H_2(D/c)\right]
}
\]

for \(0\le D<c/2\), and the lower bound is zero for \(D\ge c/2\).

Since

\[
I(Z;M)\le H(M)\le\log_2|\mathcal M|,
\]

any finite predictive-state set obeys

\[
\boxed{
\log_2|\mathcal M|
\ge
m\left[1-H_2(D/c)\right].
}
\]

This is a finite information lower bound. Standard Bernoulli Hamming
rate-distortion coding makes the per-bit expression asymptotically achievable,
so the single-letter rate is

\[
\boxed{
R(D)
=
1-H_2(D/c),
\qquad 0\le D\le c/2.
}
\]

The result cleanly separates three quantities:

- \(m\): number of independently open relational constraints;
- \(c\): reliability of each constraint after noise;
- \(D\): tolerated average predictive error.

---

## 9. Full noisy signature observations

Suppose two hidden binary signatures differ in exactly \(h\) coordinates and
all coordinates are independently observed through \(\operatorname{BSC}(q)\).
Coordinates on which the signatures agree factor out. Aggregating the remaining
\(h\) coordinates by the number \(k\) of outcomes favoring one signature gives

\[
\boxed{
\operatorname{TV}_h(q)
=
\frac12
\sum_{k=0}^{h}
\binom hk
\left|
q^k(1-q)^{h-k}
-(1-q)^kq^{h-k}
\right|.
}
\]

The Bhattacharyya coefficient is

\[
\left[2\sqrt{q(1-q)}\right]^h.
\]

Since

\[
1-\operatorname{TV}(P,Q)
=
\sum_x\min(P(x),Q(x))
\le
\sum_x\sqrt{P(x)Q(x)},
\]

we obtain

\[
\boxed{
\operatorname{TV}_h(q)
\ge
1-\left[2\sqrt{q(1-q)}\right]^h.
}
\]

So sufficiently separated codewords become almost perfectly distinguishable
under complete noisy observation even though one coordinate is unreliable.
This is the ordinary redundancy benefit of coding, expressed directly in
predictive-law distance.

---

## 10. What this changes in the simulation discussion

The noiseless relational result says an online generator cannot forget every
local outcome: it must retain enough state to satisfy later parity checks.

The noisy result sharpens that statement.

1. **Not every microscopic relation must be retained exactly.** When the
   allowed predictive error exceeds half the surviving visibility, one unbiased
   approximation can replace all one-step worst-query signatures.
2. **Below that threshold, relational memory remains extensive.** The exact
   worst-query lower bound is still one bit per open block.
3. **Average tolerance creates a rate-distortion curve, not a binary answer.**
   Required information decreases as
   \(m[1-H_2(D/c)]\).
4. **Large hidden relations can become fragile.** Independent local noise makes
   parity visibility decay exponentially with block size.
5. **Redundancy can restore reliability, but at a calculable cost.** Repeated
   samples and code distance recover distinguishability according to exact
   binomial laws, KL bounds, and Bhattacharyya exponents.

These statements constrain only a renderer that is required to reproduce the
declared noisy transcript family. They do not distinguish an exact simulator
from ordinary quantum physics, because both can generate the same law.

---

## Nonclaims

- Independent identical local flips are a model assumption, not a universal
  description of laboratory noise.
- The parity-visibility decay is not evidence of finite precision or a parent
  computation budget.
- Predictive mutual information is not automatically physical RAM usage.
- The rate-distortion theorem averages over a uniform hidden signature and a
  uniform query coordinate; other source and query distributions have different
  rate functions.
- Repeated parity preparations are independent by assumption.
- The finite Gilbert bound and the average rate-distortion bound answer
  different operational questions and must not be substituted for each other.
- None of these identities makes cat states, noise, or error correction generic
  evidence for simulation.

---

## Next research targets

1. Replace independent flips with correlated and adversarial noise.
2. Derive strong-data-processing bounds for causal chains of noisy relational
   state.
3. Add explicit CSS and stabilizer error-correcting codes whose logical labels
   are locally hidden below code distance.
4. Study communication-memory tradeoffs when distributed observers reconcile
   noisy authenticated records.
5. Derive online update-time lower bounds for maintaining many overlapping
   parity constraints.
6. Compare classical sufficient statistics with tensor-network and stabilizer
   representations of the same future law.
