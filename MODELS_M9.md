# OpenWave M9 CAT/EPT current comparison profile

M9 is integrated through **M9.121**. Stable callers should use:

```text
conformance   openwave/xperiments/m9_cat_ept/model_conformance_current.py
registration  openwave/xperiments/m9_cat_ept/model_registration_current.py
launcher      openwave/xperiments/m9_cat_ept/_launcher.py
```

Current schemas:

```text
openwave.m9.models-conformance.v22
openwave.model-registration.v24
openwave.m9.platform-integration-contract.v4
```

The conformance schema remains v22 because the evidence-derived 21-criterion headlines last changed at M9.109. M9.110--M9.121 add implementation evidence without promoting calibration, identity, or external-validation axes.

## Authorities

```text
Physlib repository   jagg-ix/entropic-physlib-private
Physlib branch       entropic-physlib-linear-full
merged Physlib head  3923d802339c957066fcccd579362f739775797a
Physlib root blob    d225e3cdb0e3239eb6c83f20af25968ddb9ec37b
public zil-lean head c671f02d8b6dcf7ba689afc86477ff7e35465c35
```

M9.121 pins merged Physlib surfaces for finite GKSL generators, bounded `C0` semigroups, trace-class density operators, and constructive nuclear density evolution. It also pins the public ZIL stratified Datalog evaluator. Physlib PRs #19 and #20 remain `draft/open/unmerged` and are not used as merged proof authority.

## Integrated lineage

| Milestone | Constructed evidence | Retained boundary |
| --- | --- | --- |
| M9.109 | evidence-derived 21-criterion maturity and Newton-G clock audit | algebraic G relations are not a withheld prediction |
| M9.110--M9.117 | shared holographic gravity, reduced BSSN-style refinement, and scale flow | no external screen calibration or continuum Einstein theorem |
| M9.119 | local SU(3) and SU(2)xU(1) gauge-covariant carriers | not QCD or the full electroweak theory |
| M9.120 | gauge-invariant finite spectra, source response, and four-grid refinement | not observed masses, widths, or a continuum theorem |
| M9.121a | exact two-level CPTP amplitude-damping channel, semigroup law, Lindblad right derivative, positivity, lifetime and half-life | rates and lifetimes are in model units; the two-level carrier is not full radiative QFT |
| M9.121b | deterministic blind prediction commitment, target-leakage rejection, and tamper detection | no independent physical scale or revealed held-out observation |
| M9.121c | Python and ZIL fail-closed promotion requirements | internal model closure is not external physical validation |

## M9.121a open-system gates

For the strongest nonzero response transition in each finite gauge carrier, M9.121 constructs

```text
gamma = coupling^2 * gap^3 * relative_transition_strength
eta(t) = exp(-gamma t)
```

and the Kraus channel

```text
K0 = diag(1, sqrt(eta) exp(-i omega t))
K1 = sqrt(1-eta) |0><1|.
```

The campaign checks Kraus completeness, trace preservation, positivity, exact semigroup composition, agreement with the GKSL right derivative, exponential excited-state population, lifetime `1/gamma`, and half-life `ln(2)/gamma`. The earlier Lorentzian plotting broadening is not reused as the decay rate.

## M9.121b calibration and holdout protocol

The model-unit spectrum and lifetime payload is hashed before any holdout can be revealed. The protocol rejects:

- using either target decay observable to set the calibration anchor;
- changing the committed prediction payload;
- treating a missing independent anchor as inferred;
- converting model units to physical units without a supplied scale.

The current plan intentionally records:

```text
independent physical anchor supplied  false
held-out observation revealed         false
physical calibration complete         false
external validation complete          false
```

## M9.121c physical promotion gate

Internal model promotion requires:

```text
formalized_by:lean_theorem
implemented_by:numerical_campaign
axiom_status:kernel_clean
reproduced_by:deterministic_runner
```

External physical promotion additionally requires:

```text
calibrated_by:independent_anchor
committed_before_reveal:prediction_digest
tested_against:heldout_observation
identity_supported_by:independent_bridge
```

The present CAT/EPT state passes the internal gate and fails the external gate. Every external relation is individually load-bearing: deleting any one from a complete synthetic record makes promotion fail.

## Current decisions

```text
universal holographic G                         preserved
source-coupled reduced BSSN                     constructed
local SU(3) and SU(2)xU(1) carriers             constructed
gauge-invariant finite spectra and response     constructed
finite spectral refinement                       constructed
CPTP intrinsic model-unit decay                  constructed
blind prediction commitment                      constructed
holdout-safe calibration protocol                constructed
fail-closed physical promotion gate              constructed
independent physical anchor                      missing
held-out physical comparison                     not revealed
observed-particle identity                       open
external physical validation                     open
```

## Reproduction

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_121a_open_decay.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_121b_calibration_holdout.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_121c_promotion_gate.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_121_current_registration.py
```

A theorem-guided adapter is not a new Lean proof. A CPTP channel in model units is not a measured lifetime. A calibration protocol is not calibration. A sealed holdout is not a successful external test.
