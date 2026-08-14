# Observed-law dynamic coding under adversarial drift

## Scope

The coupled open-loop result fixes an entire codebook sequence before the source
law moves. This note changes one assumption only:

> At the beginning of each period, the current source law is observed exactly
> before the next zero-error prefix codebook is selected.

After the current period cost is paid, an adversary chooses the next source law
from a declared finite transition relation.

This is a fully observed finite minimax control problem. It is not the same as:

- inferring a law from finite samples;
- choosing a code before seeing the current law;
- observing only the realized source symbol;
- partial-observation or belief-state control;
- a continuous-law dynamic program.

The distinction is central because the value of feedback comes from the timing
and content of the observation.

---

## 1. Finite law-state model

Let

\[
\mathcal Q=\{q^{(1)},\ldots,q^{(m)}\}
\subseteq\Delta_{n-1}
\]

be a declared finite set of exact rational source laws. Let

\[
\Gamma(i)\subseteq\{1,\ldots,m\}
\]

be the nonempty set of source-law states reachable after the current period.
The relation may be directed.

A useful constructor declares

\[
j\in\Gamma(i)
\iff
\operatorname{TV}(q^{(i)},q^{(j)})\le\eta.
\]

This is exact for the finite state set. It is not an exact solution of the
continuous TV ball unless the declared finite set itself is the intended model.

Let \(\mathcal C\) be the complete bounded deterministic zero-error binary
prefix-code universe after safe componentwise length-dominance pruning. Code
\(c\) has state-length vector

\[
\ell_c\in\mathbb Z_{\ge0}^{n}.
\]

Changing from code \(c^-\) to \(c\) incurs nonnegative rational penalty

\[
\kappa\mathbf 1\{c\ne c^-\}.
\]

The first period has no previous code and pays no switching penalty.

---

## 2. Fully observed Bellman theorem

At period \(t\), the order is:

1. the current law state \(i_t\) is observed;
2. the minimizing coder chooses code \(c_t\);
3. stage cost is paid;
4. the maximizing adversary chooses
   \(i_{t+1}\in\Gamma(i_t)\).

For terminal period \(T\),

\[
V_T(i,c^-)
=
\min_{c\in\mathcal C}
\left[
(q^{(i)})^\top\ell_c
+
\kappa\mathbf1\{c\ne c^-\}
\right].
\]

For \(t<T\), backward induction gives

\[
\boxed{
V_t(i,c^-)
=
\min_{c\in\mathcal C}
\left[
(q^{(i)})^\top\ell_c
+
\kappa\mathbf1\{c\ne c^-\}
+
\max_{j\in\Gamma(i)}V_{t+1}(j,c)
\right].
}
\]

### Proof

Assume the continuation values at \(t+1\) equal the minimax values of every
remaining subgame. Once \((i,c^-)\) is given, the coder selects one current
code. The current stage cost is then fixed. The adversary selects a reachable
next law, and by the induction hypothesis the remaining value is
\(V_{t+1}(j,c)\). Thus the adversary selects the maximum continuation and the
coder selects the minimum complete action value. The terminal expression is
the same argument without continuation. Backward induction proves the result.

The implementation stores the complete value table, minimizing code witness,
and maximizing successor witness for every

\[
(t,i,c^-).
\]

Validation replays every Bellman equality exactly over rational arithmetic.

---

## 3. Open-loop benchmark

An open-loop sequence

\[
c_{1:T}
\]

is fixed before the source path. For a declared sequence, define

\[
W_T(i)
=
(q^{(i)})^\top\ell_{c_T}
+
\kappa\mathbf1\{c_T\ne c_{T-1}\},
\]

and for \(t<T\),

\[
W_t(i)
=
(q^{(i)})^\top\ell_{c_t}
+
\kappa\mathbf1\{c_t\ne c_{t-1}\}
+
\max_{j\in\Gamma(i)}W_{t+1}(j).
\]

The exact open-loop value is

\[
\boxed{
V_{\rm OL}
=
\min_{c_{1:T}}W_1(i_1).
}
\]

The repository exhausts all code sequences below a declared cap and stores an
attaining adversarial law path.

---

## 4. Value of observing the current law

Every open-loop sequence defines a feedback policy that ignores its observation
and plays the predeclared code at each time. Therefore the fully observed policy
class contains the open-loop class.

For a minimizing coder,

\[
\boxed{
V_{\rm FB}
\le
V_{\rm OL}.
}
\]

Define

\[
\boxed{
\mathcal V_{\rm obs}
=
V_{\rm OL}-V_{\rm FB}
\ge0.
}
\]

This is the value of the **declared exact law observation** under the declared
transition game. It is not the value of one sample, one source symbol, or an
estimated empirical law.

---

## 5. Exact mobile-K3 separation

Consider complete confusion on three source symbols. The deterministic complete
binary prefix codes have state-length vectors given by permutations of

\[
(1,2,2).
\]

