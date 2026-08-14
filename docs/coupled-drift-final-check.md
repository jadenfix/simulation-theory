# Final coupled-drift branch check

Before merge, verify the exact branch head—not an earlier green commit—passes:

```text
compileall
full pytest
experiment smoke
Python 3.11
Python 3.12
Python 3.13
```

Then open the PR, let the pull-request-triggered matrix run on the same head,
inspect review threads, mark ready, squash merge with the expected head SHA, and
verify the post-merge `main` workflow.
