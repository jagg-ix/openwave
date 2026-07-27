# M9 maturity-based roadmap

M9.100--M9.121 established multi-axis maturity, reduced gravity and gauge carriers, finite spectra and response, controlled refinement, CPTP model-unit decay, blind commitment, and fail-closed physical-promotion governance. M9.122 makes the external-evidence path executable without fabricating evidence.

| Task | Target | State |
| --- | --- | --- |
| M9.100--M9.121 | Formal/numerical carriers, model-unit decay, commitment, and promotion governance | DONE; PHYSICAL AXES SEPARATE |
| M9.122a | Canonical evidence package with artifact digests, commitment ordering, target-leakage checks, and incomplete live template | DONE; NO REAL PACKAGE INGESTED |
| M9.122b | Blinded evaluator that blocks before reveal and computes preregistered metrics only for a valid package | DONE; SYNTHETIC FIXTURE ONLY |
| M9.122c | Independent transition-identity bridge requiring discriminants and negative controls | DONE; OBSERVED IDENTITY OPEN |
| M9.123 | Ingest one real independent anchor, reveal a precommitted holdout, and execute one externally identified transition test without refitting | NEXT; EXTERNAL INPUT REQUIRED |

## Current decision

```text
external-evidence package schema          constructed
artifact integrity checks                 constructed
commitment-before-reveal check            constructed
target-leakage rejection                  constructed
blinded external evaluator                constructed
identity-bridge contract                  constructed
real independent anchor                   missing
real held-out observation                 not revealed
observed transition identity              open
external validation                       open
```

## Current upstream authorities

```text
OpenWave main base    0b25d14e0e14a30b4b4ac46a95e9de4c72083134
Physlib merged branch master
Physlib merged head   80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef
Physlib root          f953c09c428eb83d9894c1944e1fd44a7ffe95a1
development branch    private/entropic-physlib-linear-full
public zil-lean       c671f02d8b6dcf7ba689afc86477ff7e35465c35
```

M9.123 cannot be closed by synthetic fixtures, another algebraic identity, or another finite diagonalization. It requires a real evidence package whose sources are independent of the target observables.
