# M9 global target plan

## Closure through M9.74

- **M9.72:** the live PhysLib branch already contains the complete continuum H¹ carrier, weak compactness with norm-bound retention, weak-plus-norm strong closure, Prokhorov compactness consequences, one common field/density subsequence from tightness, a direct-method engine, local existence/uniqueness for every `C¹` H¹ generator, and compact-sublevel Cazenave--Lions stability. PR #16 adds predicate-carrier and constrained bridges.
- **M9.73:** negative normalized energy excludes vanishing; strict subadditivity and positive binding gap exclude dichotomy; an explicit trichotomy therefore leaves compactness modulo translations.
- **M9.74:** the immutable M9.71 ratio `1.074356835825` is tested with a radial-amplitude deformation and a detrended Hann-windowed periodogram. `20³/24³/28³` discrepancies are `2.61%`, `0.21%`, and `1.60%`; all pass the unchanged 5% gate.

## Current cross-repository state

| Repository | Revision | Contribution |
| --- | --- | --- |
| OpenWave current `main` | `ec309cdf9976f16155ef3ec07f8290126a652061` | merged PR #75 / M9.69--M9.71 |
| OpenWave frozen campaign baseline | `2dfaf6da88b24fe43799b53d79ef2f7aa3244a32` | immutable numerical ancestry |
| OpenWave clean work branch | `agent/m9-deep-h1-closure-72-74` | M9.72--M9.74 reconciliation and evidence |
| PhysLib live base | `496b275336f30c0f934fe4ddcfa9fbfd99fa567c` | H¹ compactness/strong closure, tight-measure compactness, local dynamics, orbital mechanism, and variational/binding infrastructure |
| PhysLib PR #16 head | `9a15bf5023980f6bc401671de7dc7dca164a52d0` | predicate compactness bridges, constrained direct method, concentration composition, and density coercivity |
| PhysLib frozen theorem snapshot | `51aad63b2541a1377a001df71b85dfe35f26c0af` | immutable M9.69--M9.71 dependency |

## Corrected theory boundary

The platform remains `0 validated / 20 partial / 1 negative`. Generic weak H¹ compactness, norm-bound retention, strong closure from weak-plus-norm convergence, Prokhorov compactness consequences, local ODE well-posedness, and the Cazenave--Lions stability mechanism are already formal. Remaining work is target-specific.

## Next phase

| Target | Deliverable | State |
| --- | --- | --- |
| M9.75 | Prove concrete target-generator `H¹ → H¹` and `C¹`; prove normalized-mass weak closure and target-energy weak lower semicontinuity | NEXT |
| M9.76 | Derive recentered tightness/concentration trichotomy and compact target low-energy sublevels | GATED |
| M9.77 | Construct global mass/energy-preserving target flow, identify compact branch, and instantiate orbital stability | PLANNED |
