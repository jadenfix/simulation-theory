# Finite-prior robust zero-error prefix coding

## Scope

The prior-weighted coding lane solves a one-shot problem under one declared
source prior:

\[
L^*(G,\pi)
=
\min_{c\in\mathcal C(G)}L_c(\pi),
\]

where \(G\) is a finite confusion graph, \(\mathcal C(G)\) is the set of
zero-error binary prefix codebooks, and \(L_c(\pi)\) is code \(c\)'s expected
length under prior \(\pi\).

That solution can be fragile when the source law is uncertain. A tree that
places one state at depth one may be excellent when that state has probability
\(0.8\) and poor when a different state has probability \(0.8\).

This note replaces one prior by a finite nonempty scenario set

\[
\Pi=\{\pi^{(1)},\ldots,\pi^{(R)}\}.
\]

It separates four different robust resources and objectives:

1. deterministic minimax expected length;
2. deterministic minimax regret relative to a scenario-specific oracle;
3. shared-randomness minimax expected length;
4. shared-randomness minimax regret.

Every prior, codeword length, mixture weight, expected length, regret, and dual
certificate is rational. Every graph, partition, prefix tree, and support search
is finite and explicitly capped.

The shared random seed is an assistance resource known to encoder and all
decoders before the state is encoded. Private encoder randomness is not a
substitute: without the seed, a receiver would not know which partition or
prefix tree was selected.

These are internal one-shot source-coding results. They are not queueing or hard
network-capacity theorems, do not create a universal prior, and are not evidence
for simulation or parent-substrate resource claims.

---

## 1. Deterministic code universe

A deterministic zero-error codebook has two layers.

First, the graph vertices are partitioned into independent message classes:

\[
\mathcal P=\{C_1,\ldots,C_k\}.
\]

Second, each class receives one codeword in a binary prefix tree. Let the class
lengths be

\[
\ell_1,\ldots,\ell_k.
\]

Every source state in class \(C_j\) has state length \(\ell_j\). Under scenario
\(r\), the expected cost is

\[
L_r(c)
=
\sum_{j=1}^k
\left(
\sum_{x\in C_j}\pi_x^{(r)}
\right)
\ell_j.
\]

The robust code must be chosen before the scenario is revealed.

### Why complete binary trees suffice

The objectives in this note are coordinatewise nondecreasing in state lengths:
shortening a codeword under every scenario cannot worsen absolute expected
length or regret.

If an internal prefix-tree node has only one occupied child, contract that node.
Every descendant codeword becomes one bit shorter and no prefix conflict is
created. Repeating the contraction produces a full binary tree with no larger
cost under any scenario.

A full binary tree with \(k\) leaves has maximum leaf depth at most \(k-1\): a
root-to-leaf path of depth \(d\) contains \(d\) internal nodes, and every such
node contributes at least one distinct off-path leaf, so the tree has at least
\(d+1\) leaves.

Therefore every nondominated robust code is represented by:

- one proper independent-set partition;
- one labeled length vector

  \[
  \ell_j\in\{1,\ldots,k-1\}
  \]

  for \(k>1\), or \((0)\) for \(k=1\);
- exact Kraft equality

  \[
  \sum_j2^{-\ell_j}=1.
  \]

The bounded checker enumerates this complete finite universe. A cap exceedance
raises and certifies nothing.

---

## 2. Exact scenario-cost frontier and safe pruning

Each deterministic code induces a rational cost vector

\[
\mathbf L(c)
=
\bigl(L_1(c),\ldots,L_R(c)\bigr).
\]

Two different codebooks can have the same vector. Because every objective in
this note depends only on those scenario costs, one canonical representative is
retained.

A candidate \(c\) dominates \(d\) when

\[
L_r(c)\le L_r(d)
\qquad\forall r
\]

with strict inequality for at least one scenario. A dominated code can be
removed from:

- deterministic minimax length;
- deterministic minimax regret;
- mixtures minimizing either objective.

For regret, every candidate in scenario \(r\) subtracts the same oracle
constant \(L_r^*\), so dominance is preserved.

