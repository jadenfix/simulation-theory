# Prior robustness of Bayesian Boolean experiment value

For a fixed observed coordinate set `S`, the Bayesian K3 excess coding cost is the Bayes classification risk of `f(X)` from `X_S` under the declared model prior `pi`:

\[
V_\pi(S)=\sum_C\min\{\pi(C,f=0),\pi(C,f=1)\}.
\]

## Concavity in the prior

Each cell term is the minimum of two linear functions of `pi`, hence is concave. Therefore

\[
\boxed{
V_{\lambda p+(1-\lambda)q}(S)
\ge
\lambda V_p(S)+(1-\lambda)V_q(S).
}
\]

Mixing prior scenarios can make the decision problem harder because the controller is not told which component prior generated the model.

## Sharp total-variation continuity

For any classifier `a`, its `0-1` risk differs by at most `TV(p,q)` under priors `p` and `q`. Taking the optimum on each side gives

\[
\boxed{
|V_p(S)-V_q(S)|\le TV(p,q).
}
\]

The constant one is sharp. For the one-bit truth table `f(x)=x`, priors

\[
p=(1,0),\qquad q=(1-\rho,\rho),\quad 0\le\rho\le1/2,
\]

have `TV(p,q)=rho`, while the no-observation Bayes values are `0` and `rho`.

Thus if an external statistical procedure certifies

\[
TV(p,p_0)\le\rho,
\]

then every fixed experiment value satisfies

\[
\boxed{
V_p(S)\in[V_{p_0}(S)-\rho,\,V_{p_0}(S)+\rho]
}
\]

after truncating to `[0,1/2]`.

## Marginal experiment gains

For `S subset T`, define

\[
G_p(S\to T)=V_p(S)-V_p(T).
\]

Because each endpoint is 1-Lipschitz,

\[
\boxed{
|G_p-G_q|\le2TV(p,q).
}
\]

Hence a nominal marginal-gain estimate `g0` under prior `p0` has the conservative TV-radius band

\[
[g_0-2\rho,\,g_0+2\rho]
\]

truncated to the feasible loss range.

For comparing two absolute experiment values, a nominal separation greater than `2 rho` cannot reverse anywhere in the TV ball. For comparing two marginal gains, a nominal separation greater than `4 rho` cannot reverse.

These are sufficient stability margins, not necessary ones; the actual geometry may be substantially tighter.

## Statistical boundary

This module deliberately starts from a declared TV radius. It does not infer that radius from observations. A finite-sample confidence region, Bayesian posterior credible region, contamination model, or other statistical procedure must supply the uncertainty set separately, with its own assumptions about sampling, stopping, stationarity, and model specification.

That separation prevents a deterministic robustness theorem from being mislabeled as a statistical confidence statement.

## Nonclaims

- A nominal model prior is not assumed empirically correct.
- TV sensitivity bounds do not identify which prior perturbations are scientifically plausible.
- Ranking certificates are sufficient worst-case guarantees, not exact necessary thresholds.
- None of these prior-robust decision bounds is evidence for simulation.
