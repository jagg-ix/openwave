# PhysLib/ZIL reuse map through M9.83

## Repository identities

| Repository | Ref | Revision | Role |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | current `main` after PR #79 | `52bbc8ebfc748386145f55b53d1e662874d8844e` | merged simulation/evidence baseline through M9.80 |
| `jagg-ix/openwave` | `agent/m9-reduce-partials-spin-maxwell-thermal` | current work branch | M9.81--M9.83 criterion closure and partial audit |
| `jagg-ix/entropic-physlib-private` | live `entropic-physlib-linear-full` | `c7283b7fc1ec9ef8acbfd6ed292b34e7ba8d5dd3` | theorem authority and deep-grep base |
| `jagg-ix/entropic-physlib-private` | PR #18 / `agent/m9-criterion-reduction-spin-maxwell-thermal` | `19ef639d0ab849f92fb462d5899817ac1a5c4161` | Pauli exchange, harmonic Maxwell, finite heat-flow bridges and audit |
| `jagg-ix/entropic-physlib-private` | active PR #16 | `83542cc13af0a966a072d90f2082c49785d20c55` | cubic--quintic weak/mild-flow composition |
| `jagg-ix/entropic-physlib-private` | active PR #17 | `2cb1003ede54dc7d8487a8b397a1cacf15728feb` | Lean-backed ZIL evidence lifecycle |

## Reused theorem surfaces

| Criterion | PhysLib source | Reused result |
| --- | --- | --- |
| Spin-1/2 statistics | `FieldStatistics/ExchangeSign.lean` | fermion-fermion exchange phase is `-1`; exchange is involutive |
| Spin-1/2 statistics | `FieldStatistics/PauliExchange.lean` | two-state antisymmetry and identical-state exclusion |
| EM waves | `Electromagnetism/Vacuum/HarmonicWave.lean` | smooth harmonic vacuum solution satisfies Maxwell and is a plane wave |
| EM waves | `HarmonicWaveCertificate.lean` | combined Maxwell/plane-wave criterion theorem |
| Thermal field | `FiniteSpectralHeatFlow.lean` | exact spectral multiplier, semigroup, zero mode, zero diffusivity |
| Thermal field | `SobolevHeatSemigroupDuhamel.lean` | Duhamel/telescoping heat-flow scaffolding |

## Criterion reduction decisions

- `spin_half_statistics`: `validated_in_platform`; dynamical fermion assignment and electron identity remain open.
- `em_waves`: `validated_in_platform`; photon quantization, full CAT/EPT emergence, and empirical calibration remain open.
- `thermal_field`: `validated_in_platform`; microscopic thermodynamics, material calibration, and relativistic transport remain open.

## Remaining status blockers

The other seventeen partials are not missing generic carriers or bookkeeping. They require physical identity/calibration, interacting dynamics, continuum proof, analytic branch identity, or external evidence. ZIL graphs now retain those as explicit boundary nodes rather than allowing criterion validation to imply them.

## Current counts

- validated in-platform: `3`
- partial: `17`
- negative: `1`
- not yet: `0`
- externally physically validated: `0`

Lean remains theorem authority; OpenWave owns executable criterion evidence; ZIL records dependencies, status boundaries, and non-transfer of stronger claims.