The resulting Pareto frontier is exact, not a heuristic beam or sampled code
family.

---

## 3. Prior-specific oracle values

For each scenario define the oracle expected length

\[
\boxed{
L_r^*
=
\min_{c\in\mathcal C(G)}L_r(c).
}
\]

This is the cost of designing a code after being told which prior is active. It
is not generally attainable by one code chosen before the scenario.

The oracle vector is used in two ways:

- as a lower bound on any robust absolute-length design;
- as the scenario baseline for regret.

Because the deterministic code universe is fully enumerated below the declared
caps, the oracle values are exact rational minima rather than separately fitted
approximations.

---

## 4. Deterministic minimax expected length

The deterministic robust value is

\[
\boxed{
V_{\mathrm{det}}
=
\min_{c\in\mathcal C(G)}
\max_{1\le r\le R}L_r(c).
}
\]

It obeys

\[
\boxed{
\max_rL_r^*
\le
V_{\mathrm{det}}
\le
\left\lceil\log_2\chi(G)\right\rceil.
}
\]

The lower bound follows because the robust code cannot beat the scenario oracle
in any scenario. The upper bound uses fixed-length labels for a minimum
coloring, whose expected length equals the fixed length under every prior.

The robust minimax code need not be Huffman-optimal for any individual scenario.
The max across scenarios can favor a balanced tree that every scenario-specific
Huffman procedure rejects.

---

## 5. Deterministic minimax regret

Absolute robust length and competitive robustness answer different questions.
Define scenario regret

\[
\operatorname{Reg}_r(c)
=L_r(c)-L_r^*.
\]

The deterministic minimax-regret value is

\[
\boxed{
R_{\mathrm{det}}
=
\min_{c\in\mathcal C(G)}
\max_r\operatorname{Reg}_r(c).
}
\]

A minimax-length design protects the largest absolute traffic. A minimax-regret
design protects the loss relative to what could have been achieved had the
scenario been known. They need not choose the same tree.

The only universal ordering between their objective values is not a direct
comparison, because they have different units of baseline. What is universal is

\[
R_{\mathrm{det}}\ge0.
\]

The implementation reports both candidates and never labels one as the other.

---

## 6. Finite scenarios control their convex hull

A fixed code's expected length is linear in the prior. For

\[
\bar\pi
=
\sum_{r=1}^R\lambda_r\pi^{(r)},
\qquad
\lambda\in\Delta_{R-1},
\]

we have

\[
L_c(\bar\pi)
=
\sum_r\lambda_rL_c\bigl(\pi^{(r)}\bigr).
\]

Therefore

\[
\boxed{
\sup_{\bar\pi\in\operatorname{conv}(\Pi)}
L_c(\bar\pi)
=
\max_rL_c\bigl(\pi^{(r)}\bigr).
}
\]

The same identity holds for a fixed mixture of codebooks because its expected
length is still linear in the source prior.

### Regret over the convex hull

The oracle function

\[
L^*(\pi)=\min_cL_c(\pi)
\]

is the pointwise minimum of linear functions and is therefore concave. Hence

\[
L^*(\bar\pi)
\ge
\sum_r\lambda_rL^*\bigl(\pi^{(r)}\bigr).
\]

For any fixed code,

\[
\begin{aligned}
L_c(\bar\pi)-L^*(\bar\pi)
&\le
\sum_r\lambda_r
\left[
L_c\bigl(\pi^{(r)}\bigr)
-L^*\bigl(\pi^{(r)}\bigr)
\right]\\
&\le
\max_r\operatorname{Reg}_r(c).
\end{aligned}
\]

Thus the declared finite extreme scenarios also control regret throughout their
entire convex hull. This conclusion relies on uncertainty being exactly that
convex hull; it does not cover an unrelated neighborhood or drifting process.

---

## 7. Shared-randomness codebook mixtures

Let \(q_c\) be a probability distribution over complete deterministic
codebooks. A shared seed independent of the source state selects codebook \(c\),
and every receiver knows the selection before decoding.

