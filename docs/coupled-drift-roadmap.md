# Coupled-drift continuation roadmap

## Immediate next theorem lane

Build a finite hidden-mode adaptive coding model with an explicit observation
kernel. The minimum viable exact model should contain:

- a finite hidden mode set;
- a rational prior over modes;
- rational mode-dependent source distributions;
- a rational observation channel;
- a finite deterministic zero-error codebook action set;
- codebook switching cost;
- finite horizon;
- exact posterior updates;
- exhaustive bounded policy-tree search.

Return three values:

\[
V_{\mathrm{open}},
\qquad
V_{\mathrm{causal}},
\qquad
V_{\mathrm{clairvoyant}}.
\]

Their differences isolate the value of declared observations and the residual
value of hidden state information.

## Required proof objects

1. Exact rational posterior receipt for every reachable history.
2. Policy action for every reachable observation history.
3. Exact expected communication and switching cost.
4. Independent exhaustive policy-tree audit on bounded instances.
5. Open-loop and clairvoyant comparator certificates.
6. A declared tie-breaking rule.
7. Hard policy-tree caps that fail closed.

## First strict example

Use two hidden modes and three source symbols. In mode A, state one is dominant;
in mode B, state two is dominant. A binary observation before the second period
is correlated with the mode. The first period uses a common initial code. The
second-period code can either remain unchanged or switch its short leaf toward
the posterior-favored state.

The example should show:

\[
V_{\mathrm{clairvoyant}}
\le
V_{\mathrm{causal}}
\le
V_{\mathrm{open}},
\]

with both inequalities strict for an intermediate observation quality and low
enough switching cost.

## Deeper extensions

- observation acquisition cost and optimal sensing;
- delayed or censored observations;
- posterior-belief compression;
- robust mode-transition sets;
- dynamic regret against matched-information comparators;
- shared randomized policies with adversary timing stated;
- partially observable source drift;
- infinite-horizon discounted and average-cost limits with certified bounds.

No adaptive theorem should be written until the information pattern is explicit.
