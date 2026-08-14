# Coupled-drift assumptions ledger

## Mathematical assumptions

- The source alphabet is finite.
- Initial probabilities, drift budgets, and costs are exact rational values.
- Every source law lies in the full finite probability simplex.
- Temporal movement is bounded by total variation.
- The horizon is finite and known.
- Period costs are additive and linear in the source law.
- Exact searches are interpreted only when every configured cap completes.

## Coding assumptions

- The finite confusion graph is declared in advance.
- Every period uses a deterministic zero-error binary prefix codebook.
- The codebook sequence is fixed before nature selects the source path.
- Codebook switching cost is additive and constant per changed state-length
  vector.
- Encoder and decoder share the declared sequence without separately pricing its
  distribution.

## Inferential assumptions not supplied by this lane

- No theorem here establishes that observed data came from a bounded-TV path.
- No theorem here estimates the drift budgets.
- No theorem here supplies optional-stopping-safe drift confidence sequences.
- No theorem here handles arbitrary model misspecification.

## Physical assumptions not supplied by this lane

- No map from internal code length to parent hardware is assumed.
- No parent law is assumed to equal internal information theory.
- No switching penalty is assigned units of energy, mass, time, or spacetime.
- No empirical signature is derived from these coding theorems alone.