Under scenario \(r\), the expected length is

\[
\overline L_r(q)
=
\sum_cq_cL_r(c).
\]

Zero error is preserved because every selected deterministic codebook is
zero-error conditional on the seed.

The shared-randomness minimax value is

\[
\boxed{
V_{\mathrm{mix}}
=
\min_{q\in\Delta}
\max_r
\sum_cq_cL_r(c).
}
\]

This is a convexification of the code design, so

\[
\boxed{
V_{\mathrm{mix}}
\le
V_{\mathrm{det}}.
}
\]

The inequality can be strict.

The seed is not free. The certificate reports its rational codebook mixture and
support, but it does not convert those weights into an exact random-bit cost.
Sampling a non-dyadic rational mixture exactly requires a declared common
randomness model.

### Why private randomness is different

If only the encoder knows the selected codebook, the decoder does not know how
to interpret the message or where its prefix tree lies. The encoder would need
to communicate the codebook choice, or all codebooks would need to be embedded
into one larger decodable construction. Neither resource is included here.

This explains why the earlier theorem that private one-shot randomization does
not reduce the zero-error message alphabet is compatible with the present
shared-randomness gain in expected length.

---

## 8. Exact finite zero-sum game

Let the rational matrix

\[
A_{rc}=L_r(c)
\]

have one row per scenario and one column per nondominated deterministic
codebook.

The encoder's primal linear program is

\[
\begin{aligned}
\text{minimize }&v\\
\text{subject to }&
\sum_cq_cA_{rc}\le v
\quad\forall r,\\
&\sum_cq_c=1,\\
&q_c\ge0.
\end{aligned}
\]

The scenario player's dual is

\[
\begin{aligned}
\text{maximize }&u\\
\text{subject to }&
\sum_r\lambda_rA_{rc}\ge u
\quad\forall c,\\
&\sum_r\lambda_r=1,\\
&\lambda_r\ge0.
\end{aligned}
\]

Weak duality is immediate. For any feasible \(q\) and \(\lambda\),

\[
u
\le
\sum_{r,c}\lambda_rq_cA_{rc}
\le
v.
\]

Therefore a feasible primal and feasible dual with equal values are a complete
optimality certificate.

### Exact support enumeration

At a primal vertex with \(s\) positive codebook weights, normalization plus
\(s\) active scenario inequalities determines the \(s\) weights and \(v\).
The checker enumerates every code support and active-row set of equal size,
solves the square rational system exactly, and verifies every omitted scenario
inequality.

The dual side performs the symmetric enumeration over scenario supports and
active code constraints.

The returned certificate includes:

- exact primal and dual mixtures;
- every induced row and column cost;
- the common rational value;
- a zero rational duality gap;
- the number of support bases examined;
- the configured basis cap.

Completeness follows because a bounded feasible linear program has an optimal
vertex. The checker does not rely on a floating optimizer or a tolerance-based
claim of zero gap.

### Support bound

A primal basic solution uses at most \(R\) positive codebooks, where \(R\) is
the number of prior scenarios:

\[
\boxed{
|\operatorname{supp}q^*|\le R.
}
\]

This bounds the number of codebooks that shared randomness must select among,
but not the random-bit cost of realizing arbitrary rational weights.

---

## 9. Least-favorable barycenter prior

The dual mixture \(\lambda\) defines a barycenter prior

\[
\bar\pi_\lambda
=
\sum_r\lambda_r\pi^{(r)}.
\]

For every deterministic code,

\[
\sum_r\lambda_rL_r(c)
=L_c(\bar\pi_\lambda).
\]

The dual objective is therefore

\[
\max_{\lambda\in\Delta}
\min_cL_c(\bar\pi_\lambda)
=
\max_{\bar\pi\in\operatorname{conv}(\Pi)}L^*(\bar\pi).
\]

Combining this with the primal-dual equality gives the least-favorable-prior
identity

