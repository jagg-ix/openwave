# M8.1 method note: the certification gate, independent eigensolve of the twisted Möbius Laplacian

> Task: [`../tasks/m8_1_task_details.md`](../tasks/m8_1_task_details.md) (pre-registered
> criteria C1-C5 + the independence protocol). Spec of record:
> [`../m8_theory_canonical.md § 3`](../m8_theory_canonical.md). Status: 🔶 EXECUTING
> (this note is assembled as results land; nothing below § 3 is final until the audit
> record closes).

## 1. Equations first (the operator under test, transcribed from the author's paper)

Source: the author's bedrock paper "Twisted Quantum Modes on a Conic Möbius Band"
(SSRN 6968741, author registry; working text
[first-eigenvalue.md](https://github.com/dmobius3/mode-identity-theory/blob/main/files/framework/files/bedrock/files/first-eigenvalue.md),
shared on [#312](https://github.com/openwave-labs/openwave/discussions/312)).

### 1.1 The surface M(W)

```text
Rectangle:  (y, w) ∈ [0, πR] × [−W, W],   0 < W < πR
Metric:     ds² = dy² + cos²(y/R) dw²          (curvature radius R; Gauss K = 1/R²)
Seam:       (0, w) ~ (πR, −w)                  (the Möbius gluing)
Cone point: y = πR/2 (the transverse fiber collapses; cone angle 2W/R)
Boundary:   the arcs w = ±W, Neumann ∂_w ψ = 0
```

### 1.2 The twisted Laplacian

Sections of the orientation line bundle = functions on the rectangle with the sign
equivariance `ψ(πR, −w) = −ψ(0, w)`. The operator is the Laplace-Beltrami operator

```text
Δψ = ψ_yy + (f′/f) ψ_y + f^(−2) ψ_ww ,   f(y) = cos(y/R),   in L²(|f| dy dw)
```

Transverse Neumann separation: even-in-w modes carry ANTI-periodic longitudinal
conditions, odd-in-w modes periodic. Per sector (transverse eigenvalue μ):

```text
−(|f| u′)′ + (μ/|f|) u = λ |f| u   on (0, πR),   |f| ~ |δ|/R near δ = y − πR/2 = 0
```

### 1.3 The cone-point realizations (the operator's boundary data)

In the transverse-constant channel (μ = 0) both local branches are L², so a
self-adjoint extension must be chosen. Trace data per side:
`u(δ) = u_N ln(|δ|/2R) + u_D + o(1)`.

| Realization | Condition at the cone |
| --- | --- |
| Friedrichs Δ_F | `u_N⁺ = u_N⁻ = 0` (no condition linking u_D⁺, u_D⁻) |
| Bridging A(δ₀) | `ũ_D⁺ = ũ_D⁻` and `u_N⁺ + u_N⁻ = 0`, with `ũ_D = u_D + u_N ln(δ₀/2R)`, δ₀ > 0 |
| All other channels | regular Frobenius branch (sector-regular class) |

### 1.4 The claims under test (the author's Theorems 1.1-1.2, verbatim content)

```text
T1.2 (the gate):  λ₁⁺(W) = 2/R²                    for 0 < W ≤ πR/2
                  λ₁⁺(W) = α₀(α₀+1)/R², α₀ = πR/2W  for πR/2 < W < πR
                  doubly degenerate at W = πR/2;
                  SHARED by Δ_F and by A(δ₀) for every δ₀ > 2R/e.
T1.1:             every self-adjoint extension has bottom ≤ 0;
                  Δ_F bottom = 0 (discontinuous piecewise-constant zero mode);
                  A(δ₀) has one cone-localized bound state
                  λ_b(δ₀) = −4e^(−2γ)/δ₀² · (1 + O(δ₀²/R²)).
```

Pre-registered pass/fail per claim: [`../tasks/m8_1_task_details.md`](../tasks/m8_1_task_details.md).

## 2. Equation-to-code map

🔶 pending (filled when the solver + audit scripts land; blob/main permalinks per the
frozen-task convention).

## 3. Results

🔶 pending (solver + audit running under the independence protocol).

## 4. Not computed

🔶 pending.

## 5. Adversarial audit record

🔶 pending.
