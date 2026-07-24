# M9 CAT/EPT: Entropic Particle Dynamics

M9 covers all 21 comparison criteria and now includes a stationary non-Gaussian spatial branch, an exact cubic--quintic coercivity theorem, a conditional kernel orbital-stability bridge, and a replacement radial-mode prediction tested on held-out grids.

## Platform status

- Zero criteria are fully validated in-platform.
- Twenty criteria are partial or bounded.
- The predictive lepton-mass hierarchy remains the sole criterion-level negative.
- M9.69 replaces the failed Gaussian stationary ansatz with a localized full-equation branch that converges from super-Gaussian, anisotropic, and shell seeds.
- M9.70 proves exact density coercivity and derives uniform orbital control from explicit analytic certificate fields. The actual spatial `H¹` flow, conservation laws, concentration compactness, and nonzero-branch coercivity still need end-to-end construction.
- M9.71 freezes `omega_radial / omega_Compton = 1.074356835825` and passes held-out `24³` and `28³` grids without refitting. This is internal computational evidence, not experimental validation.

## Cross-repository sources

| Repository | Ref | Revision | Authority |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | `main` baseline | `2dfaf6da88b24fe43799b53d79ef2f7aa3244a32` | merged simulation evidence |
| `jagg-ix/entropic-physlib-private` | `entropic-physlib-linear-full` | `f148278ec8264d031753d9def49cd2133ac4768d` | current formal baseline including Schrödinger--Newton cluster-binding updates |
| `jagg-ix/entropic-physlib-private` | M9.70 theorem snapshot | `51aad63b2541a1377a001df71b85dfe35f26c0af` | theorem revision pinned by generated M9.69--M9.71 ledgers |
| `jagg-ix/entropic-physlib-private` | PR #16 / `agent/m9-cubic-quintic-h1-certificate-70-current` | `f165cd8ba524a4274cb46bcd4c4ba1f12a274bf7` | rebased audited theorem branch |
| `jagg-ix/zil-lean` | `main` | `7ef24a8557b610f8f0f560cf375c2a1600083591` | evidence conventions and tooling |

The rebased audited successor preserves the theorem statements used by the frozen numerical ledgers while incorporating the latest formal baseline.

## Latest closures

- **M9.69:** maximum seed distance `0.002245`; maximum stationary residual `0.002671`; nested radius spread `0.012753`; boundary fraction below `9e-7`; best-Gaussian `L²` distance at least `0.06790`.
- **M9.70:** exact density factorization is kernel formalized. The numerical coefficient specialization closes to `3.55e-15`. Uniform orbital control is proved from an explicit `H1OrbitalCertificate`; missing analytic PDE certificates remain visible premises. PR #16 exports ZIL scope records and a dedicated axiom/non-vacuity audit.
- **M9.71:** derivation ratio `1.074356835825`; held-out discrepancies `2.34%` and `4.18%`, both within the frozen `5%` gate. No external experiment was performed.

ZIL records identities, dependencies, scope, and evidence-state transitions. Lean remains theorem authority; OpenWave remains simulation software.

## Next critical targets

1. M9.72 construct the spatial cubic--quintic `H¹` flow and conserved quantities required by the M9.70 certificate.
2. M9.73 establish concentration compactness and nonzero-branch coercivity modulo phase and translation.
3. M9.74 compare the frozen M9.71 radial mode with an independent implementation or external physical observable without refitting.
