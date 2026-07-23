# M9.8 method note: instrumentation without claim promotion

M9.8 consumes the committed scientific ledgers rather than creating a second
source of numerical truth. Presets point to existing deterministic runners and
JSON records. Metric panels are projections of those records.

The instrumentation separates four operations:

1. load a committed ledger;
2. optionally rerun the corresponding deterministic study;
3. build a common metric and acceptance panel;
4. export or render that panel.

Every preset carries an explicit `establishes` and `does_not_establish` section.
This prevents the interactive layer from silently changing the scientific status
of the underlying result.

The default names are `scalar-observables`, `radial-dynamics`, and
`transverse-radiation`. None uses an electron, positron, or Standard Model label.

Focused local validation:

```text
pytest -q tests/test_m9_instrumentation.py
8 passed in 2.35s
```

No CI workflow was run or inspected.
