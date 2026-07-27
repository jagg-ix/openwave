# OpenWave Models: canonical comparison registry

OpenWave hosts multiple candidate field-theoretic models in one numerical environment. Each model has a dedicated briefing and current evidence profile. The historical M4--M8 matrix is preserved in [`MODELS_LEGACY.md`](MODELS_LEGACY.md).

## Model registry

| ID | Model | Briefing | Current profile | Status authority |
| --- | --- | --- | --- | --- |
| M4 | Energy Wave Theory (EWT) | [`__M4_model_briefing.md`](openwave/xperiments/m4_ewt/__M4_model_briefing.md) | [`MODELS_LEGACY.md`](MODELS_LEGACY.md) | legacy matrix |
| M5 | Liquid-Crystal topological defects | [`__M5_model_briefing.md`](openwave/xperiments/m5_liquid_crystal/__M5_model_briefing.md) | [`MODELS_LEGACY.md`](MODELS_LEGACY.md) | legacy matrix |
| M6 | Ouroboros | [`__M6_model_briefing.md`](openwave/xperiments/m6_ouroboros/__M6_model_briefing.md) | [`MODELS_LEGACY.md`](MODELS_LEGACY.md) | legacy matrix |
| M7 | HydroBoros | [`__M7_model_briefing.md`](openwave/xperiments/m7_hydroboros/__M7_model_briefing.md) | [`MODELS_LEGACY.md`](MODELS_LEGACY.md) | legacy matrix |
| M8 | Mode Identity Theory (MIT) | [`__M8_model_briefing.md`](openwave/xperiments/m8_mit/__M8_model_briefing.md) | [`MODELS_LEGACY.md`](MODELS_LEGACY.md) | legacy matrix |
| **M9** | **CAT/EPT entropic particle dynamics** | [`__M9_model_briefing.md`](openwave/xperiments/m9_cat_ept/__M9_model_briefing.md) | **[`MODELS_M9.md`](MODELS_M9.md)** | **[`model_conformance_current.py`](openwave/xperiments/m9_cat_ept/model_conformance_current.py) + [`model_registration_current.py`](openwave/xperiments/m9_cat_ept/model_registration_current.py)** |

## M9 status policy

M9 uses evidence-derived maturity rather than one scalar status. Its 21 criteria separately record theorem status, numerical construction, stability, calibration, physical identity, prediction readiness, and external validation.

## M9 - CAT/EPT current state

Current integrated milestone: **M9.121**.

| Layer | Current result | Boundary retained |
| --- | --- | --- |
| 21-criterion conformance | M9.109 evidence-derived maturity remains canonical | later implementation does not silently promote physical axes |
| gravity and scale flow | shared holographic G, reduced BSSN-style refinement, and coarse-graining carriers | no independently calibrated screen or continuum Einstein development |
| local gauge sectors | SU(3) and SU(2)xU(1) links with covariant matter/link evolution | finite carriers are not QCD or the full electroweak Standard Model |
| finite spectra and response | gauge-invariant spectra, residuals, response, and completeness sum rules | dimensionless modes are not observed masses or decay widths |
| spectral refinement | four odd grids show improving flat and smooth low-mode sequences | finite-grid improvement is not a continuum theorem |
| open-system decay | CPTP amplitude-damping semigroups produce intrinsic model-unit lifetimes | model-unit rates are not calibrated physical widths |
| calibration governance | blind prediction commitment and target-leakage rejection constructed | no independent physical anchor or revealed holdout is present |
| promotion governance | internal evidence passes; external physical promotion fails closed | calibration, held-out testing, and identity bridge remain mandatory |

Stable executable entry points:

```bash
python -m openwave.xperiments.m9_cat_ept._launcher --current-conformance
python -m openwave.xperiments.m9_cat_ept._launcher --current-registration
python -m openwave.xperiments.m9_cat_ept._launcher --platform-contract
```

Every result must retain explicit claim boundaries and distinguish formal or internal closure from physical validation.
