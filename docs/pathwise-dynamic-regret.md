# Pathwise dynamic regret under bounded source-law drift

## Scope

The preceding source-drift work minimizes worst-case **absolute** cumulative
cost. That objective answers:

> Which precommitted decision has the smallest cost on its worst feasible
> source-law path?

A different question is:

> How much worse is the precommitted decision than an oracle that sees the
> complete path before selecting from a declared comparator class?

That second quantity is pathwise regret. It measures nonclairvoyance relative
to an explicitly bounded oracle; it is not generally the difference of two
separately optimized robust values.

Let

\[
q_0=p,
\qquad
\operatorname{TV}(q_t,q_{t-1})\le\eta,
\quad t=1,\ldots,T.
\]

A precommitted affine decision \(a\) has period costs
\(g_{a,1},\ldots,g_{a,T}\) and a constant cost \(k_a\):

\[
C_a(q_{1:T})
=
k_a+
\sum_{t=1}^{T}q_t^\top g_{a,t}.
\]

Let \(\mathcal B\) be a finite comparator family. Its clairvoyant path-specific
oracle is

\[
O_{\mathcal B}(q_{1:T})
=
\min_{b\in\mathcal B}C_b(q_{1:T}).
\]

The regret of decision \(a\) on a path is

\[
R_a(q_{1:T})
=
C_a(q_{1:T})-O_{\mathcal B}(q_{1:T}).
\]

Every decision is required to belong to the comparator family. This guarantees

\[
R_a(q_{1:T})\ge0
\]

for every path.

All results below are finite-horizon, exact-rational, open-loop, and internal
to the declared cost and source-law model. They do not optimize a feedback
policy and do not imply that internal code lengths are parent-substrate
hardware costs.

---

## 1. Regret is convex piecewise linear in the complete path

Because the oracle is a minimum over affine costs,

\[
\begin{aligned}
R_a(q)
&=C_a(q)-\min_{b\in\mathcal B}C_b(q)\\
&=\max_{b\in\mathcal B}\left[C_a(q)-C_b(q)\right].
\end{aligned}
\]

Each difference \(C_a-C_b\) is affine in the complete free path vector.
Therefore

\[
\boxed{
R_a(q)
\text{ is convex and piecewise linear.}
}
\]

Now let the bounded-TV path polytope have vertices

\[
v^{(1)},\ldots,v^{(M)}.
\]

Every feasible path can be written as

\[
q=\sum_{j=1}^{M}\lambda_jv^{(j)},
\qquad
\lambda_j\ge0,
\quad
\sum_j\lambda_j=1.
\]

Convexity gives

\[
R_a(q)
\le
\sum_j\lambda_jR_a(v^{(j)})
\le
\max_jR_a(v^{(j)}).
\]

Thus

\[
\boxed{
\max_{q\text{ feasible}}R_a(q)
=
\max_jR_a(v^{(j)}).
}
\]

This is a different vertex argument from linear expectation maximization. The
regret objective is not linear, but its convex piecewise-linear structure is
sufficient.

---

## 2. Shared-randomness regret also reduces to path vertices

Suppose a source-independent common seed selects decision \(a\) with
probability \(x_a\). Every receiver knows the selected decision. The expected
cost on path \(q\) is

\[
C_x(q)
=
\sum_ax_aC_a(q),
\]

which is affine in \(q\). The mixture regret is

\[
\begin{aligned}
R_x(q)
&=C_x(q)-\min_bC_b(q)\\
&=\max_b\left[C_x(q)-C_b(q)\right].
\end{aligned}
\]

It is again convex piecewise linear, so

\[
\boxed{
\max_{q\text{ feasible}}R_x(q)
=
\max_jR_x(v^{(j)}).
}
\]

The continuous source-path game therefore becomes the finite rational matrix

\[
G_{ja}
=
C_a(v^{(j)})
-
\min_bC_b(v^{(j)}).
\]

The shared minimax regret is

\[
\boxed{
R_{\rm mix}
=
\min_{x\in\Delta}
\max_j
\sum_ax_aG_{ja}.
}
\]

The repository solves both the primal decision mixture and the dual
least-favorable path-vertex mixture by exact rational support enumeration and
requires a zero rational duality gap.

This assistance model is common randomness independent of the source path. If
the adversary can observe the realized seed and choose a different source path
for each realization, the benefit of mixing collapses to the best deterministic
regret.

---

## 3. Comparator classes are part of the theorem

Regret has no meaning until the oracle class is declared.

Let

\[
\mathcal B_1\subseteq\mathcal B_2.
\]

Then

