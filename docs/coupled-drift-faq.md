# Coupled-drift FAQ

## Why not solve each time step separately?

Because the separately selected laws may not be connected by the allowed
transition budget. Their sum is only an upper bound.

## Why total variation?

For a finite alphabet it has an exact event interpretation and exact rational
polyhedral representation. It is one declared geometry, not a universal choice.

## Why enumerate vertices?

A linear objective over a bounded polytope attains its optimum at a vertex.
Complete bounded enumeration gives a transparent primal receipt.

## Why also compute a dual?

The dual independently proves that no omitted path can improve the selected
vertex. Exact equality and complementary slackness make the receipt replayable.

## Is a changing code sequence adaptive?

No. The full sequence is committed before the source path is chosen. Adaptive
coding requires declared observations and a causal policy.

## Why can changing codebooks help?

A slow-moving source cannot simultaneously move away from different short
codewords at every time. Rotating specialization can exploit that temporal
incompatibility.

## What does the switching threshold mean?

It is the largest abstract reconfiguration penalty for which the communication
saving still justifies changing codebooks in the declared model.

## Does this support simulation theory?

Not by itself. It supplies tools for analyzing a restricted dynamic renderer or
communication architecture after its observable and causal interface is
specified.
