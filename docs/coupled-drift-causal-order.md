# Coupled-drift causal order

The code sequence is upstream of the adversarial source path in the principal
model. The source path is upstream of realized source symbols. No realized
symbol is fed back into the code sequence.

Any future adaptive extension must add explicit observation edges to this causal
order rather than granting the encoder direct access to the hidden law.
