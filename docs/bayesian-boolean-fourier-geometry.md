# Fourier geometry of Bayesian Boolean experiments

For the uniform Boolean cube, let `g=(-1)^f` and let

\[
g(x)=\sum_{T\subseteq[k]}\hat g(T)\chi_T(x)
\]

be its Walsh expansion. Observing coordinates `S` projects onto characters supported inside `S`:

\[
\boxed{
E[g\mid X_S]
=
\sum_{T\subseteq S}\hat g(T)\chi_T(X).
}
\]

Define the captured spectral mass

\[
\boxed{
W(S)=\sum_{T\subseteq S}\hat g(T)^2.
}
\]

Parseval gives `W([k])=1`, and conditional orthogonality gives

\[
W(S)=E[(E[g\mid X_S])^2].
\]

The Bayesian K3 gap from the preceding lane is

\[
V(S)=\frac{1-E|E[g\mid X_S]|}{2}.
\]

Writing

\[
B(S)=1-2V(S)=E|E[g\mid X_S]|,
\]

we have `|h|>=h^2` for `|h|<=1` and Cauchy-Schwarz `E|h|<=sqrt(Eh^2)`. Therefore

\[
\boxed{
B(S)^2\le W(S)\le B(S).
}
\]

This exact rational form avoids introducing square roots into the certificate. Equivalently,

\[
\frac{1-\sqrt{W(S)}}2\le V(S)\le\frac{1-W(S)}2.
\]

The bounds expose what an experiment has captured spectrally. Parity concentrates all mass on its full support, so every strict subset has `W=0` and `V=1/2`. Functions with low-order coefficients can become partially predictable sooner.

## Influence identity

For a Boolean sign function under the uniform cube,

\[
\boxed{
\operatorname{Inf}_i(f)
=
\sum_{T\ni i}\hat g(T)^2.
}
\]

The implementation verifies this independently from direct cube-edge counting. If every coordinate except `i` is observed, the captured mass is

\[
W([k]\setminus\{i\})=1-\operatorname{Inf}_i(f).
\]

In this leave-one-out case, each posterior bias takes values only in `{0,1}` in absolute value, so `E|h|=Eh^2` and the upper spectral bound is exact:

\[
\boxed{
V([k]\setminus\{i\})
=
\frac{1-W([k]\setminus\{i\})}{2}
=
\frac{\operatorname{Inf}_i(f)}2.
}
\]

## Why L1 and L2 both matter

Fourier mass is an `L2` object while Bayesian classification/coding error depends on the `L1` magnitude of posterior bias. Two functions can capture the same spectral mass yet have different posterior-bias distributions and therefore different exact Bayes gaps. The sandwich quantifies, rather than erases, that distinction.

This is why a spectral-energy argument by itself is generally insufficient to recover exact experiment value. Exact value requires the conditional-bias distribution; spectral mass supplies certified lower and upper bounds.

## Nonclaims

- Fourier coefficients are computed under the declared uniform prior.
- Spectral mass is not itself an empirical probability that a model is true.
- The square-root version is a mathematical corollary; repository certificates stay rational through `B^2<=W<=B`.
- These internal decision bounds are not physical lower bounds on a hypothetical simulator.
- None of the results is evidence for simulation.
