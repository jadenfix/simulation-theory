# Distributionally robust zero-error coding over total-variation prior balls

## Scope

The prior-weighted coding lane optimizes a zero-error binary prefix code for one
exact source prior. The finite-prior robust lane protects against a finite list
of priors and, by linearity, their convex hull.

This lane studies a genuinely continuous uncertainty set. Fix a nominal rational
prior

\[
p=(p_1,\ldots,p_n)\in\Delta_{n-1}
\]

and a total-variation radius

\[
\rho\in[0,1]\cap\mathbb Q.
\]

The possible source law is any

\[
q\in\mathcal U_{\mathrm{TV}}(p,\rho)
=
\left\{
q\in\Delta_{n-1}:
\operatorname{TV}(q,p)\le\rho
\right\}.
\]

For a fixed state-value vector \(f\), the inner problem is

\[
\sup_{q\in\mathcal U_{\mathrm{TV}}(p,\rho)}E_q[f]
\]

or its minimum analogue. For coding, \(f_i\) is the codeword length assigned to
source state \(i\).

The branch proves that the continuous inner problem has an exact rational
mass-transport solution. It then composes that exact solution with exhaustive
bounded enumeration of every proper confusion-graph partition and every
complete binary prefix shape.

The resulting claims are finite, one-shot, deterministic, rational,
binary-prefix, common-message, and zero-error. They do not cover prior learning,
time-varying source processes, allowed decoding error, block graph products,
queueing, hard edge capacity, quantum variable-length coding, or parent-level
physical resources. They are not evidence for simulation.

---

## 1. Total variation as moved probability mass

For probability vectors \(p,q\) on the same finite state set,

\[
\operatorname{TV}(p,q)
=
\frac12\sum_i|p_i-q_i|.
\]

Because both vectors sum to one,

\[
\sum_i(q_i-p_i)=0.
\]

Therefore the total positive and negative deviations agree:

\[
\boxed{
\operatorname{TV}(p,q)
=
\sum_i(q_i-p_i)_+
=
\sum_i(p_i-q_i)_+.
}
\]

Total variation is exactly the amount of probability mass removed from donor
states and reallocated to recipient states.

Let

\[
d_i=(p_i-q_i)_+,
\qquad
r_j=(q_j-p_j)_+.
\]

Then

\[
\sum_i d_i
=
\sum_j r_j
=
\operatorname{TV}(p,q).
\]

Any feasible donor and recipient marginals with equal total mass can be coupled
by a finite transport matrix \(m_{ij}\ge0\) satisfying

\[
\sum_jm_{ij}=d_i,
\qquad
\sum_im_{ij}=r_j.
\]

The expectation change is

\[
E_q[f]-E_p[f]
=
\sum_{i,j}m_{ij}(f_j-f_i).
\]

This identity converts the continuous distribution problem into an ordered
mass-transfer problem.

---

## 2. Exact extremal expectation theorem

Sort donor states by increasing value and recipient states by decreasing value.
To maximize expectation, repeatedly move as much mass as possible from the
currently shortest-valued donor to the currently longest-valued recipient. Stop
when:

- the TV budget is exhausted;
- all profitable donor mass is exhausted; or
- no recipient has strictly larger value than the current donor.

To minimize expectation, reverse the value order.

### Exchange proof

Consider any feasible transport containing positive mass on two transfers

\[
i\to j,
\qquad
k\to \ell
\]

with

\[
f_i\le f_k,
\qquad
f_j\le f_\ell.
\]

If the lower donor is paired with the lower recipient and the higher donor with
the higher recipient, exchange an amount \(\delta\) to use

\[
i\to\ell,
\qquad
k\to j.
\]

The change in objective is

\[
\begin{aligned}
&\delta[(f_\ell-f_i)+(f_j-f_k)]
-
\delta[(f_j-f_i)+(f_\ell-f_k)]\\
&=0.
\end{aligned}
\]

Thus crossings can be uncrossed without changing the objective. More directly,
for fixed donor mass, every unit should be placed at the largest available
recipient value; for fixed recipient demand, it should be taken from the
smallest available donor value. Any transfer that leaves available lower-valued
donor mass while using a higher-valued donor, or leaves available
higher-valued recipient capacity while using a lower-valued recipient, admits a
strictly improving exchange.

