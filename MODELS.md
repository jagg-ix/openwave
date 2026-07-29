# OpenWave Models: canonical comparison registry

OpenWave hosts multiple candidate field-theoretic models. Historical M4--M8 results remain in [`MODELS_LEGACY.md`](MODELS_LEGACY.md).

| ID | Model | Current profile | Status authority |
| --- | --- | --- | --- |
| M4--M8 | historical OpenWave models | `MODELS_LEGACY.md` | legacy matrix |
| **M9** | **CAT/EPT Pauli--Hartree--U(1) dynamics** | **`MODELS_M9.md`** | **stable M9.126 evidence aliases plus latest M9.141 integration aliases** |
| **M10** | **CAT/EPT Dirac--Cartan--2I--Compton--Yukawa** | **`MODELS_M10.md`** | **M10.1 executable relativistic carrier and formal equation ledger** |

## M9 stable and latest lineage

The stable compatibility registration and conformance aliases remain at **M9.126** so historical evidence payloads and schemas do not change underneath downstream users.

The latest integrated M9 contract is **M9.141**. It constructs one executable three-dimensional Pauli--Hartree--U(1) carrier on the shared odd-grid Fourier geometry.

## M10 relativistic comparison model

M10.1 constructs a distinct four-spinor model rather than replacing M9. It executes the complete 120-element binary-icosahedral group, lifts it unitarily to the Dirac carrier, couples the field to periodic U(1) potentials, eliminates the algebraic Cartan axial source into a contact term, and uses one Yukawa-generated complex mass to determine the real mass, Compton clock, and CAT/EPT entropy rate.

| Layer | M9 result | M10 result |
| --- | --- | --- |
| matter carrier | two-component Pauli spinor | four-component Dirac spinor |
| internal discrete symmetry | Pauli spin and winding | complete binary icosahedral `2I` action and `A5` bilinear descent |
| gravity interaction | Hartree/Newton potential | algebraic Einstein--Cartan axial contact term |
| mass/clock | effective mass map `D=1/(2m)` | `m_Y=yv/sqrt(2)=hbar omega_C/c^2` |
| irreversible sector | frozen-H squared-gradient functional | complex Yukawa mass with `Im(E_rest)=Sdot_I` |
| gauge sector | static periodic U(1) | static periodic U(1) in the Dirac operator |

M10.2 is the stationary, refinement, perturbation, and covariance closure for this relativistic carrier.