Let the finite law states be the three point masses

\[
e_1,e_2,e_3,
\]

and allow every law to transition to every law. Start at \(e_1\) and use a
two-period horizon.

### Open-loop

The first code can assign its short leaf to state one, giving first-period cost
one. The second code is already known to the adversary. Whichever state receives
its short leaf, the adversary chooses a different point mass for period two,
giving cost two. Hence

\[
\boxed{V_{\rm OL}=3.}
\]

### Fully observed feedback without switching cost

At each period, the coder assigns the short leaf to the observed point mass.
Every stage costs one, so

\[
\boxed{V_{\rm FB}=2.}
\]

and

\[
\boxed{\mathcal V_{\rm obs}=1.}
\]

The gain is not mysterious compression. It comes from allowing the code choice
to respond after the current law is revealed.

---

## 6. Exact feedback switching threshold

Let changing the short-leaf assignment cost \(\kappa\). At period two, after an
adversarial move away from the previous short-leaf state, the coder compares:

- keep the old code and pay expected length \(2\);
- switch and pay \(1+\kappa\).

Therefore the second-period feedback cost under a move is

\[
\min\{2,1+\kappa\}.
\]

The adversary moves whenever this is at least the cost of staying. Thus

\[
V_{\rm FB}
=
1+\min\{2,1+\kappa\}.
\]

Equivalently,

\[
\boxed{
V_{\rm FB}
=
\begin{cases}
2+\kappa,&0\le\kappa<1,\\
3,&\kappa\ge1.
\end{cases}
}
\]

The open-loop value remains three: switching an open-loop code cannot prevent
the adversary from selecting a long-leaf point mass for the second period.
Therefore

\[
\boxed{
\mathcal V_{\rm obs}
=
\max\{1-\kappa,0\}.
}
\]

The exact feedback reconfiguration threshold is

\[
\boxed{\kappa_c=1.}
\]

in this finite example.

---

## 7. Transition-set monotonicity

Suppose two transition models share the same law states and

\[
\Gamma_1(i)\subseteq\Gamma_2(i)
\qquad\forall i.
\]

The adversary has every old action and possibly more under \(\Gamma_2\). By
backward induction,

\[
\boxed{
V^{\Gamma_1}_{\rm FB}
\le
V^{\Gamma_2}_{\rm FB}
}
\]

and, for every fixed open-loop sequence, its worst path cost cannot decrease.
Minimizing over sequences preserves

\[
\boxed{
V^{\Gamma_1}_{\rm OL}
\le
V^{\Gamma_2}_{\rm OL}.
}
\]

More source mobility cannot improve the minimizing coder under the same cost
and information pattern.

---

## 8. Why this does not solve partial observation

If the current law is not observed, \(q_t\) is not an admissible controller
state. A policy may depend only on a declared information filtration, such as:

- past realized source symbols;
- delayed count vectors;
- messages from remote observers;
- a confidence set;
- a posterior or robust belief set.

The correct dynamic state is then a belief or uncertainty object. Reusing the
fully observed recursion would leak information to the controller and produce
an unjustifiably optimistic value.

Likewise, a fixed-time multinomial confidence ball is not automatically an
anytime-valid filter under repeated code changes and optional stopping.

---

## 9. Interpretation for predictive rendering

The open-loop result asks how well a representation schedule can be planned
before a changing future law is known. The feedback result asks what changes if
the exact current law becomes available before each representation choice.

This clarifies a frequently hidden assumption in lazy-rendering arguments:

\[
\boxed{
\text{What does the renderer know, and when does it know it?}
}
\]

A system that observes the relevant predictive state before choosing an
encoding can outperform one that commits blindly. A system that sees only noisy
samples may not achieve that value. The difference is an information-pattern
resource, not evidence for or against simulation.

---

## Nonclaims

- The current source law is assumed exactly observed; it is not estimated by the
  module.
- Point-mass K3 is a finite model example, not a claim about natural sources.
- The transition relation is declared and finite; a TV-generated relation over
  a finite grid does not equal a continuous TV-ball game.
- The source transition set is code-independent in this implementation.
- The source adversary chooses the next law after the current code action.
- The controller is deterministic; shared-randomness feedback policies require
  a separate timing model.
- Switching penalty is an abstract scalar, not an inferred physical cost.
- The result does not cover partial observation, online learning, or confidence
  sequences.
- None of these coding identities is evidence that reality is simulated.

---

## Next research targets

1. Partial-observation dynamic programming over exact finite belief states.
2. Robust belief-set recursion under set-valued observation updates.
3. Code-dependent source transitions and strategic source response.
4. Shared-randomness feedback policies with an oblivious or seed-observing
   adversary.
5. Dynamic regret against a clairvoyant code-sequence oracle.
6. Decoder synchronization costs when code updates cross a network.
7. Continuous-law feedback with certified lower and upper abstractions.
8. Anytime-valid source-law filtering under drift.
