# OpenWave Models: canonical comparison registry

OpenWave hosts multiple candidate field-theoretic models in one numerical environment. The historical M4--M8 comparison remains in [`MODELS_LEGACY.md`](MODELS_LEGACY.md).

| ID | Model | Current profile | Status authority |
| --- | --- | --- | --- |
| M4--M8 | historical OpenWave models | [`MODELS_LEGACY.md`](MODELS_LEGACY.md) | legacy matrix |
| **M9** | **CAT/EPT entropic particle dynamics** | **[`MODELS_M9.md`](MODELS_M9.md)** | **current registration + conformance aliases** |

## M9 current state

Current integrated milestone: **M9.122**.

| Layer | Current result | Boundary retained |
| --- | --- | --- |
| 21-criterion maturity | M9.109 evidence-derived profile remains canonical | later implementation cannot silently promote physical axes |
| gravity, gauge, spectra, and decay | reduced carriers, gauge-invariant finite spectra, response, refinement, and CPTP model-unit decay | not a calibrated continuum Standard Model or gravity prediction |
| external-evidence package | canonical digest-checked package and reveal-order validation | schema readiness is not external evidence |
| blinded evaluator | live path blocks before reveal; synthetic fixture exercises metrics | synthetic data are not held-out validation |
| identity bridge | independent discriminants and negative controls required | shared names do not establish observed identity |
| promotion | external promotion remains fail-closed | real anchor, holdout, and identity evidence remain missing |

Stable entry points:

```bash
python -m openwave.xperiments.m9_cat_ept._launcher --current-conformance
python -m openwave.xperiments.m9_cat_ept._launcher --current-registration
python -m openwave.xperiments.m9_cat_ept._launcher --platform-contract
```

Every result must distinguish formal or internal closure from physical calibration, identity, and external validation.
