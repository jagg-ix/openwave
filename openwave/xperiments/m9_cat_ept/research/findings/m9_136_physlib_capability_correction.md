# M9.136 Physlib capability correction

This correction supersedes the understated gravity, Maxwell, clock, and LDDL portions of the prior OpenWave assessment.

## Verified complete theorem families

- General-shift ADM metric evolution, symmetry, zero-shift reduction, recovery of `K`, and trace decomposition.
- Weak Hamiltonian and momentum constraint propagation, all-real-time Lipschitz flow, constraint-surface invariance, uniqueness, and finite-time norm control.
- Chain gluing, preservation of encoded global-hyperbolicity conditions, Zorn maximality, and conditional uniqueness of maximal Cauchy developments.
- Intrinsic curved Maxwell geometry, Caticha KG/intrinsic-Maxwell operator equality, and conditional retarded/advanced Green chains.
- Unified conditional-clock generator with reversible and pure dissipative Page--Wootters limits.
- Independent rate calibration, exact exponential occupation orbit, exact KL derivative, Lorentzian denominator with `gamma`, and normalized Cauchy density.

## Narrow remaining gaps

The concrete ADM phase-space vector field is not yet assembled from the full curved covariant-geometry API.

Green existence and microlocal/Hadamard hypotheses remain explicit premises.

The Page--Wootters sector still lacks the explicit loss/gain GKSL map, its semigroup orbit, and the total Hamiltonian constraint.

The relaxation--KL--linewidth chain is not yet one assembled theorem. The exact missing result must prove that the independently calibrated `RateData.gamma` is simultaneously:

- the KL-production coefficient;
- `HWHM`;
- half of `FWHM`;
- and the coefficient defining `T1 = 1/(2 gamma)`.

## ZIL governance status

The verified graph report records 4,589 edges, 21 fully documented predictions, zero circular `requires` chains, and zero adaptive-conformance failures. Remaining debt includes 143 primitive premises, 9 buried weakest-link conditionals, and incomplete metadata on some `derives` entries.

No physical claim is promoted by this correction.