The greedy transport therefore satisfies the necessary monotone support pattern
of an optimum, and every omitted transfer has no larger value gap than the
active frontier. This proves optimality.

### Exact theorem

Let the greedy transfers be

\[
(i_t,j_t,m_t),
\qquad t=1,\ldots,T.
\]

Then

\[
\boxed{
\sup_{\operatorname{TV}(q,p)\le\rho}E_q[f]
=
E_p[f]
+
\sum_{t=1}^Tm_t(f_{j_t}-f_{i_t}).
}
\]

The minimum is obtained by reversing the value ordering:

\[
\boxed{
\inf_{\operatorname{TV}(q,p)\le\rho}E_q[f]
=
E_p[f]
+
\sum_{t=1}^{T'}m_t(f_{j_t}-f_{i_t}),
}
\]

where every active value gap is nonpositive.

For rational \(p,f,\rho\), every transfer mass and both extremal distributions
are rational. No floating optimizer or discretization is needed.

---

## 3. Saturation radius

For maximization, once all probability is concentrated on maximum-value states,
no further increase is possible. Let

\[
M=\{i:f_i=f_{\max}\}.
\]

The nominal mass already on the maximum set is

\[
p(M)=\sum_{i\in M}p_i.
\]

The amount that must be moved to reach the maximum face is

\[
\boxed{
\rho_{\mathrm{sat}}^{\max}
=1-p(M).
}
\]

Therefore the greedy transport uses exactly

\[
\boxed{
\min\{\rho,\rho_{\mathrm{sat}}^{\max}\}
}

mass. For larger radii, the optimum remains

\[
f_{\max}.
\]

Similarly, if

\[
m=\{i:f_i=f_{\min}\},
\]

then

\[
\boxed{
\rho_{\mathrm{sat}}^{\min}
=1-p(m)
}
\]

and the minimum expectation saturates at \(f_{\min}\).

A TV ball may contain distributions farther from \(p\) than the extremizer. The
constraint is an inequality, so unused radius is not a defect.

---

## 4. Range bound and its exact tightness window

For any transport of mass at most \(\rho\), every unit changes value by at most

\[
f_{\max}-f_{\min}.
\]

Hence

\[
\boxed{
|E_q[f]-E_p[f]|
\le
\operatorname{TV}(q,p)
\bigl(f_{\max}-f_{\min}\bigr).
}
\]

In particular,

\[
\sup_{\operatorname{TV}(q,p)\le\rho}E_q[f]
\le
E_p[f]+ho\operatorname{range}(f),
\]

and

\[
\inf_{\operatorname{TV}(q,p)\le\rho}E_q[f]
\ge
E_p[f]-ho\operatorname{range}(f).
\]

The bound is exactly tight while probability can be moved directly from a
minimum-value state to a maximum-value state. For maximization, define

\[
p_{\min}=p\{i:f_i=f_{\min}\},
\]

and maximum-face capacity

\[
1-p\{i:f_i=f_{\max}\}.
\]

Then full-range tightness holds for

\[
\boxed{
0\le\rho
\le
\rho_{\mathrm{range}}^{\max}
=
\min\left\{
p_{\min},
1-p\{f=f_{\max}\}
\right\}.
}
\]

After minimum-valued donor mass is exhausted, the marginal slope falls to the
next value gap. The minimum analogue reverses maximum and minimum.

---

## 5. Piecewise-linear robust expectation profile

The exact transport order gives a complete profile in the radius.

For maximization, each active donor level contributes a segment whose slope is

\[
f_{\max}-f_{\mathrm{donor}}.
\]

As lower-valued donor mass is exhausted, donor values rise and slopes weakly
decrease. Therefore

\[
\boxed{
\rho\mapsto
\sup_{\operatorname{TV}(q,p)\le\rho}E_q[f]
}
\]

is nondecreasing, concave, continuous, and piecewise linear.

The minimization profile is nonincreasing, convex, continuous, and piecewise
linear. Its slopes weakly increase toward zero.

The checker returns every exact segment:

- start and end radius;
- start expectation;
- rational marginal slope;
- exact end expectation.

Equal-slope adjacent transport segments are merged without changing the
function.

---

## 6. Total-variation balls versus Huber contamination

A Huber contamination neighborhood has the form

\[
q=(1-\epsilon)p+\epsilon r,
\qquad
r\in\Delta_{n-1}.
\]

For a fixed value vector,

\[
E_q[f]
=(1-\epsilon)E_p[f]+\epsilon E_r[f].
\]

Thus

\[
\boxed{
\sup_rE_q[f]
=(1-\epsilon)E_p[f]+\epsilon f_{\max},
}
\]

and

\[
\boxed{
\inf_rE_q[f]
=(1-\epsilon)E_p[f]+\epsilon f_{\min}.
}
\]

Moreover,

\[
\operatorname{TV}(q,p)
=
\epsilon\operatorname{TV}(r,p)
\le
\epsilon.
\]

Therefore the Huber set is contained in the TV ball of the same numerical
radius:

\[
\boxed{
\mathcal U_{\mathrm{Huber}}(p,\epsilon)
\subseteq
\mathcal U_{\mathrm{TV}}(p,\epsilon).
}
\]

The inclusion is generally strict. Huber contamination scales down every
nominal coordinate before adding a replacement law. A TV adversary can instead
remove all of its budget from whichever states are most favorable and move it
directly to the worst state.

The two robustness models must not be used interchangeably merely because both
have a parameter named \(\epsilon\).

---

## 7. Outer zero-error coding problem

Let \(G\) be the finite confusion graph. Every deterministic zero-error binary
prefix code is represented by:

1. a proper independent-set partition \(\mathcal P\);
2. a complete binary prefix shape with class lengths \(\ell_j\).

The induced state-length vector is

\[
\ell(x)=\ell_j
\qquad
x\in C_j.
\]

For one code \(c\), define its robust TV cost

\[
R_\rho(c)
=
\sup_{\operatorname{TV}(q,p)\le\rho}
E_q[\ell_c].
\]

The exact deterministic distributionally robust code value is

\[
\boxed{
V_{\mathrm{TV}}(G,p,\rho)
=
\min_{c\in\mathcal C(G)}R_\rho(c).
}
\]

Below explicit caps, the checker exhausts every proper partition and every
complete prefix shape. Codebooks inducing the same state-length vector are
equivalent for every prior and every TV radius, so one canonical representative
is retained.

For each candidate the certificate records:

- nominal expected length;
- exact worst-case distribution and expectation;
- exact best-case distribution and expectation;
- transfer receipts;
- maximum codeword length;
- message count and proper partition.

The selected robust code minimizes, in order:

1. worst-case expectation;
2. nominal expectation;
3. peak length;
4. message count;
5. canonical state-length and partition order.

The tie-break does not alter the robust optimum; it makes certificates stable.

---

## 8. Price of robustness decomposition

Let

\[
L^*(G,p)
=
\min_cE_p[\ell_c]
\]

be the nominal prior-weighted optimum, and let \(c_\rho^*\) be a selected
TV-robust optimum.

The total gap is

\[
V_{\mathrm{TV}}(G,p,\rho)-L^*(G,p).
\]

It decomposes exactly as

\[
\boxed{
V_{\mathrm{TV}}-L^*
=
\underbrace{E_p[\ell_{c_\rho^*}]-L^*}_{\text{price of robustness}}
+
\underbrace{
\sup_{q\in\mathcal U}E_q[\ell_{c_\rho^*}]
-E_p[\ell_{c_\rho^*}]
}_{\text{uncertainty uplift}}.
}
\]

The first term is the nominal performance sacrificed by selecting a robust code.
The second is the adversarial shift against that selected code.

A code can have zero price of robustness but positive uplift when the nominal
optimum remains robust-optimal at small radius. At larger radius the selected
code can switch to a more balanced tree, producing positive price of robustness
but a smaller or zero uplift.

---

## 9. Radius monotonicity

For

\[
0\le\rho_1\le\rho_2\le1,
\]

we have

\[
\mathcal U_{\mathrm{TV}}(p,\rho_1)
\subseteq
\mathcal U_{\mathrm{TV}}(p,\rho_2).
\]

Thus every fixed code satisfies

\[
R_{\rho_1}(c)
\le
R_{\rho_2}(c).
\]

Taking the minimum across codes preserves the inequality:

\[
\boxed{
V_{\mathrm{TV}}(G,p,\rho_1)
\le
V_{\mathrm{TV}}(G,p,\rho_2).
}
\]

The robust value is the lower envelope of finitely many continuous concave
piecewise-linear fixed-code profiles. The envelope is continuous and
nondecreasing, but it need not itself be concave: code switches can create
slope increases. This distinction matters when interpreting robustness curves.

---

## 10. Radius-zero endpoint

At radius zero,

\[
\mathcal U_{\mathrm{TV}}(p,0)=\{p\}.
\]

Therefore

\[
R_0(c)=E_p[\ell_c]
\]

for every code, and

\[
\boxed{
V_{\mathrm{TV}}(G,p,0)=L^*(G,p).
}
\]

The distributionally robust solver reduces exactly to the prior-weighted nominal
solver, not merely asymptotically as \(\rho\to0\).

---

## 11. Radius-one endpoint and peak coding

Every pair of finite probability distributions has TV distance at most one.
Hence

\[
\mathcal U_{\mathrm{TV}}(p,1)=\Delta_{n-1}.
\]

For a fixed state-length vector,

\[
\sup_{q\in\Delta_{n-1}}E_q[\ell]
=
\max_i\ell_i.
\]

Thus radius-one robust coding minimizes the maximum state length:

\[
V_{\mathrm{TV}}(G,p,1)
=
\min_{c\in\mathcal C(G)}\max_i\ell_c(i).
\]

A prefix code with maximum length \(d\) has at most \(2^d\) leaves, so a
zero-error code with at least \(\chi(G)\) messages requires

\[
d\ge\left\lceil\log_2\chi(G)\right\rceil.
\]

Conversely, let

\[
b=\left\lceil\log_2\chi(G)\right\rceil.
\]

Begin with \(2^{b-1}\) leaves at depth \(b-1\), and expand exactly

\[
\chi(G)-2^{b-1}
\]

of them. This produces a full binary tree with \(\chi(G)\) leaves, all of depth
at most \(b\). Assign those leaves to a minimum coloring.

Therefore

\[
\boxed{
V_{\mathrm{TV}}(G,p,1)
=
\left\lceil\log_2\chi(G)\right\rceil.
}
\]

The full TV radius connects expected source coding continuously to the hard
peak prefix-length problem.

---

## 12. Skew K4 exact fixed-code transport

Let \(G=K_4\), nominal prior

\[
p=
\left(
\frac7{10},
\frac1{10},
\frac1{10},
\frac1{10}
\right),
\]

and state lengths

\[
\ell=(1,2,3,3).
\]

The nominal expectation is

\[
E_p[\ell]=\frac32.
\]

At radius

\[
\rho=\frac1{10},
\]

the maximizing adversary moves \(1/10\) mass from the length-one state to a
length-three state:

\[
\boxed{
\sup E_q[\ell]
=
\frac32+rac1{10}(3-1)
=
\frac{17}{10}.
}
\]

The minimizing adversary moves the same mass from a length-three state to the
length-one state:

\[
\boxed{
\inf E_q[\ell]
=
\frac32-rac1{10}(3-1)
=
\frac{13}{10}.
}
\]

The worst profile has slopes:

\[
2
\quad\text{for }0\le\rho\le\frac7{10},
\]

then

\[
1
\quad\text{for }\frac7{10}\le\rho\le\frac45,
\]

then zero. It saturates at expectation three.

The best profile reaches expectation one at radius \(3/10\) and then remains
constant.

---

## 13. Huber and TV separation on skew K4

For the same nominal prior and lengths, use Huber contamination fraction

\[
\epsilon=\frac1{10}.
\]

Putting the contamination law on a length-three state yields

\[
\begin{aligned}
E_{\mathrm{Huber}}[\ell]
&=
\frac9{10}\cdot\frac32
+
\frac1{10}\cdot3\\
&=
\boxed{\frac{33}{20}}.
\end{aligned}
\]

Its actual TV distance from the nominal prior is

\[
\frac9{100},
\]

because the chosen contamination state already has nominal mass \(1/10\).

The full radius-\(1/10\) TV ball allows the more targeted transfer and reaches

\[
\frac{17}{10}>rac{33}{20}.
\]

This finite example shows concretely that equal numerical radii do not define
equal uncertainty sets.

---

## 14. Skew K4 robust-code phase change

For \(K_4\), the nominal-optimal unbalanced tree has lengths

\[
(1,2,3,3)
\]

and robust profile, before its first slope change,

\[
\frac32+2\rho.
\]

The balanced tree

\[
(2,2,2,2)
\]

has robust cost exactly two for every radius.

They meet when

\[
\frac32+2\rho=2,
\]

so

\[
\boxed{
\rho_c=\frac14.
}
\]

The exact robust value is

\[
\boxed{
V_{\mathrm{TV}}(K_4,p,\rho)
=
\begin{cases}
\frac32+2\rho,&0\le\rho\le\frac14,\\
2,&\frac14\le\rho\le1.
\end{cases}
}
\]

At the exact tie, the deterministic certificate's secondary nominal-cost
criterion retains the unbalanced tree. For any radius above \(1/4\), the balanced
tree is strictly robust-better.

Below the switch, price of robustness is zero and all robust gap is uncertainty
uplift. Above the switch, the selected balanced tree has nominal sacrifice
\(1/2\) and zero uncertainty uplift.

---

## 15. Bounded certificate and independent checks

The implementation returns:

- exact nominal prior and radius;
- exact state-value or state-length vector;
- exact extremal distributions;
- every donor-recipient transfer and rational mass;
- nominal and extremal expectations;
- TV distance, moved mass, unused radius, and saturation radius;
- full-range tightness radius and range-bound slack;
- exact piecewise-linear profile segments;
- a Huber contamination certificate;
- every proper coding partition and complete prefix-shape search cap;
- raw and distinct state-length candidate counts;
- exact nominal optimum and hard peak optimum;
- selected robust code, best- and worst-case laws;
- price of robustness, uncertainty uplift, and total robust gap;
- radius-zero and radius-one endpoint checks.

Independent tests:

1. compare exact transport against every rational denominator-ten distribution
   on forty seeded four-state instances;
2. verify exact K4 worst and best transfer receipts;
3. verify piecewise slopes and saturation;
4. distinguish Huber contamination from the full TV ball;
5. verify the exact \(\rho=1/4\) robust-code phase change;
6. verify radius-zero and radius-one endpoints on a nontrivial five-vertex graph;
7. independently enumerate every coloring, complete prefix shape, and feasible
   denominator-ten adversarial distribution on all sixty-four labeled
   four-vertex graphs;
8. verify radius monotonicity and sign symmetry;
9. fail closed on inexact priors, invalid radii, and exceeded candidate caps.

---

## 16. Boundaries and next questions

This lane does not establish:

- a confidence region for an empirically estimated prior;
- optional-stopping or time-uniform prior uncertainty;
- KL, chi-square, Wasserstein, moment, or general polyhedral ambiguity sets;
- shared-randomness minimax over a continuous TV ball;
- minimax regret over a continuous ball;
- allowed-error coding or Bayes-risk tradeoffs;
- block coding, graph products, or asymptotic graph entropy;
- queueing delay or hard network cut feasibility from expected length;
- prior drift, source dependence, or online universal adaptation;
- parent-substrate costs or evidence for simulation.

The next mathematically natural extensions are:

1. shared-randomness codebook games against a continuous TV adversary;
2. exact robust LP duals for arbitrary rational polyhedral prior sets;
3. KL-ball inner optimization with certified transcendental bounds rather than
   unchecked floating optimization;
4. finite-sample confidence sets that feed directly into the robust code
   designer;
5. allowed-error confusion hypergraphs, where the unweighted zero-error graph
   no longer contains the full risk information.
