# Coupled-drift merge readiness

The lane is merge-ready only when:

- all coupled-drift source files compile;
- the full repository test suite passes on Python 3.11, 3.12, and 3.13;
- the deterministic experiment smoke suite passes on all three versions;
- claim evidence paths resolve;
- exact benchmark values replay;
- no active-basis or sequence cap is exceeded in the declared tests;
- README and research roadmap preserve open-loop/adaptive and internal/parent
  boundaries.

A previous red workflow caused only by an intentionally added incorrect test
expectation does not count as green evidence; the corrected branch head must
have its own successful full matrix.
