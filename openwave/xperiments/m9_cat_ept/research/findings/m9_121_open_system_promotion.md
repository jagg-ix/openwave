# M9.121 open-system and physical-promotion findings

## Result

M9.121 closes an intrinsic irreversible channel in the finite CAT/EPT gauge carriers without reusing M9.120's Lorentzian plotting width. The selected nonzero response gap and relative transition strength define a model-unit rate

```text
gamma = coupling^2 * gap^3 * relative_strength.
```

The corresponding two-level amplitude-damping Kraus channel is completely positive and trace preserving. It obeys exact semigroup composition, agrees with its GKSL right derivative, preserves density positivity, and gives exponential excited-state decay with lifetime `1/gamma` and half-life `ln(2)/gamma`.

## Negative and retained results

The channel does not establish a measured decay width. The coupling, spectral gap, and response strength remain finite-carrier model quantities. The two-level truncation is not a complete radiative QFT sector and does not identify an observed particle or transition.

The blind calibration protocol commits the model-unit prediction before any holdout is revealed. It rejects target leakage, payload tampering, and physical-unit conversion without an independent scale. No independent anchor or held-out observation is supplied in this milestone.

The physical-promotion gate accepts internal model closure and rejects external promotion. External promotion requires all of:

```text
calibrated_by:independent_anchor
committed_before_reveal:prediction_digest
tested_against:heldout_observation
identity_supported_by:independent_bridge
```

## Formal authority

The formal contract pins merged Physlib results for finite GKSL generators, bounded `C0` semigroups, trace-class density operators, and constructive nuclear density evolution. It also pins the public ZIL stratified Datalog evaluator. Draft Physlib PRs #19 and #20 are recorded but not promoted.

## Next falsifiable target

M9.122 must supply an independent physical scale, freeze the prediction, reveal held-out data, and test one independently identified transition without refitting. Another internal diagonalization or algebraic identity cannot satisfy the promotion gate.
