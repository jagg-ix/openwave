# OpenWave Models: canonical comparison registry

OpenWave hosts multiple candidate field-theoretic models in one numerical environment. Each model has a dedicated briefing and a current evidence profile. The registry below is the stable entry point; model-specific profiles carry the detailed, reproducible status.

The historical five-model wide table is preserved unchanged in [`MODELS_LEGACY.md`](MODELS_LEGACY.md). It remains useful for its per-cell evidence links, but it predates the M9 CAT/EPT integration and uses a scalar validated/partial/planned vocabulary that does not represent M9's multidimensional maturity model.

## Model registry

| ID | Model | Briefing | Current profile | Status authority |
| --- | --- | --- | --- | --- |
| M4 | Energy Wave Theory (EWT) | [`__M4_model_briefing.md`](openwave/xperiments/m4_ewt/__M4_model_briefing.md) | [`MODELS_LEGACY.md`](MODELS_LEGACY.md) | legacy 21-row scalar matrix |
| M5 | Liquid-Crystal topological defects | [`__M5_model_briefing.md`](openwave/xperiments/m5_liquid_crystal/__M5_model_briefing.md) | [`MODELS_LEGACY.md`](MODELS_LEGACY.md) | legacy 21-row scalar matrix |
| M6 | Ouroboros | [`__M6_model_briefing.md`](openwave/xperiments/m6_ouroboros/__M6_model_briefing.md) | [`MODELS_LEGACY.md`](MODELS_LEGACY.md) | legacy 21-row scalar matrix |
| M7 | HydroBoros | [`__M7_model_briefing.md`](openwave/xperiments/m7_hydroboros/__M7_model_briefing.md) | [`MODELS_LEGACY.md`](MODELS_LEGACY.md) | legacy 21-row scalar matrix |
| M8 | Mode Identity Theory (MIT) | [`__M8_model_briefing.md`](openwave/xperiments/m8_mit/__M8_model_briefing.md) | [`MODELS_LEGACY.md`](MODELS_LEGACY.md) | legacy 21-row scalar matrix |
| **M9** | **CAT/EPT entropic particle dynamics** | [`__M9_model_briefing.md`](openwave/xperiments/m9_cat_ept/__M9_model_briefing.md) | **[`MODELS_M9.md`](MODELS_M9.md)** | **[`model_conformance_current.py`](openwave/xperiments/m9_cat_ept/model_conformance_current.py) + [`model_registration_current.py`](openwave/xperiments/m9_cat_ept/model_registration_current.py)** |

## Status vocabularies

M4--M8 currently retain the historical scalar labels in `MODELS_LEGACY.md`: validated, partial, negative, in progress, and planned.

M9 uses evidence-derived maturity because a single scalar label can hide material distinctions. Each of its 21 criteria records separate axes for:

- mathematical and formal closure;
- numerical construction and stability;
- physical-unit calibration;
- particle or phenomenon identity;
- prediction readiness and external validation.

A criterion may therefore have a constructed reduced carrier while physical identity and prediction readiness remain open. Root summaries must not convert that state into an unconditional check mark.

## M9 - CAT/EPT current state

Current integrated milestone: **M9.119**.

| Layer | Current result | Boundary retained |
| --- | --- | --- |
| 21-criterion conformance | evidence-derived M9.109 maturity remains current | later implementation evidence does not silently promote criterion headlines |
| one-screen gravity | one holographic `G = (A/N_H)c^3/hbar` reaches weak and nonlinear carriers | synthetic anchors are not physical calibration |
| generalized gravity | TT modes, trace-free curvature, shift, BSSN-style variables and gauges constructed | reduced periodic carrier is not production numerical relativity |
| curvature and constraints | metric-built conformal Ricci, scalar screen-tidal source, tensor/Gamma damping and three-grid refinement constructed | finite-grid consistency is not a continuum Einstein proof |
| coarse graining | continuous count flow, finite heat/block flow and Gaussian covariance adapter constructed | particle-mass endpoint and interacting CAT/EPT fixed point remain open |
| multi-resolution gravity | one-G low-mode Poisson/tidal observables agree across three odd grids | scale consistency is not external experimental validation |
| local strong carrier | SU(3) links, covariant color transport, plaquettes and finite Wilson loops constructed | finite carrier is not lattice QCD or a confinement result |
| local electroweak carrier | SU(2)xU(1) links, U(1)^3 Higgs action, covariant flow and quartic vacuum orbit constructed | bosonic carrier is not full chiral electroweak theory or mass prediction |

Stable executable entry points:

```bash
python -m openwave.xperiments.m9_cat_ept._launcher --current-conformance
python -m openwave.xperiments.m9_cat_ept._launcher --current-registration
python -m openwave.xperiments.m9_cat_ept._launcher --platform-contract
```

## Comparison policy

Every positive or negative result must link to executable code or a research record, preserve explicit claim boundaries, and distinguish implementation closure from physical validation. Lean/Physlib remains proof authority for imported formal statements; OpenWave supplies numerical and discretization evidence.

The shared comparison target remains 21 criteria across particles, forces, waves/quantum emergence, and thermal behavior. See each model profile for its current evidence and [`MODELS_LEGACY.md`](MODELS_LEGACY.md) for the original M4--M8 side-by-side table.
