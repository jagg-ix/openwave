# OpenWave M9 CAT/EPT current comparison profile

M9 is integrated through **M9.122**. Stable callers should use:

```text
conformance   openwave/xperiments/m9_cat_ept/model_conformance_current.py
registration  openwave/xperiments/m9_cat_ept/model_registration_current.py
launcher      openwave/xperiments/m9_cat_ept/_launcher.py
```

Current schemas:

```text
openwave.m9.models-conformance.v22
openwave.model-registration.v25
openwave.m9.platform-integration-contract.v5
```

The evidence-derived 21-criterion maturity headlines remain those of M9.109. M9.110--M9.122 add implementation and evidence-readiness infrastructure without promoting calibration, observed identity, held-out validation, or external prediction.

## Authorities

```text
Physlib repository    jagg-ix/entropic-physlib-private
merged branch         master
development branch    private/entropic-physlib-linear-full
merged Physlib head   80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef
Physlib root blob     f953c09c428eb83d9894c1944e1fd44a7ffe95a1
public zil-lean head  c671f02d8b6dcf7ba689afc86477ff7e35465c35
```

M9.122 repins the merged open-system authority, including direct infinitesimal trace preservation of the finite LDDL generator and weak convergence of Cauchy broadening to a Dirac level as its width tends to zero. Those formal results do not themselves validate an observed line shape.

## Integrated lineage

| Milestone | Constructed evidence | Retained boundary |
| --- | --- | --- |
| M9.109 | evidence-derived 21-criterion maturity and Newton-G clock audit | algebraic relations are not held-out predictions |
| M9.110--M9.117 | shared holographic gravity, reduced BSSN-style refinement, and scale flow | no independent screen calibration or continuum Einstein theorem |
| M9.119 | local SU(3) and SU(2)xU(1) gauge-covariant carriers | not QCD or the full electroweak Standard Model |
| M9.120 | gauge-invariant finite spectra, response, and four-grid refinement | not observed masses, widths, or a continuum theorem |
| M9.121 | CPTP model-unit decay, blind commitment, and fail-closed promotion requirements | no calibrated lifetime, held-out result, or observed identity |
| M9.122a | canonical external-evidence package, artifact digests, commitment ordering, target-leakage checks | schema readiness is not evidence ingestion |
| M9.122b | blinded evaluator with blocked live path and synthetic metric fixture | synthetic evaluation is not a held-out physical test |
| M9.122c | independent transition-identity contract with discriminants and negative controls | contract completeness is not observed identity |

## M9.122 evidence-package requirements

A live package must contain:

```text
prediction commitment matching M9.121
commitment timestamp before evidence reveal
independent positive physical time scale
revealed holdout not used for fitting
complete target observations with uncertainties
independent identity bridge
non-label discriminants and negative controls
matching payload and package SHA-256 digests
```

The repository ships an incomplete live template and a clearly marked synthetic fixture. The fixture exercises validation and numerical comparison but can never satisfy the external-evidence or observed-identity gates.

## Current decisions

```text
CPTP intrinsic model-unit decay                  constructed
external evidence package schema                 constructed
artifact integrity and reveal-order checks       constructed
blinded external evaluator                       constructed
independent identity-bridge contract             constructed
weak Cauchy-to-Dirac formal limit                 registered
real external evidence package                   not ingested
live held-out evaluation                         not executed
observed transition identity                     open
external physical validation                     open
external physical promotion                      blocked
```

## Reproduction

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_122a_external_evidence_package.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_122b_blinded_evaluator.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_122c_identity_bridge.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_122_current_registration.py
```

A formal weak zero-width limit is not an empirical detector validation. A structurally complete synthetic fixture is not external evidence. A transition identity must be independently supported rather than inferred from a shared label.
