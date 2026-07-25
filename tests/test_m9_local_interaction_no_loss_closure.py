import json
from pathlib import Path


def test_m9_85_frozen_ledger_passes():
    path = Path("openwave/xperiments/m9_cat_ept/research/data/m9_85_local_interaction_no_loss_result.json")
    result = json.loads(path.read_text())
    assert result["passed"]
    assert all(result["acceptance"].values())
    errors = [row["target_interaction_error"] for row in result["rows"]]
    assert errors[2] < errors[1] < errors[0]
    assert result["decision"]["continuum_local_interaction_theorem_proved"] is False
