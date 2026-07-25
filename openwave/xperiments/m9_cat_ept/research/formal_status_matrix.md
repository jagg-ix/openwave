# CAT/EPT formal interface status

Live PhysLib baseline: `829abc1c3a6c947de8aa1cab61194c3d83aa5c4e`.
Constructed-adapter branch: `agent/m9-live-flow-identified-branch-87-89` at `8e0ce0c9a73348dd44fe46151b30cbe41b4bfec5`.

| Interface | Status | Boundary |
| --- | --- | --- |
| Complete continuum `H¹(ℝ³)` carrier | directly proved | genuine infinite-dimensional Bessel-energy carrier |
| Free Schrödinger identity/group/norm/strong continuity | directly proved | exact `L²` evolution, now packaged on the complete `H¹` coordinate |
| Exact nonlinear continuum semiflow for fixed multiplication energy | directly proved | not a claim about every state-dependent spatial Hamiltonian |
| Local Rellich + recentered tails + `L3` to Born `L^(6/5)` and Hartree | directly proved | target model supplies the estimates |
| Cubic--quintic coercivity and weak/mild target interface | directly present on live base | no longer an unavailable PR-only surface |
| Global conservative Born mild-flow certificate | directly present on live base | consumes explicit flow invariants |
| Compact minimizing orbit and uniform orbital stability | directly proved from the certificate | physical identity is separate |
| Identified-target-branch structure and membership theorem | directly present on live base | branch constructor added on adapter branch |
| Free `H¹` unitary-group adapter | added on adapter branch | kernel check pending |
| Identified stable minimizing-branch constructor | added on adapter branch | consumes an actual conservative certificate |
| M9.87 exact free/local flow and split-flow composition | OpenWave executable | group/reverse/mass errors at roundoff |
| M9.88 conservative perturbation campaign | OpenWave executable | mass exact; energy second-order under refinement |
| M9.89 standing-wave branch orbit | OpenWave executable | physical particle identity and external validation remain false |

The stale labels “free H1 flow unavailable,” “compact stable orbit unavailable,” and “identified-branch constructor unavailable” are rejected. The platform matrix is `4 validated / 16 partial / 1 negative`; particle stability is the newly validated literal criterion.
