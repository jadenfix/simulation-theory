# Primary Sources and Research Context

These sources motivate model assumptions, mathematical tools, and counterarguments. None is treated as empirical evidence that simulation is true.

## Core simulation argument

- Nick Bostrom, **Are You Living in a Computer Simulation?** (2003): https://simulation-argument.com/simulation/
- Oxford University Research Archive record: https://ora.ox.ac.uk/objects/uuid:44c386c4-5d9e-4ecf-a47c-9631a2a59747/

Bostrom's result is a trilemma involving pre-posthuman extinction, convergence on not running many ancestor simulations, or simulated observers dominating the relevant observer population. It is not itself an empirical detection theorem.

## Bayesian model uncertainty

- David Kipping, **A Bayesian Approach to the Simulation Argument** (2020): https://arxiv.org/abs/2008.12254

Kipping explicitly models uncertainty over whether the relevant simulations are technically possible. This repository separately studies uncertainty inside observer measure, likelihood classes, and conditioning conventions.

## Restricted physical architecture

- Silas R. Beane, Zohreh Davoudi, Martin J. Savage, **Constraints on the Universe as a Numerical Simulation** (2012): https://arxiv.org/abs/1210.1847

This is an example of the scientifically meaningful lane: assume a specific cubic spacetime-lattice implementation and derive observable consequences. Such a test constrains that implementation class, not every possible simulator.

## Anthropic conditioning

- Radford M. Neal, **Puzzles of Anthropic Reasoning Resolved Using Full Non-indexical Conditioning** (2006): https://arxiv.org/abs/math/0608592

Neal argues for conditioning on the observer's full evidence rather than only reference-class membership. The repository does not claim to settle SSA/SIA/FNC; its finite rules are sensitivity models.

## Predictive states and minimal representations

- Cosma R. Shalizi and James P. Crutchfield, **Computational Mechanics: Pattern and Prediction, Structure and Simplicity**: https://arxiv.org/abs/cond-mat/9907176

Computational mechanics defines causal states through equivalence of future conditional distributions and proves minimality properties for accurate prediction. The repository's finite predictive-equivalence and packing arguments are deliberately narrower, auditable analogues for adaptive-rendering models.

## Minimax identification

- Ramji Venkataramanan and Oliver Johnson, **A Strong Converse Bound for Multiple Hypothesis Testing, with Applications to High-Dimensional Estimation** (2017): https://arxiv.org/abs/1706.04410

Fano-style bounds are useful for showing when no architecture classifier can succeed with limited observations. Stronger converse methods may improve the current finite lower bounds and are a planned extension.

## Causal selection bias

- Elias Bareinboim, Jin Tian, Judea Pearl, **Recovering from Selection Bias in Causal and Statistical Inference** (2014): https://ojs.aaai.org/index.php/AAAI/article/view/9074
- Elias Bareinboim and Judea Pearl, **A General Algorithm for Deciding Transportability of Experimental Results**: https://arxiv.org/abs/1312.7485

These works motivate treating retention and environment selection as causal variables rather than merely static likelihood corrections.

## Anytime-valid inference and e-processes

- Aaditya Ramdas, Johannes Ruf, Martin Larsson, Wouter Koolen, **Admissible Anytime-Valid Sequential Inference Must Rely on Nonnegative Martingales**: https://arxiv.org/abs/2009.03167
- Aaditya Ramdas, Peter Grünwald, Vladimir Vovk, Glenn Shafer, **Game-Theoretic Statistics and Safe Anytime-Valid Inference**: https://arxiv.org/abs/2210.01948
- Ben Chugg, Aaditya Ramdas, Peter Grünwald, **E-values as Statistical Evidence: A Comparison to Bayes Factors, Likelihoods, and p-values** (2026): https://arxiv.org/abs/2603.24421

The repository's Bernoulli likelihood-ratio e-process is intentionally simple: it provides an auditable optional-stopping guarantee under a declared sampling model, not a generic anomaly detector.

## Physical limits of local computation

- Rolf Landauer, **Irreversibility and Heat Generation in the Computing Process** (1961): https://doi.org/10.1147/rd.53.0183
- Norman Margolus and Lev B. Levitin, **The Maximum Speed of Dynamical Evolution**: https://arxiv.org/abs/quant-ph/9710043
- Jacob D. Bekenstein, **Universal Upper Bound on the Entropy-to-Energy Ratio for Bounded Systems** (1981): https://doi.org/10.1103/PhysRevD.23.287
- Seth Lloyd, **Ultimate Physical Limits to Computation**: https://arxiv.org/abs/quant-ph/9908043

These bounds apply under specified local physical assumptions. They do not constrain an unknown parent substrate without a separate law-transfer or implementation premise.

## How sources are used

A citation can motivate a hypothesis, model family, or definition. It does not inherit theorem status. Every repository result must still be assigned one of: theorem under stated assumptions, model result, bounded finite check, restricted empirical hypothesis, or open problem.
