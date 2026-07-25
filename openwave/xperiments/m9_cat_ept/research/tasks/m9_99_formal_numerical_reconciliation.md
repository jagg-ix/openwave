# M9.99 task details: reconcile OpenWave with current PhysLib equations

## Objective

Complete the highest-value prerequisites for a valid numerical comparison with
`jagg-ix/entropic-physlib-private:entropic-physlib-linear-full`.

## Target A — equation authority

Pin the current formal source blobs and classify every compared term as:

- exact structural overlap;
- conditional bridge;
- formal term missing numerically;
- numerical term outside the formal carrier;
- carrier mismatch;
- parameter mismatch;
- observable-domain mismatch;
- discrete-operator mismatch.

Required findings:

```text
Hartree/Newton term absent from legacy stationary equation
Gaussian coefficient selection not derived by Lean coercivity
D=0.65 and m=1 inconsistent with D=1/(2m)
periodic neutralized Maxwell carrier differs from isolated R3 carrier
spectral matter and centered Maxwell derivatives are not one complex
Dirac center acceleration comparison is not the exact alpha-velocity theorem
rest-frame BMT shadow is outside the moving-packet theorem domain
```

## Target B — shared discrete geometry and mass map

Implement one periodic Fourier differential complex for:

```text
gradient
divergence
curl
Laplacian
Helmholtz projection
Poisson inversion
gauge-covariant Laplacian
```

Acceptance:

```text
curl grad <= 1e-12
div curl <= 1e-12
div grad versus Laplacian <= 1e-12
Fourier null modes = 1
legacy centered null modes > 1
D * 2m = 1
q/m = 2Dq
```

Use the same effective mass in kinetic, convective-current, magnetization-current,
and Pauli-coupling terms.

## Target C — current formal interaction surface

Make the attractive Hartree term executable in the reconciled stationary
operator. Since no unique OpenWave dimensionless `G` has been derived, use an
explicit sweep rather than one hidden value.

Acceptance:

```text
G sweep includes zero control and positive values
all rows use one operator family
Maxwell constraints close for every row
normalization and spin controls remain explicit
no row is called the unique formal or physical target
```

## Target D — correct Dirac observables

Measure the exact relation

```text
d<x_i>/dt = <alpha_i>
```

for pair and self-field control separately and for their interaction difference.
Retain

```text
d<pi_i>/dt versus integral(rho E_i + (j cross B)_i)
```

as the force gate.

Demote these to diagnostics outside the current theorem domain:

```text
d2<x>/dt2 = F/m
rest-frame averaged-field BMT on a moving extended packet
```

## Target E — evidence authority and registration

Add:

- composed reconciliation authority;
- canonical registration schema v6;
- executable runners;
- a ZIL dependency/status graph;
- deterministic tests and adversarial source controls;
- roadmap, briefing, status, and comparison-document updates.

## Status boundary

The task must not claim:

- a selected formal Hartree coupling;
- derivation of one coupled gauge-spinor action;
- a stable charged stationary particle;
- a Foldy--Wouthuysen packet position operator;
- a covariant packet T-BMT theorem;
- physical units or experimental agreement.

The M9 comparison matrix remains `7 validated / 13 partial / 1 negative`.
