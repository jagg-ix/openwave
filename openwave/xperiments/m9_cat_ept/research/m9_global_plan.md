# M9 global target plan

## Closure through M9.74

- **M9.72:** the live PhysLib branch already contains the complete continuum `H¹(ℝ³)` Bessel-energy carrier, weak sequential compactness for bounded sequences, and a conditional direct-method minimizer theorem. PR #16 adds constrained attainment by making sequential weak closure explicit. The scoped target closes; normalized-mass weak closure, target-energy weak lower semicontinuity, and a concrete bounded minimizing sequence remain target-specific obligations.
- **M9.73:** the live branch already proves a negative normalized variational level, exact cubic mass scaling, strict subadditivity, and a positive cluster binding gap. These exclude vanishing and dichotomy. PR #16 proves that an explicit concentration--compactness trichotomy therefore leaves compactness modulo translations. Derivation of the trichotomy, translation tightness, limit identification, and orbital coercivity remain open.
- **M9.74:** the immutable M9.71 ratio `1.074356835825` is tested with a radial-amplitude deformation and a detrended Hann-windowed periodogram, both different from the derivation controls. Relative discrepancies on `20³/24³/28³` are `2.61%`, `0.21%`, and `1.60%`; all pass the unchanged 5% gate. No external experiment was used.

## Current cross-repository state

| Repository | Revision | Contribution |
| --- | --- | --- |
| OpenWave baseline | `2dfaf6da88b24fe43799b53d79ef2f7aa3244a32` | merged M9.68 state |
| OpenWave work branch | `agent/m9-stationary-formal-mode-69-71` | M9.69--M9.74 implementation and evidence |
| PhysLib live base | `0a04328a01b7911078c4f9d01cc0c8c963519dc2` | complete H¹ weak compactness plus Schrödinger--Newton variational and binding infrastructure |
| PhysLib PR #16 head | `5d0cdf07c891b1dbe7381b93c2d794b593fae09d` | constrained direct method, concentration-branch composition, density coercivity, and orbital certificate |
| PhysLib frozen theorem snapshot | `51aad63b2541a1377a001df71b85dfe35f26c0af` | immutable dependency of M9.69--M9.71 generated ledgers |
| ZIL | `7ef24a8557b610f8f0f560cf375c2a1600083591` | evidence conventions and operational tooling |

## Corrected theory boundary

The platform remains `0 validated / 20 partial / 1 negative`. The lepton hierarchy remains the sole criterion-level negative. The methodological ledger contains two frozen subpredictions: M9.65 is internally falsified; M9.71 passes held-out grids and an independent perturbation/estimator. Neither is externally tested or physically validated.

The formal gap is narrower than previously reported. The branch already supplies weak continuum H¹ compactness, a direct-method engine, vanishing exclusion, and dichotomy exclusion. Remaining work is specific: weak closure of the mass constraint, weak lower semicontinuity of the promoted energy, translation tightness, construction of the conservative flow and invariants, compact-limit identification, and nonzero-branch coercivity modulo symmetries.

## Next phase

| Target | Deliverable | State |
| --- | --- | --- |
| M9.75 | Prove normalized-mass weak closure and sequential weak lower semicontinuity of the promoted target energy | NEXT |
| M9.76 | Construct the conservative state-dependent spatial cubic--quintic `H¹` flow and prove mass/energy conservation | GATED |
| M9.77 | Derive translation tightness, identify the compact limit, and prove coercivity modulo phase/translation | PLANNED |
