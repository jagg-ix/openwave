import openwave.xperiments.m9_cat_ept.model_registration_m108 as registration


def fake_previous():
    return {"schema": "openwave.model-registration.v11", "claim_boundary": {}}


def fake_conformance():
    return {
        "schema": "openwave.m9.models-conformance.v21",
        "formal_authority": {
            "formal_repository": {"current_head": "1" * 40},
            "zil_repository": {"head": "2" * 40},
            "program_health_baseline": {"untested_numerical": 0},
        },
        "evidence": {
            "components": {
                "nonlinear_gravity": {
                    "campaign_passed": True,
                    "constraint_gate": False,
                },
                "coupled_sectors": {
                    "campaign_passed": True,
                    "gates": {
                        "antimatter_annihilation": True,
                        "strong_force": True,
                        "weak_force": True,
                    },
                },
                "candidate_states": {
                    "campaign_passed": True,
                    "gates": {
                        "dark_matter": True,
                        "quarks": True,
                        "baryons": True,
                        "mesons": True,
                    },
                },
            }
        },
        "summary": {},
    }


def test_registration_preserves_failed_gravity_subgate(monkeypatch):
    monkeypatch.setattr(registration, "previous_payload", fake_previous)
    monkeypatch.setattr(registration, "conformance_payload", fake_conformance)
    payload = registration.canonical_registration_payload()
    assert payload["schema"] == "openwave.model-registration.v12"
    assert not payload["m9_106_108"]["nonlinear_gravity_constraint_gate"]
    assert payload["m9_106_108"]["physical_claims_promoted"] == []
