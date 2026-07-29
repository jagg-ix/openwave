# M9.134 — ADM general-shift correction

## Corrected formal status

The general shift term was not absent from Physlib. The existing declaration

```text
Curvature.DiffeomorphismMetricVariation.metricLieDerivative
```

supplies the coordinate metric Lie derivative

\[
(\mathcal L_\epsilon\gamma)_{mn}
=
\epsilon^s\partial_s\gamma_{mn}
+
\gamma_{ms}\partial_n\epsilon^s
+
\gamma_{ns}\partial_m\epsilon^s.
\]

With \(\epsilon=N\), this is the ADM shift contribution. The user reports the
new formal composition in `AdmMetricEvolutionGeneralShift.lean` at short commit
`31461dc67`, with six axiom-clean and non-vacuous declarations.

OpenWave records that short commit honestly. The full 40-character commit and
source blob could not be retrieved in this execution environment, so they are
not represented as verified pins.

## Executable bridge

`adm_general_shift_m134.py` evaluates

\[
\partial_t\gamma_{ij}
=
-2N K_{ij}
+
(\mathcal L_N\gamma)_{ij}
\]

on a nonconstant periodic metric, a nonzero spatially varying shift, and a
symmetric extrinsic-curvature tensor. The campaign verifies:

- symmetry of the metric rate;
- nontrivial shift contribution;
- exact reduction to \(-2NK\) for zero shift;
- recovery of \(K\) after subtracting Lie drag;
- the trace-free decomposition of the momentum-flux tensor.

## Corrected gravity assessment

The following inspection gaps are closed:

1. general \(K_{ij}\) carrier;
2. transverse-traceless metric mode carrier;
3. general-shift ADM spatial-metric evolution.

The remaining checked limits are narrower:

- no sourced TT propagation equation
  \(\Box h^{TT}_{ij}=-16\pi G T^{TT}_{ij}\);
- no general covariant-derivative operator over an arbitrary curved spatial
  metric. The present Lie derivative is evaluated in a coordinate frame;
- no claim of a complete Einstein Cauchy solver or production numerical
  relativity;
- no independently verified full Physlib source pin in this OpenWave change.

No physical claim or criterion status is promoted by M9.134.
