# Bell-derived predictive-state lower bounds

## Scope

This note derives state-memory and query-complexity bounds from one explicit physical family: two-qubit Werner/singlet correlations under a finite set of coplanar projective measurements.

It does **not** claim that quantum mechanics implies simulation, that a parent substrate must implement this family in any particular way, or that the bounds below constrain an unrestricted simulator. The results constrain any internal online representation that must reproduce the declared Bell experiment family to the stated accuracy.

## 1. Physical family

Let Alice choose angle \(\alpha_x\), Bob choose angle \(\beta_y\), and outcomes be \(a,b\in\{-1,+1\}\). For visibility \(v\in[0,1]\), define

\[
P_v(a,b\mid x,y)
=\frac14\left[1-ab\,v\cos(\alpha_x-\beta_y)\right].
\]

This is the standard singlet correlation law with white-noise visibility parameter \(v\). Marginals are uniform and

\[
\mathbb E_v[AB\mid x,y]
=-v\cos(\alpha_x-\beta_y).
\]

For the canonical CHSH angles

\[
\alpha_0=0,\qquad \alpha_1=\frac\pi2,
\]

\[
\beta_0=\frac\pi4,\qquad \beta_1=-\frac\pi4,
\]

the absolute CHSH value is

\[
|S|=2\sqrt2\,v.
\]

Thus this family crosses the local-hidden-variable CHSH threshold at

\[
v=1/\sqrt2.
\]

The threshold is a property of this restricted physical model; it is not evidence for or against simulation.

## 2. Exact predictive-law geometry

Assume a fixed probability \(w_{xy}\) of querying setting pair \((x,y)\), with \(\sum_{xy}w_{xy}=1\). Define

\[
C=\sum_{xy}w_{xy}\left|\cos(\alpha_x-\beta_y)\right|.
\]

Let \(P_v\) denote the joint law of the randomly selected setting pair and its outcomes.

### Theorem 1: exact TV distance

For any \(u,v\in[0,1]\),

\[
\boxed{
\operatorname{TV}(P_v,P_u)
=\frac{|v-u|}{2}C.
}
\]

### Proof

For one fixed pair \((x,y)\), let \(c_{xy}=\cos(\alpha_x-\beta_y)\). Then

\[
P_v(a,b\mid x,y)-P_u(a,b\mid x,y)
=-\frac14ab(v-u)c_{xy}.
\]

Every one of the four outcomes therefore has absolute difference

\[
\frac14|v-u||c_{xy}|.
\]

The conditional \(\ell_1\) distance is

\[
|v-u||c_{xy}|,
\]

so conditional total variation is

\[
\frac12|v-u||c_{xy}|.
\]

Because the setting distribution is identical under both hypotheses, joint total variation is the weighted sum over settings:

\[
\operatorname{TV}(P_v,P_u)
=\sum_{xy}w_{xy}\frac12|v-u||c_{xy}|
=\frac{|v-u|}{2}C.
\]

QED.

For the uniform canonical CHSH schedule, every \(|c_{xy}|=1/\sqrt2\), hence

\[
C=\frac1{\sqrt2}
\]

and

\[
\operatorname{TV}(P_v,P_u)
=\frac{|v-u|}{2\sqrt2}.
\]

The implementation checks this formula against direct enumeration of all 16 setting/outcome atoms across multiple visibility grids.

## 3. Physically derived state-memory lower bound

Suppose an online renderer stores a finite internal state \(Z\). For every allowed hidden physical history indexed by visibility \(v_i\), it must output a future Bell predictive law \(Q_{Z_i}\) satisfying

\[
\operatorname{TV}(Q_{Z_i},P_{v_i})\le \epsilon.
\]

If two target laws satisfy

\[
\operatorname{TV}(P_{v_i},P_{v_j})>2\epsilon,
\]

then one renderer state cannot represent both, because otherwise the triangle inequality would imply

\[
\operatorname{TV}(P_{v_i},P_{v_j})
\le
\operatorname{TV}(P_{v_i},Q_Z)
+
\operatorname{TV}(Q_Z,P_{v_j})
\le 2\epsilon,
\]

