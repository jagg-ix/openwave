# M9.36 task: adaptive refinement and propagated error budgets

Allocate total numerical tolerance across temporal, spatial, domain-truncation,
and coupling-iteration channels. Refine each component until its allocation is
met, propagate the component bounds, fingerprint the plan, and fail explicitly
when refinement limits are insufficient.

The benchmark concerns numerical error, not physical uncertainty.