\[
O_{\mathcal B_2}(q)
=
\min_{b\in\mathcal B_2}C_b(q)
\le
\min_{b\in\mathcal B_1}C_b(q)
=
O_{\mathcal B_1}(q).
\]

Therefore every fixed decision has weakly larger regret against the stronger
oracle:

\[
\boxed{
R_a^{\mathcal B_2}(q)
\ge
R_a^{\mathcal B_1}(q).
}
\]

Taking path maxima and then minimizing over the same decision class preserves
the inequality for deterministic and shared-randomness minimax regret.

For code sequences, the repository distinguishes:

- a decision switch budget \(B_D\);
- a comparator switch budget \(B_C\);
- one common declared switch penalty \(\kappa\).

It requires

\[
0\le B_D\le B_C\le T-1.
\]

This creates several non-equivalent regret notions:

- **static regret:** \(B_D=B_C=0\);
- **static-versus-dynamic regret:** \(B_D=0<B_C\);
- **bounded dynamic regret:** \(0<B_D\le B_C\);
- **fully switching open-loop regret:** \(B_D=B_C=T-1\).

A larger comparator budget is a stronger benchmark, not a more capable online
decision rule.

---

## 4. Regret is not the difference of robust values

Define the deterministic robust absolute value

\[
V_{\rm abs}^{\rm det}
=
\min_a\max_qC_a(q).
\]

Define the best and worst oracle costs

\[
O_{\min}
=
\min_qO(q),
\qquad
O_{\max}
=
\max_qO(q).
\]

For any fixed decision \(a\),

\[
\max_q[C_a(q)-O(q)]
\ge
\max_qC_a(q)-O_{\max},
\]

because at a path maximizing \(C_a\), the oracle cost is at most
\(O_{\max}\). Also,

\[
\max_q[C_a(q)-O(q)]
\le
\max_qC_a(q)-O_{\min}.
\]

Minimizing over \(a\) yields

\[
\boxed{
V_{\rm abs}^{\rm det}-O_{\max}
\le
R_{\rm det}
\le
V_{\rm abs}^{\rm det}-O_{\min}.
}
\]

The same proof applies to a shared mixture \(x\):

\[
\boxed{
V_{\rm abs}^{\rm mix}-O_{\max}
\le
R_{\rm mix}
\le
V_{\rm abs}^{\rm mix}-O_{\min}.
}
\]

The lower endpoint

\[
V_{\rm abs}-O_{\max}
\]

is sometimes called a value-of-clairvoyance or adaptivity gap. It is only a
lower bound on regret. The path maximizing decision cost need not be the path
maximizing oracle cost.

The repository computes both absolute-cost games independently and stores the
exact slack between regret and the lower value-gap bound.

---

## 5. Full-drift binary prediction has a closed solution

Consider two source states and horizon \(T\). At each period the decision chooses
one of two actions. Action zero has cost vector

\[
g_0=(0,1),
\]

and action one has

\[
g_1=(1,0).
\]

Thus the cost is one on the opposite pure state and zero on the matched pure
state.

Let \(\eta=1\). Every period law may be chosen independently from the complete
binary simplex. The decision family contains all \(2^T\) action sequences, and
the comparator family is identical.

### Deterministic value

For any precommitted sequence, the adversary chooses the opposite pure state in
every period. The decision cost is \(T\), while the clairvoyant comparator
matches every state and costs zero. Hence

\[
\boxed{R_{\rm det}=T.}
\]

### Shared-randomness value

For a decision mixture, let

\[
r_t=P(A_t=1).
\]

If the adversary chooses state zero at period \(t\), expected mismatch is
\(r_t\). If it chooses state one, expected mismatch is \(1-r_t\). Therefore

\[
\max\{r_t,1-r_t\}\ge\frac12.
\]

Summing over periods gives the lower bound

\[
R_{\rm mix}\ge\frac T2.
\]

Equality is achieved whenever every action marginal is balanced. For example,
mix the all-zero and all-one sequences with probability one half each. Thus

\[
\boxed{R_{\rm mix}=\frac T2.}
\]

Only two shared-seed outcomes are needed, even though the complete decision
class has \(2^T\) sequences.

### Why robust value subtraction fails sharply

For this example,

\[
V_{\rm abs}^{\rm det}=T,
\qquad
O_{\max}=\frac T2,
\]

so the deterministic value-gap lower bound is \(T/2\), while actual regret is
\(T\).

For shared decisions,

\[
V_{\rm abs}^{\rm mix}=\frac T2
=
O_{\max}.
\]

The difference of robust values is therefore zero even though

\[
R_{\rm mix}=\frac T2.
\]

This is an exact counterexample to reporting regret as

\[
\min_x\max_q C_x(q)
-
\max_q\min_b C_b(q).
\]

