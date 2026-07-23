# M9.1 task: formal-contract conformance

## Question

Can OpenWave consume a stable, reviewable subset of the CAT/EPT Lean development
without copying the formal repository or turning theorem names into unsupported
particle claims?

## Frozen source

- repository: `jagg-ix/entropic-physlib-private`
- branch: `entropic-physlib-linear-full`
- commit: `f6e2b37571086e5ef6de40f77439a5eab468f71f`
- Lean: `4.29.1`

## Deliverables

1. JSON theorem contract with hypotheses and nonclaims.
2. Pure-Python equation implementations.
3. Deterministic executable report.
4. Pytest coverage for the identities and input validation.
5. Committed method note and result JSON.

## Pass condition

All declared numeric identities pass with absolute error at most `1e-12`, and the
scope documents never promote the result to particle existence or phenomenology.

## Failure condition

Any theorem path, hypothesis, coefficient, sign, or numerical identity differs
from the pinned source, or the executable accepts malformed probability data.