a contradiction.

Therefore every pairwise \(2\epsilon\)-separated subset of candidate visibility values requires distinct renderer states.

Using Theorem 1, separation is exactly

\[
|v_i-v_j|>\frac{4\epsilon}{C}.
\]

If a finite visibility grid contains a maximum packing of cardinality \(K\), then

\[
\boxed{|\mathcal Z|\ge K}
\]

and therefore

\[
\boxed{\text{memory bits}\ge\lceil\log_2K\rceil.}
\]

This is the first repository lower bound whose metric geometry is derived from a concrete physical experiment rather than supplied as an arbitrary collection of probability vectors.

## 4. Query geometry and Fisher information

For one setting pair define

\[
c=\cos(\alpha-\beta).
\]

Direct evaluation of the score gives

\[
\boxed{
I_v(c)=\frac{c^2}{1-v^2c^2}
}
\]

for interior regular points. For a randomized schedule,

\[
I_v=\sum_{xy}w_{xy}\frac{c_{xy}^2}{1-v^2c_{xy}^2}.
\]

Consequently, under the regular unbiased-estimator conditions of the Cramer-Rao theorem, \(n\) independent trials obey

\[
\boxed{
\operatorname{Var}(\hat v)\ge\frac1{nI_v}.
}
\]

This establishes a local estimation lower bound for the same physical parameter that defines the predictive-state packing.

For canonical CHSH settings, \(c_{xy}^2=1/2\) for every pair, so

\[
I_v=\frac{1/2}{1-v^2/2}.
\]

## 5. Adaptive-query distinguishability bound

An interrogator may choose the next allowed setting pair adaptively based on all previous settings and outcomes. Let

\[
D_{xy}(v\Vert u)
=D_{\mathrm{KL}}\left(
P_v(A,B\mid x,y)
\Vert
P_u(A,B\mid x,y)
\right)
\]

and

\[
D_{\max}(v\Vert u)=\max_{x,y}D_{xy}(v\Vert u).
\]

Even under an adaptive policy, the KL chain rule yields

\[
D_{\mathrm{KL}}(P_v^{(n)}\Vert P_u^{(n)})
\le nD_{\max}(v\Vert u),
\]

because each conditional contribution is at most the best one-step KL available among allowed queries.

Pinsker then gives

\[
\operatorname{TV}(P_v^{(n)},P_u^{(n)})
\le
\sqrt{\frac{nD_{\max}(v\Vert u)}2}.
\]

Therefore achieving transcript separation at least \(\delta\) requires

\[
\boxed{
n\ge \frac{2\delta^2}{D_{\max}(v\Vert u)}.
}
\]

The implementation returns the ceiling of this quantity. It is a **necessary, not sufficient**, number of trials.

This result matters for lazy-rendering discussions because adaptivity alone does not make arbitrarily close physical states instantly distinguishable. The transcript can accumulate information only at a rate bounded by the most informative allowed query.

## 6. What this establishes and what it does not

Established within the declared model:

1. the exact total-variation geometry of a finite Bell experiment family;
2. a visibility-grid packing number induced by that physical geometry;
3. a corresponding renderer-state and memory lower bound;
4. a closed-form Fisher-information geometry;
5. an adaptive KL/Pinsker necessary-query lower bound.

Not established:

- that the universe uses lazy rendering;
- that a simulator stores a classical finite state;
- that parent memory is measured in our bits;
- that the Werner family spans all relevant quantum histories;
- that Bell violation is evidence for simulation;
- that an unrestricted simulator is distinguishable at all.

## 7. Next extension

The one-parameter visibility family has simple one-dimensional geometry. The next meaningful extension is a finite family with multiple hidden predictive degrees of freedom, such as:

- Bell states with unknown phase plus visibility;
- finite stabilizer-state families with adaptive Pauli queries;
- delayed-choice circuits where early records constrain later compatible measurements;
- distributed causal networks with independently stored transcripts.

Those families can produce genuinely multidimensional packing numbers and stronger state-complexity lower bounds.