---

## 6. Zero-error code-sequence regret

Let the confusion graph define a bounded complete universe of deterministic
zero-error binary-prefix codebooks. Pure-state prior scenarios make each
candidate's scenario-cost vector equal to its state-length vector.

A code sequence

\[
a=(a_1,\ldots,a_T)
\]

has path cost

\[
C_a(q)
=
\sum_{t=1}^{T}q_t^\top\ell_{a_t}
+
\kappa
\sum_{t=2}^{T}\mathbf1\{a_t\ne a_{t-1}\}.
\]

The same switch penalty is used for the comparator. This prevents regret from
being manufactured by charging unequal accounting rules to the decision and
oracle.

The bounded exact solver:

1. enumerates the componentwise-undominated deterministic codebook universe;
2. enumerates every decision sequence below \(B_D\);
3. enumerates every comparator sequence below \(B_C\);
4. enumerates the exact bounded-TV path-polytope vertices;
5. computes the oracle cost at every path vertex;
6. constructs the regret matrix;
7. solves deterministic minimax regret;
8. solves the shared-randomness primal and dual games exactly.

Componentwise codebook dominance remains safe here. If codebook \(c'\) is no
longer than \(c\) in every state, replacing every occurrence of \(c\) by
\(c'\) cannot increase path cost. Replacing all occurrences also cannot increase
switch count: boundaries against unrelated codebooks remain switches, while
boundaries against \(c'\) may merge.

---

## 7. Timing hierarchy

The following objects should not be conflated:

1. **Robust absolute decision**

   \[
   \min_a\max_qC_a(q).
   \]

2. **Open-loop minimax regret**

   \[
   \min_a\max_q[C_a(q)-O(q)].
   \]

3. **Shared-open-loop minimax regret**

   \[
   \min_x\max_q[C_x(q)-O(q)].
   \]

4. **Clairvoyant comparator**

   \[
   O(q)=\min_bC_b(q).
   \]

5. **Causal feedback policy**

   A policy whose period-\(t\) decision depends only on observations available
   before period \(t\).

The current lane implements the first four. It does **not** implement item five.
A causal policy requires an observation model and an explicit move order:

- does the policy observe the exact previous source law or only sampled states?
- is the next codebook selected before or after the source chooses \(q_t\)?
- does the source observe private or common randomness?
- is the switching state itself observable?
- are observations censored by the selected codebook?

Changing those answers changes the extensive-form game.

---

## 8. Relevance to on-demand simulation arguments

A hypothetical on-demand renderer may face a changing distribution over future
queries or observations. Several distinct engineering objectives then appear:

- minimize worst absolute compute or communication;
- minimize regret relative to a path-specific representation oracle;
- limit reconfiguration frequency;
- use source-independent common randomness to diversify representations;
- adapt causally to observed drift.

The mathematical results show that these objectives are not interchangeable.
In particular:

- a design can have a small robust absolute value but large pathwise regret;
- comparator power must be declared;
- shared randomness can reduce open-loop regret without providing feedback;
- source drift couples time periods, so independent one-period analyses may be
  invalid;
- internal coding regret is not evidence that reality is simulated.

An exact simulator governed by the declared model can satisfy these bounds. The
results constrain only architectures using the specified finite predictive and
communication interface.

---

## Nonclaims

- The pathwise oracle is not an implementable online policy; it observes the
  complete path before choosing.
- Shared randomness is assumed independent of the source path and known to all
  required decoders.
- The finite comparator class is declared rather than derived from all possible
  algorithms.
- Switch penalties are rational design inputs, not inferred physical costs.
- Bounded active-basis, code, sequence, and game enumeration is not a
  polynomial-time scalability theorem.
- Vertex reduction relies on affine path costs and a finite comparator family.
- The source path represents a sequence of categorical laws, not necessarily a
  physically realizable cosmological process.
- Dynamic regret, robust cost, queueing delay, peak bandwidth, energy, and
  parent-substrate memory are different quantities.
- None of these regret identities constitutes evidence for simulation.

---

## Next research targets

1. Exact finite causal-feedback games with move order made explicit.
2. Partial observation where the code selector sees samples rather than the
   exact source law.
3. Belief-state filtering under hidden drift.
4. Feedback policies with shared and private randomness separated.
5. Path-dependent or state-dependent switching costs.
6. Comparator classes defined by total variation, switch count, or cumulative
   path length rather than only a hard switch budget.
7. Strongly adaptive regret over every time interval.
8. Multi-letter coding where source drift and block coding interact.
9. A general extensive-form certificate format distinguishing open-loop,
   causal, and clairvoyant information sets.
