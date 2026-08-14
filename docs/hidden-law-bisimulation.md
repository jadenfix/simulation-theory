# Hidden-law bisimulation and predictive-state quotienting

## Scope

The Bayesian hidden-source-law model may contain several syntactically distinct
hidden states.  A larger hidden-state alphabet does not automatically imply a
larger predictive state.  Two hidden states can differ only in names or in
internal transitions that never change any future observable or coding-relevant
law.

This note defines an exact probabilistic bisimulation for the repository's
hidden-law coding interface and constructs the coarsest quotient.

A hidden state determines three objects:

1. the categorical source law used for expected prefix length;
2. the observation-channel row used to generate the current signal;
3. the distribution of the next hidden state.

The first two are immediate observable/cost labels.  The third matters only
through the future behavioral equivalence classes.

The quotient theorem is internal to this declared finite stochastic model.  It
does not claim that behaviorally equivalent physical systems are ontologically
identical, and it does not identify quotient-state count with parent-universe
memory.

---

## 1. Behavioral equivalence

Let the finite hidden-state set be \(\mathcal S\).  State \(s\) has:

- source law \(p^{(s)}\);
- observation row \(O_s\);
- transition law \(K_s\).

For a partition

\[
\Pi=\{B_1,\ldots,B_r\}
\]

of \(\mathcal S\), define the transition signature

\[
\boxed{
\tau_\Pi(s)
=
\left(
K_s(B_1),\ldots,K_s(B_r)
\right),
}
\]

where

\[
K_s(B_j)=\sum_{u\in B_j}K_{su}.
\]

The partition is a hidden-law bisimulation when every two states \(s,t\) in the
same block satisfy

\[
\boxed{
 p^{(s)}=p^{(t)},
 \qquad
 O_s=O_t,
 \qquad
 \tau_\Pi(s)=\tau_\Pi(t).
}
\]

The conditions have separate roles:

- equal source laws make every codebook's current expected length identical;
- equal observation rows make the current signal law identical;
- equal class-transition signatures make the next equivalence-class law
  identical.

Equality of raw transition rows is not required.  States may redistribute
probability differently *within* one equivalence block without changing any
future block-level behavior.

---

## 2. Exact partition refinement

Start with the partition induced by immediate labels:

\[
\Pi_0
=
\text{classes of equal }(p^{(s)},O_s).
\]

Given \(\Pi_k\), split each current block by the exact rational transition
signature \(\tau_{\Pi_k}(s)\).  This produces

\[
\Pi_{k+1}=F(\Pi_k).
\]

Every refinement is finite and strict unless stable.  Therefore the process
terminates after at most \(|\mathcal S|-1\) strict refinements.

At termination,

\[
\Pi_*=F(\Pi_*),
\]

so states in each block have equal labels and equal transition mass into every
final block.  Hence \(\Pi_*\) is a bisimulation.

The implementation stores the complete refinement trace and verifies each split
in exact rational arithmetic.

---

## 3. Coarsest-bisimulation theorem

The fixed point is not merely one valid partition.  It is the coarsest
bisimulation respecting the declared source and observation labels.

Let \(\mathcal R\) be any such bisimulation partition.

First, \(\mathcal R\) refines \(\Pi_0\), because states related by \(\mathcal R\)
must have equal source laws and equal observation rows.

Assume inductively that \(\mathcal R\) refines \(\Pi_k\).  Every block
\(B\in\Pi_k\) is then a union of \(\mathcal R\)-blocks.  If states \(s,t\) lie
in one \(\mathcal R\)-block, bisimulation gives equal transition probability to
every \(\mathcal R\)-block.  Summing those equalities over the
\(\mathcal R\)-blocks contained in \(B\) gives

\[
K_s(B)=K_t(B).
\]

Thus \(s,t\) have equal signatures with respect to \(\Pi_k\) and cannot be
separated by the next refinement.  Therefore \(\mathcal R\) refines
\(\Pi_{k+1}\).

By induction, every valid bisimulation refines every \(\Pi_k\), and therefore
refines the stable partition \(\Pi_*\).  Hence

\[
\boxed{
\Pi_*\text{ is the unique coarsest hidden-law bisimulation.}
}
\]

---

## 4. Quotient hidden Markov model

For each final block \(B_i\), choose any representative \(s_i\in B_i\).  Define

\[
\bar p^{(i)}=p^{(s_i)},
\qquad
\bar O_i=O_{s_i}.
\]

These are representative independent because labels are constant on a block.

Aggregate the initial belief:

\[
\boxed{
\bar\mu_i
=
\sum_{s\in B_i}\mu_s.
}
\]

Define quotient transitions by

\[
\boxed{
\bar K_{ij}
=
\sum_{u\in B_j}K_{s_i u}.
}
\]

This is also representative independent because transition signatures are
constant on each block.

Each quotient transition row is nonnegative and sums to one.  Thus

\[
(\bar\mu,\bar K,\bar p,\bar O)
\]

is a valid finite hidden Markov source-law model.

---

## 5. Equality of finite observation laws

Let \(C_t\) be the quotient class containing \(S_t\).  The bisimulation
conditions imply:

\[
P(C_{t+1}=j\mid S_t=s)
=
\bar K_{ij}
\qquad
s\in B_i.
\]

