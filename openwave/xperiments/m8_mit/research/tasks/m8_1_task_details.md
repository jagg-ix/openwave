# M8.1: THE CERTIFICATION GATE, independent eigensolve of the twisted Möbius Laplacian

> Roadmap row: [`../m8_roadmap.md`](../m8_roadmap.md) M8.1 (maintainer-run). Spec of
> record: [`../m8_theory_canonical.md § 3`](../m8_theory_canonical.md). Operator
> source: the author's
> [first-eigenvalue.md](https://github.com/dmobius3/mode-identity-theory/blob/main/files/framework/files/bedrock/files/first-eigenvalue.md)
> (shared on [#312](https://github.com/openwave-labs/openwave/discussions/312)).

## TASK PLANNING (2026-07-21, go 12:54 EDT)

### Scope

Independent numerical verification of the headline analytic result of the MIT bedrock
first-eigenvalue paper: the first positive eigenvalue of the twisted Laplacian on the
constant-curvature (spherical) Möbius band M(W) with a cone point, and its stability
across the cone's self-adjoint extensions. This is the M8 column's certification gate:
either outcome is a result and informs everything downstream (Λ = 3/R² rides this
eigenvalue).

### The independence protocol (per ONBOARDING_MODELS.md § 6)

| Role | Sees | Does not see |
| --- | --- | --- |
| Designer (this session's orchestrator) | the author's full paper (fetched to the session scratchpad, OUTSIDE the repo) | n/a |
| Solver agent | ONLY a self-contained operator spec sheet (geometry, gluing, boundary conditions, the two realizations defined via cone-trace data) + task list | the claimed eigenvalues, thresholds, eigenfunctions, asymptotics, the author's name/repo/paper, ALL repository docs (explicitly instructed not to read any markdown) |
| Audit agent | the same spec sheet + the solver's outputs + the solver's script | same blindness to the claims |
| Comparison to the claims | done by the designer AFTER both agents return numbers | |

Withheld from both agents: every formula of the paper's Theorems 1.1/1.2 (the values
2/R², α₀(α₀+1)/R², the δ₀ > 2R/e threshold, the λ_b(δ₀) asymptotic, the mode-crossing
location, the eigenfunction forms, the Legendre/lune reductions).

### Pre-registered claims under test (fixed BEFORE numerics)

Units: R = 1 throughout (report λ·R² = λ). "Converged" = Richardson-extrapolated
across ≥ 3 resolutions with a stated error estimate.

| ID | Claim (from the paper, exact) | Pass condition | Fail condition |
| --- | --- | --- | --- |
| C1 (PRIMARY, the gate) | λ₁⁺(W) = 2/R² for every 0 < W ≤ πR/2, Friedrichs realization | converged λ₁⁺ within 0.5% of 2 at every narrow-grid W | systematic converged deviation > 0.5% at any narrow W |
| C2 | λ₁⁺(W) = α₀(α₀+1)/R², α₀ = πR/(2W), for πR/2 < W < πR; branches cross (degenerate) at W = πR/2 | converged λ₁⁺ within 0.5% of the formula on the wide grid; near-degeneracy at W = πR/2 | deviation > 0.5% or no crossing |
| C3 | the first positive level is IDENTICAL between Friedrichs and the bridging realization for every δ₀ > 2R/e | measured λ₁⁺(δ₀) matches the Friedrichs value within tolerance for all sampled δ₀ > 0.736R; the empirical stability boundary consistent with 2R/e ≈ 0.7358R | λ₁⁺ moves with δ₀ in the claimed-stable region |
| C4 (secondary) | Friedrichs bottom = 0 (a zero mode exists); bridging carries exactly ONE negative eigenvalue with λ_b(δ₀) → −4e^(−2γ)/δ₀² as δ₀ → 0 | zero mode found at 0 (\|λ\| < tol); one negative eigenvalue whose small-δ₀ trend matches the asymptotic within its O(δ₀²/R²) correction | bottom > 0, no negative state, or wrong count/trend |
| C5 (spec-fidelity) | the numerics implement the paper's own operator (metric, gluing, Neumann arcs, trace-defined extensions), confirmed by the audit | audit CONFIRMS spec fidelity of both implementations | audit finds either implementation deviates from the spec |

No-search rule: every computed number is reported; nothing is tuned toward the
claims; if the numbers land somewhere else, that IS the result (the M6 lesson).

### Definition of done

| # | Item |
| --- | --- |
| 1 | Solver agent returns converged spectra for the W-grid (Friedrichs) + the δ₀ scan (bridging) + an internal cross-check discretization, scripts + JSON in the repo |
| 2 | Adversarial audit agent independently recomputes with its OWN method, audits the solver's script, per-claim verdicts |
| 3 | Designer comparison against C1-C5, verdicts stated with all numbers |
| 4 | Method note `findings/m8_1_method_note.md` (equations first, eq-to-code map, embedded plots, audit record) |
| 5 | Doc sync staged for REVIEW: canonical § 3 status flip, MODELS.md gravity-cell note, roadmap row, briefing status row |
| 6 | Doc checker exit 0 over touched files; TASK REVIEW presented in terminal |

### Blindspot pass (what could go wrong, checked in advance)

| Blindspot | Mitigation |
| --- | --- |
| The naive discretization silently selects ONE extension (typically Friedrichs), making the extension scan vacuous | the spec DEFINES both realizations via the cone-trace data (u_N, u_D); the bridging family must be implemented as an explicit matching condition; audit checks which realization each solver actually lands on |
| Transverse-sector truncation misses the true λ₁⁺ (the wide band moves the lowest level to a different sector) | the spec requires the low spectrum, not one sector; audit checks sector completeness |
| Weighted-measure errors near the cone (\|f\| → 0) fake convergence | ≥ 3 resolutions + extrapolation required; audit uses a different discretization family |
| A zero mode masquerades as "first positive" (or vice versa) at finite resolution | the spec asks for the lowest 6 eigenvalues INCLUDING any ≤ 0, so the positive level is identified from the full low spectrum |
| The seam (gluing) condition is mis-signed, shifting the anti-periodic sector | audit re-derives the seam handling independently; C1's W-independence on the narrow grid is itself a sensitive detector |
| Independence leak (agent finds the claims in the repo) | agents instructed to read NO markdown; the author's paper lives only in the session scratchpad, not the repo |

### Sub-experiments

| ID | What | Artifact |
| --- | --- | --- |
| S1 | Solver: Friedrichs W-grid + δ₀ scan + internal cross-check | `scripts/m8_1_eigensolve.py` (+ xcheck), `data/m8_1_*.json` |
| S2 | Adversarial audit: own method + script audit | `scripts/m8_1_audit_eigensolve.py`, `data/m8_1_audit_*.json` |
| S3 | Designer comparison + plots | `plots/m8_1_*.png`, this doc § FINDINGS |
| S4 | Method note + sync | `findings/m8_1_method_note.md` |

## DEVIATIONS LOG

(none yet)

## FINDINGS

(pending execution)