\[
\boxed{
V_{\mathrm{mix}}
=
\max_{\bar\pi\in\operatorname{conv}(\Pi)}
L^*(G,\bar\pi).
}
\]

The codebooks in the primal support are tied at the game value under the dual
barycenter, and every omitted codebook is no better there.

This identity is specific to shared-randomness minimax **expected length** and a
convex hull of priors. It should not be transferred without proof to peak
length, nonlinear queueing loss, or arbitrary distributional uncertainty.

For minimax regret, the dual formula is instead

\[
\boxed{
R_{\mathrm{mix}}
=
\max_{\lambda\in\Delta}
\left[
L^*(\bar\pi_\lambda)
-
\sum_r\lambda_rL_r^*
\right].
}
\]

The scenario-oracle subtraction remains explicit.

---

## 10. Robust bound hierarchy

The four values obey

\[
\boxed{
\max_rL_r^*
\le
V_{\mathrm{mix}}
\le
V_{\mathrm{det}}
\le
\left\lceil\log_2\chi(G)\right\rceil.
}
\]

The first inequality holds because even a randomized design cannot beat each
scenario's oracle simultaneously. The second is convexification. The third is
the fixed-length minimum-coloring construction.

For regret,

\[
\boxed{
0
\le
R_{\mathrm{mix}}
\le
R_{\mathrm{det}}.
}
\]

There is no reason for the code minimizing absolute worst-case length to equal
the one minimizing worst-case regret.

---

## 11. Three-state strict shared-randomness gain

Let \(G=K_3\), and consider

\[
\pi^{(1)}
=
\left(
\frac45,
\frac1{10},
\frac1{10}
\right),
\]

\[
\pi^{(2)}
=
\left(
\frac1{10},
\frac45,
\frac1{10}
\right).
\]

Every deterministic prefix tree has lengths \((1,2,2)\) up to permutation.
The scenario oracles give the one-bit codeword to their own probability-\(4/5\)
state:

\[
L_1^*=L_2^*=\frac65.
\]

Any one deterministic tree can shorten at most one of those two states. The
exact deterministic robust values are

\[
\boxed{
V_{\mathrm{det}}=\frac{19}{10},
}
\]

and

\[
\boxed{
R_{\mathrm{det}}=\frac7{10}.
}
\]

Mix equally between the tree shortening state zero and the tree shortening
state one. Both scenarios then have cost

\[
\frac12\cdot\frac65
+
\frac12\cdot\frac{19}{10}
=
\boxed{\frac{31}{20}}.
\]

Thus

\[
\boxed{
V_{\mathrm{mix}}=\frac{31}{20}
<
\frac{19}{10}=V_{\mathrm{det}}.
}
\]

The mixed regret is

\[
\boxed{
R_{\mathrm{mix}}=\frac7{20}.
}
\]

The dual least-favorable scenario mixture is \((1/2,1/2)\), producing barycenter
prior

\[
\boxed{
\left(
\frac9{20},
\frac9{20},
\frac1{10}
\right).
}
\]

The zero-error message alphabet remains three. The gain concerns worst-prior
expected prefix length and consumes a shared codebook seed.

---

## 12. Four-state minimax tree need not be any scenario oracle

Let \(G=K_4\), with priors

\[
\pi^{(1)}
=
\left(
\frac1{10},
\frac1{10},
\frac1{10},
\frac7{10}
\right)
\]

and

\[
\pi^{(2)}
=
\left(
\frac1{10},
\frac1{10},
\frac7{10},
\frac1{10}
\right).
\]

Each oracle uses an unbalanced \((1,2,3,3)\) tree and obtains

\[
L_1^*=L_2^*=\frac32.
\]

No one unbalanced tree can give the one-bit position to both high-probability
states. The exact deterministic minimax tie-break selects the balanced tree

\[
(2,2,2,2),
\]

with

\[
\boxed{V_{\mathrm{det}}=2.}
\]

That tree is strictly suboptimal in both individual scenarios. This is why a
robust solver cannot enumerate only scenario-specific Huffman trees.

Mixing the two relevant unbalanced trees gives

