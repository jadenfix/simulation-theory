# Coupled-drift resource separation

The lane tracks distinct resources:

- expected source-message length;
- maximum codeword length;
- number of codebook switches;
- abstract cost per switch;
- source-law movement budget;
- horizon;
- active-basis search size;
- code-sequence search size.

It does not collapse these into one number. In particular, expected bits are not
peak capacity, switch count is not switch energy, and drift radius is not
statistical confidence.
