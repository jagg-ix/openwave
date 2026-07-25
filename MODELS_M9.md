# OpenWave M9 CAT/EPT comparison profile

The executable source is `openwave/xperiments/m9_cat_ept/model_conformance.py`. Platform validation, formal theorem status, physical identity, calibration, and experimental validation are separate layers.

## Platform summary after M9.93c

| Status | Count |
| --- | ---: |
| ✅ validated in-platform | 7 |
| ⚠️ partial / bounded | 13 |
| ❌ honest negative | 1 |
| 🚧 planned / not yet | 0 |
| **Explicit criteria** | **21** |

Validated rows:

- charge quantization;
- particle stability / Derrick escape;
- spin-1/2 statistics;
- source-free Maxwell waves;
- free massive Klein–Gordon evolution;
- dimensionless Coulomb orbital quantization;
- explicit dimensionless thermal field.

## M9.90 — charge quantization

The field-derived winding observable recovers sectors `-2,-1,0,1,2` with maximum resolution error `2.22e-16`, remains contour and global-phase invariant, survives smooth perturbations, and is additive across separated vortices. Exact arithmetic gives

```text
electron = -1
neutrino = 0
up       = 2/3
down     = -1/3
```

PhysLib proves winding additivity, charge conjugation, the integer-sector iff `3 | n` theorem, and the Fock-space scalar charge grading.

**Boundary:** the winding unit is not identified with a measured elementary electric charge, and spontaneous sector selection is not derived.

## M9.91 — Klein–Gordon

The massive periodic spectral field conserves energy to `4.44e-16`, recovers the dispersion relation with relative error `3.54e-9`, and matches the massless wave sector to `2.22e-16`.

An independent audit across four masses and three nonzero modes closes:

| Control | Maximum error |
| --- | ---: |
| Dispersion | `3.55e-15` |
| Group composition | `8.88e-16` |
| Reversal | `2.22e-16` |
| Mode energy | `3.55e-15` |

The zero-frequency limit also composes exactly. PhysLib packages the finite spectral massive dispersion and conserved quadratic mode energy.

**Boundary:** no interacting scalar QFT, physical scalar-particle identity, or calibrated mass is claimed.

## M9.92 — orbital quantization

The existing radial study recovers four negative hydrogenic levels, node counts `0,1,2,3`, orthogonality to `4.44e-16`, stationary densities, second-order refinement, and stable domains.

The new cross-angular-momentum campaign obtains:

```text
2s / 2p spread       = 1.80677e-5
3s / 3p / 3d spread  = 4.75926e-6
```

PhysLib supplies the unscreened Yukawa-to-Coulomb endpoint and the integer-labelled `O(4)/S³` Gegenbauer harmonics.

**Boundary:** no emergent electron/nucleus identity, radiative transition theory, or physical atomic-unit calibration is claimed.

## M9.93 — model infrastructure closure

M9.93 adds three infrastructure surfaces without promoting a criterion:

- `physlib_contract.py` and `formal/physlib_contract.v2.json` pin `entropic-physlib-linear-full` at an exact commit and source-blob set, associate declarations with numerical adapters, preserve assumptions and claim boundaries, and fail closed under simulated commit/blob drift;
- `particle_model.py` exposes the current action specification, particle specification, three-dimensional state, exact free/local subflows, Strang evolution, perturbations, translations, observables, fingerprints, and physical-identity gate;
- `model_registration.py` registers the launcher, profile, formal contract, particle API, briefing, and current `7/13/1` conformance state as one canonical M9 component.

The repository-default particle has no physical name or calibration record. The neutral stationary branch can be constructed through the existing M9.69 solver. A nonzero winding can be declared, but it is not marked as embedded into the same stationary state until a charged branch is actually constructed.

**Boundary:** M9.93 establishes reusable and testable infrastructure. It does not establish a charged stationary particle, physical unit calibration, an electron identity, or an out-of-sample physical prediction.

## Retained blockers

The remaining thirteen partials require at least one of:

- independent particle identity or calibration;
- full interacting gauge or constituent dynamics;
- physical rates, spectra, abundance, or phenomenology;
- external datasets and no-refit predictions.

The sole criterion-level negative remains the predictive lepton-mass hierarchy. The internally successful M9.71 radial-mode record remains externally blocked.
