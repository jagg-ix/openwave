# OpenWave M12 CAT/EPT particle-zoo coverage model

M12 is an executable coverage layer over the particle, electroweak, lepton,
neutrino, hadron, and QCD theorem surfaces in `entropic-physlib-linear-full`.
It does not replace M9--M11.

## Lineage

| Milestone | Executable result |
| --- | --- |
| M12.1 | all 17 Standard-Model particle types, 12 gauge states, CPT pairing, additive `(Q,B,L)` and flavor selection rules |
| M12.2 | tree-level electroweak mass matrix, couplings, cross sections and widths; charged-lepton identities; supplied-parameter PMNS vacuum oscillations |
| M12.3 | six-flavor quark data, named-hadron flavor composition, Gell-Mann--Nishijima, SU(3) mass relations, one-loop `alpha_s` running, and M10 QCD integration |

## Claim boundary

M12 separates four classes of statements:

1. **Exact finite structure:** particle counts, charges, spins, CPT conjugation,
   additive conservation and flavor composition.
2. **Exact consequences of supplied models:** tree-level electroweak relations,
   PMNS unitarity, SU(3) mass-formula identities and one-loop QCD running.
3. **Empirical inputs:** PDG masses, lifetimes, branching fractions, gauge
   couplings, PMNS angles and mass splittings.
4. **Not claimed:** radiative corrections, decay matrix elements, first-principles
   Yukawa values, first-principles quark/hadron masses, or collider-grade cross
   sections.

## Formal authority

The ledgers pin `jagg-ix/entropic-physlib-private`, branch
`entropic-physlib-linear-full`, TIP
`8bafa9ab93cbb39e85909fc3837bb4b6e0dec748`.

## Reproduction

```bash
PYTHONPATH=. python - <<'PY'
from openwave.xperiments.m12_particle_zoo import run_particle_zoo_model_study
import json
print(json.dumps(run_particle_zoo_model_study(), indent=2, sort_keys=True, default=str))
PY
```