\[
\boxed{V_{\mathrm{mix}}=\frac95,}
\]

while deterministic and mixed regrets are

\[
\boxed{
R_{\mathrm{det}}=\frac12,
\qquad
R_{\mathrm{mix}}=\frac3{10}.
}
\]

The least-favorable barycenter is

\[
\boxed{
\left(
\frac1{10},
\frac1{10},
\frac25,
\frac25
\right).
}
\]

---

## 13. Minimax length and minimax regret can disagree

Again take \(G=K_4\), but use

\[
\pi^{(1)}
=
\left(
\frac1{10},
\frac1{10},
\frac1{10},
\frac7{10}
\right)
\]

and

\[
\pi^{(2)}
=
\left(
\frac1{10},
\frac15,
\frac12,
\frac15
\right).
\]

The oracle vector is

\[
\left(
\frac32,
\frac95
\right).
\]

The balanced tree has absolute scenario costs

\[
(2,2),
\]

so it minimizes absolute worst-case length at value two. Its regrets are

\[
\left(
\frac12,
\frac15
\right),
\]

with worst regret \(1/2\).

A different unbalanced tree has costs

\[
\left(
\frac32,
\frac{21}{10}
\right).
\]

Its regrets are

\[
\left(
0,
\frac3{10}
\right),
\]

so it is the deterministic minimax-regret code even though its absolute
worst-case cost \(21/10\) is larger.

Therefore

\[
\boxed{
\arg\min_c\max_rL_r(c)
\ne
\arg\min_c\max_r[L_r(c)-L_r^*]
}
\]

in this declared finite instance.

Shared randomness lowers the two values separately to

\[
\boxed{
V_{\mathrm{mix}}=\frac{19}{10},
\qquad
R_{\mathrm{mix}}=\frac15.
}
\]

---

## 14. Bounded certificate and independent checks

The implementation returns:

- the exact prior scenarios;
- an exact chromatic certificate and fixed-length upper bound;
- all configured partition, prefix-shape, candidate, dominance, and game caps;
- raw candidate, distinct cost-vector, dominated, and Pareto-frontier counts;
- exact state-length vectors and scenario costs;
- the scenario-oracle vector;
- deterministic minimax and minimax-regret codebooks;
- exact shared-randomness primal mixtures;
- exact dual scenario mixtures;
- least-favorable barycenter prior;
- every primal row cost and dual column cost;
- zero rational primal-dual gaps;
- mixture-support sizes and support-basis counts.

Independent tests:

1. enumerate complete Kraft-equality length vectors for one through four message
   classes;
2. check a matching-pennies rational game with known value \(1/2\);
3. verify the exact \(K_3\) and \(K_4\) examples;
4. verify the absolute-minimax versus regret separation;
5. reduce a one-scenario robust problem to the nominal prior-weighted optimum;
6. verify convex-hull linearity directly;
7. independently enumerate every coloring and complete tree on all 64 labeled
   four-vertex graphs, comparing deterministic and mixed length and regret
   values;
8. fail closed on candidate, prefix, dominance, and game-support caps.

---

## 15. Boundaries and next layer

This lane assumes a finite scenario set, or equivalently its convex hull for
expected-length and regret guarantees. It does not cover:

- a total-variation, KL, Wasserstein, moment, or contamination neighborhood not
  already equal to that convex hull;
- online prior drift or adversarially adaptive source processes;
- learning the prior from the same encoded sample;
- allowed decoding error;
- block graph products and asymptotic rates;
- queueing delay, overflow probability, or peak cut feasibility;
- private randomness without a codebook identifier;
- the random-bit cost of realizing non-dyadic shared mixtures;
- quantum codebook superpositions;
- parent-substrate costs or evidence for simulation.

The next exact layer should replace a finite prior list by a continuous
uncertainty set. For a total-variation ball and a fixed state-length vector,
the adversary has a mass-transport solution: move probability from the shortest
states to the longest states until the radius or available mass is exhausted.
That continuous inner problem can then be composed with the complete finite
code universe developed here.
