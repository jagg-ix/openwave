# OpenWave M14 CAT/EPT continuum AdS double-copy model

M14 composes the latest `entropic-physlib-linear-full` continuum PDE and smooth-geometric infrastructure with the existing finite BCJ and AdS/CFT dictionaries. The formal authority is pinned to TIP `ea6c394fcb1d55546d11cd6af3df6556c610d52e`.

## Lineage

| Milestone | Executable result |
| --- | --- |
| M14.1 | causal retarded/advanced Green recurrences, Pauli--Jordan propagator, energy bounds, positive-frequency Hadamard probe kernel |
| M14.2 | pointwise Jacobi numerator sequences, square-summable infinite BCJ direct limit, analytic tail control and generalized-gauge invariance |
| M14.3 | D3/boundary-central-charge normalization of the continuum BCJ limit, GKP source kernel and RT/Complex-Einstein observables |
| M14.4 | compatible nested harmonic slabs, smooth Lorentzian metric direct limit and conditional continuum AdS double-copy closure |

## Formal composition

The formal repository supplies independent theorem surfaces for finite BCJ color replacement and generalized-gauge invariance; D3-normalized finite AdS/BCJ, GKP, RT and Complex-Einstein identities; infinite-dimensional `H¹(R³; C⁴) -> H⁻¹(R³; C⁴)` causal Maxwell Green operators with graph-energy bounds; distributional Hadamard wavefront transport; continuum `L²(X x X)` Liouville kernels and dense maximal pointwise operators; local harmonic-gauge Einstein existence/uniqueness; and a smooth pseudo-Riemannian metric on the Cauchy-development direct limit under explicit compatibility data.

M14 supplies the executable compatibility layer between those surfaces. M14.2 does not rename the finite BCJ theorem as a continuum theorem: it adds a concrete square-summable numerator family, pointwise Jacobi closure, a convergent weighted series and a quantitative tail estimate.

## Claim boundary

The final M14.4 result has status **conditional-model**. It does not claim that every globally hyperbolic metric automatically supplies coercive Green/Hadamard data, that finite BCJ algebra alone proves infinite-graph convergence, that the BCJ amplitude equals RT entropy, or that a global interacting, loop-level or nonperturbative AdS double-copy theorem has been proved.

Visible premises include causal Sobolev closedness/coercivity, microlocal regularity and singularity, numerator summability, weighted gauge orthogonality, D3 compactification data, harmonic Einstein well-posedness and smooth direct-limit compatibility.

## Reproduction

```bash
PYTHONPATH=. python - <<'PY'
from openwave.xperiments.m14_continuum_ads_double_copy import run_m14_model_study
import json
print(json.dumps(run_m14_model_study(), indent=2, sort_keys=True, default=str))
PY
```
