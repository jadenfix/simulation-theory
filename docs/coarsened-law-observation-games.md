# Coarsened source-law observations and exact policy-vector frontiers

## Scope

The observed-law dynamic-game result assumes that the exact current source law
is revealed before each codebook choice. The open-loop result assumes that no
new source-law information arrives after the initial commitment. Between those
endpoints lies a large class of information patterns:

\[
\text{current law state}
\longrightarrow
\text{deterministic coarsened observation}
\longrightarrow
\text{code choice}.
\]

This note solves a finite, deterministic, worst-case set-membership version of
that problem. It does **not** attach probabilities to hidden law states. It does
not estimate a law from samples. It preserves one actual hidden path through a
declared transition relation.

The main subtlety is that a scalar Bellman value indexed only by the current
information set is generally insufficient. The exact recursion must retain a
Pareto frontier of cost vectors, one coordinate per possible actual hidden law
state.

---

## 1. Finite hidden law and observation model

Let

\[
\mathcal Q
=
\{q^{(1)},\ldots,q^{(m)}\}
\subseteq\Delta_{n-1}
\]

be exact rational categorical source laws. Let

\[
\Gamma(i)
\subseteq
\{1,\ldots,m\}
\]

be a nonempty directed transition relation. Nature selects one actual law-state
path

\[
i_1,i_2,\ldots,i_T
\]

with

\[
i_{t+1}\in\Gamma(i_t).
\]

The controller does not necessarily observe \(i_t\). It observes

\[
o_t=h(i_t),
\]

where

\[
h:\{1,\ldots,m\}\to\mathcal O
\]

is a deterministic partition map.

At each period:

1. the current observation is revealed;
2. one deterministic zero-error prefix code is chosen;
3. expected code length and any switching penalty are charged;
4. nature selects the next reachable hidden law state.

The code transition relation is source-independent in this lane.

---

## 2. Information sets

Given the observation history, the controller knows that the current hidden law
belongs to an information set

\[
B_t
\subseteq
h^{-1}(o_t).
\]

Let

\[
\operatorname{Post}(B)
=
\bigcup_{i\in B}\Gamma(i).
\]

If the next observation is \(o\), the correct next information set is

\[
\boxed{
B'_o
=
\operatorname{Post}(B)
\cap
h^{-1}(o).
}
\]

This update preserves every hidden transition still compatible with the public
observation history. It does not identify which current \(i\in B\) was actual.

---

## 3. Why a scalar information-set Bellman equation can be wrong

A tempting recursion is

