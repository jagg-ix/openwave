# Ceperley rotating-wave equations (the phase-vortex formalism behind Fleury's torus)

> **Provenance.** Two Ceperley papers (both paywalled; local PDFs gitignored, not in the repo):
> - **Primary (Fleury's ref [13]):** P. H. Ceperley, *Rotating Waves*, Am. J. Phys. **60**(10),
>   938-942 (1992), [DOI 10.1119/1.17020](https://doi.org/10.1119/1.17020). The pedagogical paper:
>   cylindrical + spherical + radiating rotating waves, the angular-momentum law, and the
>   circularly-polarized-EM form.
> - **Applications companion:** J. E. Velazco & P. H. Ceperley, *A Discussion of Rotating Wave Fields
>   for Microwave Applications*, IEEE Trans. MTT **41**(2), 330-339 (1993),
>   [DOI 10.1109/22.216476](https://doi.org/10.1109/22.216476). Same formalism, with the full
>   cylindrical-cavity `E,H` field set (§ 4 below).
>
> §§ 1-4 below transcribe the cylindrical formalism (consistent across both papers); § 4b adds the
> AJP-only results (angular-momentum / QM-spin bridge, circularly-polarized EM, spherical, radiating).

Rotating waves are a **third category** of wave fields (alongside traveling and standing): a constant
field profile that rotates in space, "a traveling wave chasing its tail." A rotating wave is a
particular linear combination of two degenerate standing waves.

## 1. Rotating mode from two standing waves

Two identical, φ-shifted, degenerate standing waves (TM`mnp`, z-component shown), Eq (1):

```text
E_z^(1)(r,φ,z,t) = E₀ J_m(k_c r) cos(mφ) cos(k_z z) cos(ωt)
E_z^(2)(r,φ,z,t) = E₀ J_m(k_c r) sin(mφ) cos(k_z z) cos(ωt − δ)
```

with, Eq (2):

```text
ω   = c (k_c² + k_z²)^(1/2)          angular frequency
k_c = u_mn / a                       radial wave number  (u_mn = nth root of J_m)
k_z = p π / l                        z-directed wave number
m   = 0,1,2,…  azimuthal periodicity ;  n = radial nodes ;  p = z periodicity
```

Add the two with `δ = π/2` → a **pure rotating mode**, Eq (3) / complex form Eq (4):

```text
E_z(r,φ,z,t) = E₀ J_m(k_c r) cos(k_z z) cos(ωt − mφ) ,   m = 0,±1,±2,…
E_z(r,φ,z,t) = E₀ J_m(k_c r) cos(k_z z) e^{ j(ωt − mφ) }
```

`+m` rotates counterclockwise, `−m` clockwise (add vs subtract the two standing waves). The
`cos(ωt − mφ)` term is the `cos(ωt − kx)` of a traveling wave, but traveling **around the ring** in φ.

## 2. Rotation rate (the phase vortex)

Track a constant-phase feature, Eq (5)-(7):

```text
ωt − mφ = C   ⇒   m dφ = ω dt   ⇒   ω_rot = dφ/dt = ω / m
```

The field rotates at `ω/m`, the RF frequency divided by the azimuthal index. For `m = 1` the field
rotates once per RF period (Fleury's case: one wavelength around the ring, phase `ψ = φ − ωt`).

## 3. Energy, angular momentum, Poynting

φ-directed time-averaged Poynting vector and z angular momentum (Section III):

```text
P_φ = ½ Re(E × H*)_φ
l_z = r · P_φ / c²            (angular momentum density)
L_z = ∫ l_z dV   =   m U / ω          ← the key result (Eq 13)
```

where `U` is the total field energy. So **`L_z = m U / ω`**: angular momentum is proportional to `m`
even though the rotation rate `ω/m` falls with `m`. For `m = 1`, `L_z = U/ω`.

## 4. Complete cylindrical field set (Section V)

Standing TM`mnp` fields, Eqs (17)-(22):

```text
E_z = E₀ J_m(k_c r) cos(k_z z) cos(mφ) cos(ωt)
E_r = −(k_z/k_c) E₀ J_m'(k_c r) sin(k_z z) cos(mφ) cos(ωt)
E_φ = +(k_z m /(k_c² r)) E₀ J_m(k_c r) sin(k_z z) sin(mφ) cos(ωt)
H_r = −(ω ε₀ m /(k_c² r)) E₀ J_m(k_c r) cos(k_z z) sin(mφ) sin(ωt)
H_φ = −(ω ε₀ / k_c) E₀ J_m'(k_c r) cos(k_z z) cos(mφ) sin(ωt)
H_z = 0
```

(signs / prefactors per the paper; `J_m'` = derivative of the Bessel function.) The rotating-mode
fields follow by the same add-with-`δ=π/2` recipe of § 1, replacing the `cos(mφ)/sin(mφ)·cos(ωt)`
structure with the `e^{j(ωt−mφ)}` phase. TE modes use `u'_mn`, the nth root of `J_m'(u)=0`.

## 4b. AJP-only results (the 1992 paper, Fleury's ref [13])

The pedagogical AJP paper adds four results not in the IEEE companion, all directly load-bearing for
M7.

**(i) Angular momentum + the QM-spin bridge (Eqs 4-8).** From the velocity potential `Φ`, the
z-directed angular momentum of a rotating mode is

```text
L_z = m (U / ω)              (Eq 8;  U = total field energy)
```

Ceperley's own punchline: "in quantum mechanics `U/ω` is equal to the constant `ℏ`, which means `L_z`
only takes on values which are integer multiples of `ℏ`; however, in the classical systems, `U/ω` can
take on a continuum of positive values." He notes Jackson derives the same `L_z = m U/ω` for
classical EM fields. So **rotating-wave spin is `L_z = m·(U/ω)`**, quantized only when `U/ω = ℏ`.

**(ii) Circularly polarized EM as a rotating wave (Eq 15) , the direct Fleury form.** In cylindrical,
complex form:

```text
E_r(r,φ,z,t) = E₀ e^{ i(κz + φ − ωt) }
E_φ(r,φ,z,t) = E₀ e^{ i(κz − φ − ωt + π/2) }
```

the cylindrical equivalent of the Cartesian `E_x = E₀ e^{i(κz−ωt)}`, `E_y = E₀ e^{i(κz−ωt+π/2)}`.
Ceperley: this form is used "because it most clearly shows the rotating wave form having a
`(κz + mφ − ωt)` argument, `m = 1` in this case." **This is exactly Fleury's `e^{i(φ−ωt)}` toroidal
electron at `m = 1`**, and circularly polarized light = spin `±1` photons = a rotating wave (§ VI).

**(iii) Spherical rotating waves (Eqs 16-19).** With spherical Bessel `j_l` + associated Legendre
`P_l^m`:

```text
p(R,θ,φ,t) = A j_l(κR) P_l^m(cosθ) sin(mφ − ωt)            (Eq 16, acoustic)
multipole : A P_l^m(cosθ) h_l^(1)(κR) e^{ i(mφ−ωt) }        (Eq 18, complex)
```

with `m = −l … +l` (the same range as the QM hydrogen `ψ_nlm`, Eq 20). The spherical option if M7
explores a non-toroidal geometry.

**(iv) Radiating / open rotating waves (Eqs 10-12).** For open (un-masked) systems, Hankel functions:

```text
ζ = A H_m^(1)(κr) e^{ i(mφ−ωt) }    (outgoing spiral;  H_m^(2) for incoming)
far field:  ζ ≈ √(2/πκr) · A cos(κr + mφ − ωt − mπ/2 − π/4)
```

a spiral / pinwheel wave traveling in **both** `r` and `φ`. This is the radiating alternative to
Fleury's **closed** Heaviside-masked torus (relevant to whether the electron mode is a closed
resonance or a confined-but-leaky one).

## 5. Relevance to M7 / HydroBoros

| M7 piece | What Ceperley gives | Plan ref |
| --- | --- | --- |
| **Fleury's `e^{i(φ−ωt)}` phase IS Ceperley's Eq 15** | the circularly-polarized-EM rotating wave `E_r = E₀ e^{i(κz+φ−ωt)}` at `m = 1` is literally Fleury's torus ansatz (§ 4b-ii); Fleury cites this paper as [13] | [`m7_background.md § 3`](../research/m7_background.md) (Fleury) |
| **The Bessel envelope = Fleury's own fix** | Fleury's § 5.2 flags the Heaviside mask as unphysical and suggests **Bessel functions**; Ceperley gives the rotating mode with a `J_m(κr)` radial envelope, the smooth replacement | [`m7_background.md § 3`](../research/m7_background.md) · [roadmap](../research/m7_roadmap.md) M7.2 |
| **Spin from rotation: `L_z = mU/ω`** + the QM bridge | a clean angular-momentum law (§ 4b-i); `U/ω = ℏ` quantizes it, the structural origin of Fleury's spin `= ℏ/2` constraint; Jackson derives the same for EM | [`m7_background.md § 3`](../research/m7_background.md) · [roadmap](../research/m7_roadmap.md) M7.6 |
| **Seeder profiles (M7.1)** | the cylindrical `E,H` set (§ 4) + the spherical (§ 4b-iii) + the radiating Hankel (§ 4b-iv) forms = concrete analytic seeds, closed **and** open | [roadmap](../research/m7_roadmap.md) M7.1 |

## Cross-references

- Corpus source table: [`../research/tasks/m7_0_bootstrap.md`](../research/tasks/m7_0_bootstrap.md) (Task-0 table #14/#15); background [`../research/m7_background.md`](../research/m7_background.md)
- Companion theory: [arXiv:2510.22384](https://arxiv.org/abs/2510.22384) (Fleury torus, cites this as [13]),
  [`sato_yamada_beltrami.md`](sato_yamada_beltrami.md) (Beltrami construction)
