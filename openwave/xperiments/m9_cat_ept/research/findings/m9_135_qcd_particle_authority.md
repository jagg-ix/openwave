# M9.135 — QCD and particle-physics authority

## Correction

The earlier OpenWave assessment understated the particle-physics content of
`jagg-ix/entropic-physlib-private` on `entropic-physlib-linear-full`.
The branch root imports `Physlib.Meta.Zil`, `Physlib.Meta.ZilGraph`, Standard
Model and BSM modules, perturbative and lattice QFT modules, and a dedicated
CAT/EPT QCD hierarchy.

M9.135 records the verified source blobs and adds executable downstream checks
for five theorem families.

## Verified Physlib sources

| Source | Blob |
| --- | --- |
| `Physlib.lean` | `bf9028667305c70e77142e5fd24ec06fadb0d66f` |
| `QCDComplexActionUnification.lean` | `c5d7108ec4781eee3068898d0d844b689230a6fa` |
| `QCDBetaFunctionAsymptoticFreedom.lean` | `ee1d516c44cbb196ada9be69fd9b2e0237211743` |
| `QCDThetaTermStrongCP.lean` | `063732c52c41b7cebfefeeec7d0eeff2b9f4a63b` |
| `TraceAnomalyHadronMass.lean` | `381841338506a6b904077a0fd4435d2b2888b5ca` |

## Executable identities

### One-loop QCD

OpenWave evaluates

```text
b0 = (33 - 2 nf)/(12 pi)
beta(alpha) = -b0 alpha^2
alpha(t) = alpha0/(1 + b0 alpha0 t)
```

and checks that the explicit running solution differentiates to the beta
function, decreases toward the ultraviolet, and generates a positive
transmutation scale.

### Strong CP and complex action

The authority checks

```text
|exp(i theta n)| = 1
exp(i (theta + 2 pi) n) = exp(i theta n)
exp(-i theta n) = conjugate(exp(i theta n))
```

and the CAT/EPT factorization

```text
exp(i theta n - sigma A) = exp(i theta n) exp(-sigma A).
```

### Color counting

For the light `u,d,s` sector,

```text
R = 3[(2/3)^2 + 2(-1/3)^2] = 2,
```

with the SU(3) adjoint count `3^2 - 1 = 8`.

### Trace anomaly

For positive one-loop coefficient, coupling squared, and gluon-condensate
input, the represented anomaly is negative and the associated hadron mass
squared is positive.

## ZIL scope

The Physlib files use ZIL to bind Lean declarations to claims, references,
requirements, maturity, witness lists, and forbidden stronger substitutes.
M9.135 preserves those boundaries rather than converting every satisfied file
contract into a new empirical claim.

## Not established

M9.135 does not claim:

- a numerical hadron spectrum;
- an ab initio gluon condensate;
- a continuum Yang–Mills mass-gap theorem;
- first-principles four-dimensional confinement;
- higher-loop QCD threshold and scheme matching;
- a solution of the small strong-CP angle;
- unique empirical confirmation of CAT/EPT.

## Reproduction

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_135_qcd_particle_authority.py
python -m pytest -vv tests/test_m9_qcd_particle_authority_m135.py
```
