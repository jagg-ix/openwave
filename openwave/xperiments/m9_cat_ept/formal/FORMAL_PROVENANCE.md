# M9 formal provenance

## Purpose

This directory freezes the small part of `entropic-physlib` consumed by the first
M9 OpenWave task. The JSON contract is an equation-to-code manifest, not a copy of
the Lean development and not a substitute proof system.

## Pinned source

| Field | Value |
| --- | --- |
| Repository | `jagg-ix/entropic-physlib-private` |
| Branch | `entropic-physlib-linear-full` |
| Commit | `f6e2b37571086e5ef6de40f77439a5eab468f71f` |
| Lean | `4.29.1` |
| Export date | 2026-07-22 |

The source repository was private at export time. Consequently, a public
OpenWave reader can reproduce the Python conformance run but cannot independently
rebuild the pinned Lean source without access. This limitation is explicit and
must not be described as public end-to-end proof reproducibility.

## Status vocabulary

- `mapped_not_reproved`: the contract identifies a theorem in the pinned source
  and maps it to Python. OpenWave tests the numerical transcription; it does not
  rerun the Lean kernel.
- A passing M9.1 result certifies equation transcription at deterministic test
  points only.
- Particle existence, localization, stability, charge, spin, and a mass spectrum
  remain separate numerical and physical obligations.

## Update rule

Any change to the source branch or commit requires all of the following in the
same pull request:

1. update `entropic_spine_contract.json`;
2. audit each theorem path and hypothesis;
3. rerun `m9_1_formal_contract.py`;
4. update the committed result JSON and method note;
5. record any changed physical interpretation separately from algebraic changes.