\[
V_t(B)
=
\min_c
\max_{i\in B}
\left[
\text{stage}(i,c)
+
\max_{j\in\Gamma(i)}V_{t+1}(B'_{h(j)})
\right].
\]

But a scalar \(V_{t+1}(B')\) is already maximized over *all* hidden states in
\(B'\). It can therefore let nature arrive at one next state \(j\) and then
silently replace it by a different state in the same information set. That can
splice together branches that do not form one admissible hidden path.

### Exact K3 counterexample

Use three point-mass source laws, identity transitions, no observation, and a
three-period horizon. Every complete binary zero-error code for \(K_3\) has a
permutation of lengths

\[
(1,2,2).
\]

The hidden state is fixed for all three periods. Assign the short leaf to a
different state in each period. Every possible hidden state then incurs

\[
1+2+2=5.
\]

Hence the exact open-loop/set-membership value is at most five, and a simple
counting argument makes five optimal.

A scalar rectangular relaxation can choose a length-two state independently at
every period and charges

\[
2+2+2=6.
\]

Thus

\[
\boxed{
V_{\rm path}=5
<
V_{\rm rectangular}=6.
}
\]

The missing object is the continuation cost conditional on each possible
actual hidden state.

---

## 4. Achievable policy cost vectors

Fix period \(t\), information set \(B\), and previous code \(c^-\). Define

\[
\mathcal F_t(B,c^-)
\subseteq
\mathbb Q^B
\]

to be the set of future-cost vectors achievable by deterministic continuation
policies.

For

\[
v\in\mathcal F_t(B,c^-),
\]

the coordinate \(v_i\) is the worst future cost of that policy when the actual
current hidden state is \(i\in B\).

Only Pareto-minimal vectors are needed. If

\[
u_i\le v_i
\quad\forall i\in B
\]

with strict inequality somewhere, then every parent operation weakly prefers
\(u\). Addition, coordinate selection, and maximization over successors are all
coordinatewise monotone.

---

## 5. Terminal frontier

Let \(\mathcal C\) be the complete bounded deterministic zero-error prefix-code
universe. Code \(c\) has state-length vector \(\ell_c\). With switching penalty
\(\kappa\), define

\[
s(i,c,c^-)
=
(q^{(i)})^\top\ell_c
+
\kappa\mathbf1\{c\ne c^-\}.
\]

The first code has a sentinel predecessor and pays no switching penalty.

At terminal period \(T\), one code is selected and no continuation remains:

\[
\boxed{
\mathcal F_T(B,c^-)
=
\operatorname{ParetoMin}
\left\{
\bigl(s(i,c,c^-)\bigr)_{i\in B}
:
 c\in\mathcal C
\right\}.
}
\]

---

## 6. Exact nonterminal frontier recursion

At period \(t<T\):

1. select one current code \(c\);
2. compute every reachable next observation cell
   \(B'_o=\operatorname{Post}(B)\cap h^{-1}(o)\);
3. for each reachable \(o\), select one continuation vector
   \[
   w^o\in\mathcal F_{t+1}(B'_o,c);
   \]
4. construct the current vector
   \[
   v_i
   =
   s(i,c,c^-)
   +
   \max_{j\in\Gamma(i)}w^{h(j)}_j.
   \]

The exact recursion is therefore

\[
\boxed{
\mathcal F_t(B,c^-)
=
\operatorname{ParetoMin}
\left\{
(v_i)_{i\in B}
:
 c\in\mathcal C,
 
 w^o\in\mathcal F_{t+1}(B'_o,c)
\right\}.
}
\]

### Why this is exact

A deterministic policy at \((t,B,c^-)\) consists of:

- one current code \(c\);
- one continuation policy for every possible next public observation.

By induction, every continuation policy corresponds to a vector in the
appropriate next frontier. If the actual current state is \(i\), nature selects
one reachable actual successor \(j\), so the continuation cost is the maximum
of the coordinate belonging to that actual \(j\). This produces the displayed
vector.

Conversely, every code and tuple of continuation-frontier entries defines one
valid deterministic policy tree. Thus the construction enumerates exactly the
achievable cost vectors before safe Pareto pruning.

---

## 7. Value after an observation

Once current observation has reduced the possible states to \(B\), the
controller selects one frontier vector and nature's hidden current state selects
its largest coordinate:

\[
\boxed{
V_t(B,c^-)
=
\min_{v\in\mathcal F_t(B,c^-)}
\max_{i\in B}v_i.
}
\]

If an initial possible set \(B_0\) is given *before* the first observation, the
controller may use a different policy after each observed initial cell. Nature
selects the actual initial state and therefore the cell. The initial value is

\[
\boxed{
V_0(B_0)
=
\max_{o:B_0\cap h^{-1}(o)\ne\varnothing}
V_1(B_0\cap h^{-1}(o),\bot).
}
\]

The certificate stores one policy-vector witness for every possible initial
observation and an attaining hidden path for the worst cell.

---

## 8. Observation refinement monotonicity

Let partition \(h_f\) refine \(h_c\): every fine cell is contained in one
coarse cell. A controller receiving the fine observation can compute the coarse
observation and ignore the additional distinction. Therefore every coarse
policy is implementable under the fine partition.

For a minimizing controller,

\[
\boxed{
V(h_f)
\le
V(h_c).
}

The implementation solves both exact frontier games and returns the rational
information gain

\[
\boxed{
\mathcal V(h_f:h_c)
=V(h_c)-V(h_f)
\ge0.
}
\]

### Strict three-level example

Use point-mass \(K_3\), identity transitions, a two-period horizon, and initial
uncertainty over all three states.

1. No observation, partition \(\{1,2,3\}\):
   one state receives no short leaf over two periods, so
   \[
   V=4.
   \]
2. Intermediate partition \(\{1\},\{2,3\}\):
   the singleton costs two, while alternating the short leaf inside the pair
   gives worst cost three, so
   \[
   V=3.
   \]
3. Full observation, three singleton cells:
   the short leaf follows the known fixed state, so
   \[
   V=2.
   \]

Hence

\[
\boxed{4>3>2.}
\]

Coarsened information has an exact intermediate operational value.

---

## 9. Endpoint equivalence

### No observation

Suppose the initial law state is known and all future law states share one
observation label. The information-set sequence is determined by time and the
transition relation, independent of the actual hidden path. A policy can
therefore be written as one precommitted time-indexed code sequence. The exact
frontier value equals the independent open-loop sequence solver:

\[
\boxed{V_{\rm one\ cell}=V_{\rm open\ loop}.}
\]

### Full observation

With singleton observation cells, every information set is a singleton. A
frontier vector has one coordinate, Pareto pruning reduces it to the minimum
scalar value, and the recursion becomes the fully observed Bellman equation:

\[
\boxed{V_{\rm singleton}=V_{\rm feedback}.}
\]

The repository computes both routes independently and requires exact rational
value agreement.

---

## 10. Complexity and bounded completeness

The frontier recursion is exact but can grow rapidly. At each node it combines
one continuation-frontier choice for every reachable next observation cell.
The implementation therefore declares hard caps on:

- law states and code-candidate enumeration;
- information-set nodes;
- continuation-policy combinations;
- Pareto frontier entries;
- dominance comparisons.

Crossing a cap raises an error. Truncated search is never returned as an exact
certificate.

The finite construction is intended as a theorem harness and counterexample
generator, not as a claim of scalable solution to arbitrary imperfect-
information dynamic games.

---

## 11. What this adds to predictive-rendering analysis

The relevant information resource is not simply whether a hidden predictive
state is observed. It may be observed through a quotient:

\[
\text{hidden state}
\to
\text{observation class}
\to
\text{representation choice}.
\]

More informative observations can lower robust representation cost, but the
benefit depends on:

- the transition relation;
- the timing of the observation;
- the code action set;
- switching penalties;
- whether hidden-path consistency is preserved;
- whether the controller uses worst-case sets or probabilistic beliefs.

A scalar worst-case value attached to an information set can erase hidden-path
consistency. The policy-vector frontier is the finite exact object for the
deterministic set-membership model.

This is ordinary information-pattern and source-coding mathematics. It neither
supports nor refutes simulation without an independently justified mapping from
that internal model to a restricted simulator architecture.

---

## Nonclaims

- The observation partition is declared, not learned.
- The current hidden law is not assigned a Bayesian posterior.
- Nature selects one transition-consistent hidden path; the solver does not
  permit arbitrary state reselection inside an information set.
- The controller is deterministic and has perfect recall of public observation
  history and prior code choices.
- Source transitions are code-independent.
- The finite law-state model is not a certified abstraction of a continuous
  source-law process unless separate abstraction bounds are supplied.
- The result does not cover noisy observation kernels, samples, partial
  posterior beliefs, or confidence sequences.
- Switching penalty is an abstract declared cost.
- Internal expected message lengths are not parent-universe hardware, energy,
  mass, or spacetime.
- None of these results is empirical evidence for simulation.

---

## Next research targets

1. Stochastic observation kernels and exact finite belief-state dynamic
   programming.
2. Robust belief-set updates under set-valued observations.
3. Lower and upper abstractions from continuous law spaces to finite law states.
4. Shared-randomness policies under oblivious versus seed-observing nature.
5. Observation acquisition cost and active sensing.
6. Code-dependent transitions and strategic source response.
7. Dynamic regret against open-loop, feedback, and clairvoyant comparators.
8. Networked decoders receiving different coarsenings or delayed code updates.
