# Tempera Math Bridge

## Ownership boundary

`jadenfix/simulation-theory` is the canonical home for simulation-hypothesis research, code, assumptions, and nonclaims.

`tempera-math` may be used as an external evidence and certificate harness. It should not become the canonical source of the domain theory, and structural validation must not be mistaken for proof execution.

## Current bridge artifact

[`../claims/claims-v1.json`](../claims/claims-v1.json) records:

- stable claim IDs;
- theorem, model-result, finite-check, or open-problem kind;
- exact scope;
- assumptions;
- evidence paths;
- explicit nonclaims.

`simtheory.claims` validates the schema and computes a deterministic SHA-256 hash over canonical JSON. This supports content-addressed export without coupling the research package to a particular Tempera contract revision.

## Safe future adapter

A future adapter should:

1. Pin the simulation-theory source commit.
2. Validate and hash the claim manifest.
3. Map claim kind and scope without promotion.
4. Attach exact source files, checker commands, inputs, and outputs.
5. Register bounded finite evidence only against bounded claims.
6. Keep external physical/data assumptions unresolved unless separately evidenced.
7. Obtain independent checker receipts where policy requires them.
8. Preserve failed and inconclusive attempts in the proof/search graph.

## Nonclaims

- A manifest hash proves byte identity, not mathematical truth.
- A GitHub Actions pass proves that the declared tests passed in that environment, not that all assumptions hold in reality.
- A Tempera structural validator cannot by itself verify a physical sampling model, an anthropic measure, consciousness, or parent-universe laws.
- No current simulation-theory result establishes that reality is or is not simulated.
