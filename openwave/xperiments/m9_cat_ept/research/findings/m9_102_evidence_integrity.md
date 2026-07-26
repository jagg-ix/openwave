# M9.102 findings: evidence integrity after PR #92

## Formal drift

OpenWave PR #92 remains the latest merged OpenWave change. Its historical formal pin is `acdbe8ce6456e66837bd18604cf3107d3181c4de`.

The live `entropic-physlib-linear-full` branch moved six commits to `eba0124fcfbc1216d973bb6f504c5a6d324de60c`, adding claim-maturity, evidence-integrity, and theorem-intent auditing. The M9.101 physics-source files did not change in that six-commit delta.

Result: historical reproduction and current formal verification are now represented separately.

## Maturity correction

M9.101 stored the actual stationary and packet sub-gates, but the maturity overlay assigned `reduced_constructed` to the three spin/force rows whenever the coupled-action campaign was present.

M9.102 records:

- coupled action and solver as implementation evidence;
- packet T-BMT adapter as implementation evidence;
- symmetry-reduced stationary branch as a state gate;
- unrestricted stability as a stronger state gate;
- packet T-BMT closure as a reduction gate.

Result: an executed solver with a failed state gate leaves the state axis `not_constructed`.

## Reproducibility correction

M9.101 did not commit post-merge result JSON for its four long campaigns. M9.102 adds a fresh snapshot generator and verifier. Every bundle contains full payloads, exact schemas, component SHA-256 hashes, quantitative summaries, and both campaign and physical sub-gate outcomes.

Result: third parties can publish a complete quantitative run without relying on PR prose or a top-level `passed` flag.

## Status impact

The headline counts remain:

```text
validated_in_scope       7
conditional_validated    5
reduced_model_validated  3
calibration_pending      1
candidate                4
negative                 1
```

No physical identity, calibration, or external prediction status changes. The improvement is evidence precision and reproducibility.
