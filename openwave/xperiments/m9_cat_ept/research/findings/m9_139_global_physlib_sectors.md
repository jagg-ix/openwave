# M9.139 — global Physlib sector authority

This milestone was selected from a global inspection of `entropic-physlib-linear-full`, not only the newest commit.

## Target A — retarded gravitational-wave causality

Formal source: `GWRetardedCausalDiamond.lean`, blob `c85fd527c736e6e4f0c4f92ddca6dcf5c34bfa82`.

The retarded source-to-field separation is lightlike and future-directed, placing retarded propagation on the causal-diamond null boundary. OpenWave reproduces the null-form and causal-orientation identities. This does not provide a complete sourced TT Einstein solver.

## Target B — anomalous magnetic-moment links

Formal source: `AnomalousMomentLinks.lean`, blob `51c0e5d9adacf144b6c902ff47d0850071083a0c`.

The Pauli coupling is built from the gauge-invariant Faraday tensor and the magnetic interaction splits as the Dirac term plus anomalous coefficient `(1+a)`. OpenWave checks the plane-wave gauge shift and coefficient split. It does not predict the Schwinger coefficient or a measured lepton anomaly.

## Target C — axial anomaly and eta-prime topology

Formal source: `AxialAnomalyEtaPrimeMass.lean`, blob `bfbaf7766c5b6d8e9929b59166ffa15241465fdf`.

OpenWave checks the exact chiral rotation that removes theta for a massless quark, the trivialized theta-vacuum weight, positivity of the Witten–Veneziano eta-prime mass-squared, and its zero-susceptibility limit. The anomaly equation and topological susceptibility remain inputs rather than path-integral derivations.

## Boundaries

No physical criterion is promoted. The authority does not claim full gravitational-wave dynamics, a numerical anomalous moment, a massive-QCD solution of strong CP, or an ab initio topological susceptibility.
