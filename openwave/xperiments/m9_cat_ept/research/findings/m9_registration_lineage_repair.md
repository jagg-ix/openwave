# M9 registration-lineage repair

The moving `model_conformance_current` and `model_registration_current` aliases remain on M9.126. Historical M9.96, M9.97, and M9.98 consumers now import explicit versioned modules instead of traversing those moving aliases.

This removes recursive registration evaluation while preserving the historical schemas, criterion counts, claim boundaries, and the current M9.126 platform entry points.

No physical criterion is promoted by this repair.
