# M9.109 Newton-G and Compton-clock scope audit

## Corrected verdict

The species calculation does **not** contradict any current Lean theorem. It confirms the algebraic identity

```text
omega_C(m) = m*c^2/hbar
hbar*c/m^2 = c^5/(hbar*omega_C(m)^2)
```

for every audited mass.

What fails is the additional physical hypothesis that every unequal particle Compton clock can independently be the same universal gravity anchor.

For positive masses `m1` and `m2`,

```text
hbar*c/m1^2 = hbar*c/m2^2
```

implies

```text
m1 = m2.
```

Therefore unequal electron, muon, and proton masses cannot all define one universal measured `G` through the same species-specific substitution.

## Lean theorem scope

| Lean surface | What is proved | Load-bearing hypotheses or definitions | What is not proved |
| --- | --- | --- | --- |
| `FrequencyTrinity.comptonFrequency` | `omega_C = m*c^2/hbar` | selected `m`, `c`, `hbar` | mass value, microscopic oscillator, Newton `G` |
| `zitterbewegung_rest_eq_two_compton` | rest-frame Dirac splitting is `2*omega_C` | frequency definitions, nonnegative mass | experimental resonance or particle identity |
| `EntropicAgreement.entropicPhysicalTimeAdvance_eq_physicalTime` | calibrated entropic phase reads supplied proper time | `Delta S_I = hbar*omega_0*Delta tau_phys` and an independent phase clock | the action-rate law or universal validity for every entropy arrow |
| `comptonAnchored_newtonG_eq_from_clockFrequency` | `hbar*c/m^2 = c^5/(hbar*omega_C^2)` | Compton frequency definition and positive parameters | equality with measured universal `G`, anchor selection, species independence |
| `newtonG_from_comptonCellBits` | the `G`-free Compton-cell expression reduces to `hbar*c/m^2` | Compton-cell screen and an independent mass scale | numerical `G` without an anchor or dynamical selection of that scale |
| `higgs_clock_three_origins` | equivalent clock forms after three masses are identified | `m_Yukawa = m_horizon` and `m_Yukawa = m_topological` | those equalities, the lepton hierarchy, or species data |

The no-go audit rejects no theorem. It rejects only:

```text
every-particle-Compton-clock-is-the-universal-gravity-anchor
```

## Planck selection

The effective coupling

```text
G_eff(m) = hbar*c/m^2
```

matches the observed Newton coupling exactly when

```text
m = sqrt(hbar*c/G_N),
```

which is the Planck mass. This inversion uses measured `G_N`; it is a consistency control, not a prediction.

The earlier Compton-cell theorem already states the same structural fact in cell-count language: Planck-cell and Compton-cell tilings coincide at the Planck-mass identification.

## Paper-evidence scope

| Source | Directly supports | Does not directly support |
| --- | --- | --- |
| Lan et al., *Science* 339 (2013) | an oscillator synchronized to a subharmonic of the atomic Compton frequency; mass-time metrology | `Delta S_I = m*c^2 Delta tau`, Newton `G` from that clock, or a universal microscopic oscillator interpretation |
| Parker et al., *Science* 360 (2018) | cesium recoil-frequency and precision `h/m` metrology used to determine `alpha` | direct ticking at `omega_C`, the CAT/EPT action-rate law, or `G = hbar*c/m_Cs^2` |
| Margalit et al., *Science* 349 (2015) | a two-spin-state self-interfering clock; engineered differential ticking changes visibility | a Compton-frequency clock, gravitational redshift measurement, imaginary-action law, or Newton `G` |
| Wolf et al., *Class. Quantum Grav.* 28 (2011) | a major theoretical objection to interpreting ordinary closed atom interferometers as Compton-redshift clocks | a rejection of all Compton-referenced metrology or a test of CAT/EPT imaginary-action dynamics |

Paper edges must attach to the narrowest supported subclaim. None of these papers validates the complete chain

```text
Delta S_I = m*c^2*Delta tau
    -> entropic time = physical proper time
    -> particle Compton clock supplies universal gravity anchor
    -> measured Newton G.
```

## Untested CAT/EPT premises

The following remain experimentally or dynamically open:

1. `Delta S_I = m*c^2*Delta tau_phys` for the relevant physical clock.
2. Selection of one universal gravitational mass or frequency independently of measured `G`.
3. Derivation of that anchor value from CAT/EPT dynamics rather than insertion or inversion.
4. Derivation, rather than assumption, of the Yukawa/horizon/topological mass coincidence.

## CODATA interpretation audit

The mass and clock paths agree for each species, confirming the formal identity. Relative to measured `G_N`:

| Clock | `G_eff/G_N` |
| --- | ---: |
| electron | about `5.71e44` |
| muon | about `1.34e40` |
| proton | about `1.69e38` |

These numbers do not falsify Lean. They show that ordinary particle masses are not the Planck anchor required by the universal-`G` identification.

## Current decision

- Lean algebraic identities: **preserved**.
- Current Lean theorem falsified: **no**.
- every-particle universal-clock hypothesis: **rejected**.
- Compton-cell `G_eff(m)` interpretation: **mass-dependent candidate coupling**.
- equality with measured `G_N`: **Planck-anchor condition**.
- independent Planck-scale anchor: **open**.
- full paper validation of CAT/EPT `G` chain: **absent**.
- calibrated injection into gravity campaigns: **blocked**.

## Reproduction

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_109_formal_G_authority.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_109_theorem_evidence_scope.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_109_G_clock_universality.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_109_G_anchor_protocol.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_109_current_registration.py
```

## Promotion rule

A physical prediction of `G_N` requires one universal-gravity mass or frequency derived or independently measured without using `G_N`, plus an explicit SI-to-OpenWave unit map. The same frozen dimensionless coupling must then feed both weak and nonlinear gravity.

Natural-unit closure at `hbar = c = m = omega = sigma0 = G = 1` is not external calibration.
