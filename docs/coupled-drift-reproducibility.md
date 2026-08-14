# Coupled-drift reproducibility

Run the complete repository checks:

```bash
python -m pip install -e . pytest
python -m compileall -q src
python -m pytest
python -m simtheory.experiments
```

Run only the coupled-drift lane:

```bash
python -m pytest \
  tests/test_coupled_drift.py \
  tests/test_coupled_drift_properties.py \
  tests/test_coupled_drift_sequence_receipts.py \
  tests/test_coupled_drift_claims.py
```

The expected exact benchmark values are:

```text
binary reversing-cost coupled value: 5/4
binary marginal relaxation:          7/4
binary compatibility gap:            1/2
uniform K3 rotating value:           11/3
uniform K3 best static value:         23/6
uniform K3 switching threshold:       1/6
```

A successful run establishes only that the declared exact finite checker and
its bounded tests agree at the checked source revision. It does not establish a
large-instance complexity theorem or an empirical simulation claim.