Therefore the class process is Markov with transition matrix \(\bar K\).
Conditional on \(C_t=i\), every internal state in \(B_i\) has the same source
law and observation row.  Hence the joint finite-dimensional law of

\[
(C_{1:T},Y_{1:T},X_{1:T})
\]

in the original model equals the law generated directly by the quotient model,
where \(X_t\) denotes the categorical source symbol.

Internal hidden-state identity may retain correlations inside one class, but
those identities neither change current coding loss nor alter the future class,
signal, or source-symbol law.

---

## 6. Preservation of causal coding values

### No-signal policies

A no-signal policy depends only on time and previous codebook.  Its expected
cost depends on the hidden model only through the marginal class distribution,
which is identical in the quotient.  Therefore every policy has the same cost
in both models, and the optimal no-signal values agree.

### Noisy-observation policies

Every signal history has the same probability under the original and quotient
models.  Given one signal history, the posterior probability of each quotient
class is the aggregation of the original posterior over that class.  Since all
states in a class have the same codebook loss and class transition law, the
conditional future control problem is identical.  Therefore

\[
\boxed{
V_{\rm obs}^{\rm original}
=
V_{\rm obs}^{\rm quotient}.
}
\]

### Perfect current-state observation

The original perfect observer sees the internal state, while the quotient
observer sees only its class.  Internal identity does not improve control:
within a class,

- all current codebook losses are identical;
- the next class distribution is identical;
- the future within-class identity remains irrelevant by induction.

A finite-horizon induction therefore gives a value function constant on every
bisimulation block and

\[
\boxed{
V_{\rm perfect}^{\rm original}
=
V_{\rm perfect}^{\rm quotient}.
}
\]

---

## 7. Preservation of the clairvoyant path oracle

The clairvoyant code-sequence oracle sees the complete hidden path before
selecting a code sequence.  Its realized cost depends on that path only through
the corresponding source-law/class path, because stage cost under each codebook
is constant within a class and switching cost depends only on codebook changes.

Thus all internal paths mapping to one class path have the same oracle cost.
Their probabilities sum to the quotient class-path probability.  Therefore

\[
\boxed{
E[O(S_{1:T})]
=
E[O(C_{1:T})].
}
\]

Subtracting the common clairvoyant constant also preserves all three Bayes
regrets.

The repository solves the original and quotient coding models independently and
requires exact equality of:

- no-signal value;
- noisy-observation value;
- perfect-state value;
- expected clairvoyant value;
- all corresponding regrets.

---

## 8. Predictive multiplicity versus syntactic multiplicity

Suppose a model replaces one hidden state by several copies with:

- the same source law;
- the same observation row;
- equal total transition mass into every behavioral class.

The syntactic hidden-state count increases, but the coarsest quotient and every
finite coding value remain unchanged.

Therefore raw hidden-state multiplicity is not, by itself, predictive
multiplicity:

\[
\boxed{
\text{more state labels}
\not\Rightarrow
\text{more behaviorally distinct predictive states}.
}

This parallels the repository's earlier warning about counting multiple
programs that implement one observable law.  Representation copies should not
be counted as separate evidence or separate predictive burden without an
operational distinction.

---

## 9. Example with nonidentical raw transitions

Consider three hidden states.  States zero and one share one source law and one
observation row; state two has different labels.  Let

\[
K_0=(1/2,1/4,1/4),
\]

\[
K_1=(1/4,1/2,1/4),
\]

\[
K_2=(1/4,1/4,1/2).
\]

The raw rows for states zero and one differ, but both assign

\[
3/4
\]

to the block \(\{0,1\}\) and

\[
1/4
\]

to \(\{2\}\).  Hence they are bisimilar.

The quotient transition matrix is

\[
\boxed{
\bar K
=
\begin{pmatrix}
3/4 & 1/4\\
1/2 & 1/2
\end{pmatrix}.
}
\]

An initial belief \((1/4,1/4,1/2)\) becomes \((1/2,1/2)\).  The exact bounded
checker confirms the original three-state model and quotient two-state model
have identical finite-horizon coding and regret values.

---

## Nonclaims

- Bisimilarity is behavioral equivalence for the declared interface, not
  metaphysical or physical identity.
- Source-law and observation-row equality are exact assumptions; approximate
  quotienting requires explicit value-loss bounds.
- The quotient theorem assumes action-independent hidden transitions and
  observation channels.
- Perfect-state value preservation relies on all action costs being constant
  within each final block.
- The refinement implementation is finite and exact, not a complexity result
  for very large models.
- Quotient-state count is not parent-universe memory, energy, or hardware.
- A smaller equivalent hidden model is not evidence that reality is simulated.

---

## Next research targets

1. Approximate bisimulation under bounded source-law, observation, and transition
   perturbations.
2. Explicit value-loss bounds for merging nearly equivalent hidden states.
3. Action-dependent probabilistic bisimulation.
4. Bisimulation metrics for controlled observation channels.
5. Joint quotienting of hidden states and codebooks.
6. Minimal predictive state under sampled-symbol observations.
7. Unknown-model Bayesian or robust quotienting.
8. Infinite-horizon quotient preservation.
