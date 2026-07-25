import json
from pathlib import Path

from openwave.xperiments.m9_cat_ept.branch_identity_certificate import (
    REFERENCE_FINGERPRINT,
    feature_fingerprint,
)


def test_feature_fingerprint_is_deterministic():
    features = {"mass": 1.0, "shell_masses": [0.25, 0.75]}
    assert feature_fingerprint(features) == feature_fingerprint(features)
    assert len(REFERENCE_FINGERPRINT) == 64


def test_m9_86_frozen_ledger_is_fail_closed():
    path = Path("openwave/xperiments/m9_cat_ept/research/data/m9_86_branch_identity_certificate_result.json")
    result = json.loads(path.read_text())
    assert result["passed"]
    assert result["reference"]["fingerprint"] == REFERENCE_FINGERPRINT
    assert result["decision"]["analytic_minimizing_orbit_identified_in_lean"] is False
    assert result["decision"]["external_comparison_admissible"] is False
