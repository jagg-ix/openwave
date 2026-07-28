# M9.131 — Existing-data import authority

M9.131 closes the final methodology layer before real data ingestion:

1. source manifests require DOI/URI, SHA-256, artifact kind, access status, extractor, and extraction version;
2. dataset adapters map relational-conditioning and binary-relaxation tables into the canonical M9.130 row schema;
3. leakage audits enforce disjoint calibration/holdout IDs, calibration-only fitting, retained negative results, and no per-carrier refitting.

Real source artifacts, verified digests, and held-out reports remain required for physical promotion.
