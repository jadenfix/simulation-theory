# Coupled-drift notation

| Symbol | Meaning |
|---|---|
| \(n\) | finite source alphabet size |
| \(T\) | future horizon |
| \(p\) | fixed initial source law \(q_0\) |
| \(q_t\) | source law at period \(t\) |
| \(\eta_t\) | TV movement budget from \(q_{t-1}\) to \(q_t\) |
| \(R_t\) | cumulative marginal radius \(\min(1,\sum_{s\le t}\eta_s)\) |
| \(g_t\) | rational state-cost vector at period \(t\) |
| \(x\) | concatenated free simplex coordinates |
| \(A x\le b\) | exact path-polytope halfspace system |
| \(c_0+c^Tx\) | eliminated-coordinate cumulative objective |
| \(y\) | nonnegative dual multiplier vector |
| \(c_t\) | deterministic codebook selected at period \(t\) |
| \(\ell^{(c)}\) | source-state length vector of codebook \(c\) |
| \(\kappa\) | cost per codebook switch |
| \(N_{\rm switch}\) | number of adjacent codebook changes |
| \(V_{\rm coupled}\) | exact jointly feasible path value |
| \(V_{\rm marginal}\) | independent expanding-ball upper bound |
