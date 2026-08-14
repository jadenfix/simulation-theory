# Coupled-drift notation

| Symbol | Meaning |
|---|---|
| `p` | nominal source law at time zero |
| `q_t` | source law at future period `t` |
| `eta` | per-step total-variation mobility budget |
| `g_t` | period-`t` state-cost vector |
| `ell_c` | state-length vector of deterministic codebook `c` |
| `kappa` | additive codebook-switching penalty |
| `T` | finite commitment horizon |
| `V(g_1:T)` | exact coupled adversarial path value |
| `M(g_1:T)` | sum of independently optimized nominal-centered marginal envelopes |

Always:

\[
V(g_{1:T})\le M(g_{1:T}).
\]

Equality is a simultaneous-attainability statement, not a generic property of time-varying costs.