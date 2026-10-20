import pytest
import os
import tempfile
from app.database.db import Database
from app.services.mapping_engine import MappingEngine
from app.services.requirement_service import RequirementService
from app.models.requirement import Requirement


@pytest.fixture
def temp_engine():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = Database(path)
    engine = MappingEngine(db)
    req_svc = RequirementService(db)
    yield engine, req_svc, db
    db.close()
    if os.path.exists(path):
        os.remove(path)


def test_table_iii_rule_matching(temp_engine):
    engine, req_svc, db = temp_engine
    chars = req_svc.get_all_fr_characteristics()

    # Create test FR with "CRUD / database process"
    crud_char = next(c for c in chars if "CRUD" in c.name)
    req = Requirement(
        project_id=1,
        req_code="FR-TEST-01",
        type="FR",
        title="Uji Pemrosesan Database Rekam Medis",
        description="Pengujian aturan Table III",
        priority="High",
        status="Draft",
        mapping_status="Not Analyzed"
    )
    created = req_svc.create_requirement(req, [crud_char.id])

    suggestions = engine.analyze_requirement(created.id)
    assert len(suggestions) == 1
    s = suggestions[0]
    # According to mapping rules, CRUD matches Performance efficiency
    assert s["quality_characteristic_name"] == "Performance efficiency"
    assert "Mapping Rule" in s["rule_source"] or "Table III" in s["rule_source"]
    assert s["subcharacteristic_name"] == "Time behaviour"
    assert len(s["available_measures"]) >= 1


def test_all_table_iii_mappings(temp_engine):
    engine, req_svc, db = temp_engine
    rules = engine.get_rules()
    assert len(rules) == 8

    expected_pairs = {
        "Runs according to the actor": "Functional suitability",
        "CRUD / database process": "Performance efficiency",
        "File transfer": "Compatibility",
        "Makes tasks easier for users and reduces human error": "Usability",
        "Failure/error detection in the system": "Reliability",
        "Security of transfers, data, access rights, and controls": "Security",
        "Module-related functions: reusability, logging, analysis, modification, testability": "Maintainability",
        "Application configuration and adaptation to other environments, applications, or software": "Portability"
    }

    for r in rules:
        assert r.fr_characteristic_name in expected_pairs
        assert expected_pairs[r.fr_characteristic_name] == r.quality_characteristic_name


def test_confirm_and_reject_mapping(temp_engine):
    engine, req_svc, db = temp_engine
    chars = req_svc.get_all_fr_characteristics()

    sec_char = next(c for c in chars if "Security" in c.name)
    req = req_svc.create_requirement(
        Requirement(project_id=1, req_code="FR-SEC", type="FR", title="Enkripsi", priority="Critical"),
        [sec_char.id]
    )

    created_count = engine.apply_auto_mapping_for_requirement(req.id)
    assert created_count >= 1

    mappings = engine.get_mappings_for_requirement(req.id)
    assert len(mappings) >= 1
    m_id = mappings[0].id

    # Confirm
    confirmed = engine.confirm_mapping(m_id, "Validated by Lead Architect.")
    assert confirmed is True

    updated_m = engine.get_mappings_for_requirement(req.id)[0]
    assert updated_m.status in ("Confirmed", "Terkonfirmasi")

    # Reject
    rejected = engine.reject_mapping(m_id, "Out of module scope.")
    assert rejected is True

    updated_m2 = engine.get_mappings_for_requirement(req.id)[0]
    assert updated_m2.status in ("Rejected", "Ditolak")


def test_apply_rule_suggestion_maps_all_measures(temp_engine):
    engine, req_svc, db = temp_engine
    chars = req_svc.get_all_fr_characteristics()

    sec_char = next(c for c in chars if "Security" in c.name)
    req = req_svc.create_requirement(
        Requirement(project_id=1, req_code="NFR-TEST-SEC", type="NFR", title="Patient Encryption", priority="Critical"),
        [sec_char.id]
    )

    suggestions = engine.analyze_requirement(req.id)
    assert len(suggestions) == 1
    s = suggestions[0]
    assert s["quality_characteristic_name"] == "Security"
    # Available measures for Confidentiality should include SCo-1-G and SCo-2-G
    measure_ids = [m["id"] for m in s["available_measures"]]
    assert len(measure_ids) >= 2

    # Apply rule recommendation
    created_ids = engine.apply_rule_suggestion(
        req_id=req.id,
        fc_id=s["fr_characteristic_id"],
        qc_id=s["quality_characteristic_id"],
        qsc_id=s["subcharacteristic_id"],
        rule_id=s["rule_id"],
        measure_ids=measure_ids,
        rational_note="Applied ISO rule recommendation"
    )

    assert len(created_ids) == len(measure_ids)

    # Check mappings
    mappings = engine.get_mappings_for_requirement(req.id)
    assert len(mappings) == len(measure_ids)
    mapped_measure_ids = {m.quality_measure_id for m in mappings}
    for mid in measure_ids:
        assert mid in mapped_measure_ids

    # Analyze requirement again - should show as Confirmed
    sugs_after = engine.analyze_requirement(req.id)
    assert sugs_after[0]["current_status"] == "Confirmed"


def test_reject_and_reassign_restores_rule_suggestion(temp_engine):
    engine, req_svc, db = temp_engine
    chars = req_svc.get_all_fr_characteristics()
    sec_char = next(c for c in chars if "Security" in c.name)

    req = req_svc.create_requirement(
        Requirement(project_id=1, req_code="FR-REASSIGN", type="FR", title="Auth Test", priority="High"),
        [sec_char.id]
    )

    # 1. Initially it has suggestion with Not Analyzed
    sugs = engine.analyze_requirement(req.id)
    assert len(sugs) == 1
    assert sugs[0]["current_status"] == "Not Analyzed"

    # 2. Reject the rule suggestion
    rejected = engine.reject_rule_suggestion(
        req_id=req.id,
        fc_id=sec_char.id,
        qc_id=sugs[0]["quality_characteristic_id"],
        qsc_id=sugs[0]["subcharacteristic_id"],
        rule_id=sugs[0]["rule_id"]
    )
    assert rejected is True

    sugs_rej = engine.analyze_requirement(req.id)
    assert sugs_rej[0]["current_status"] == "Rejected"

    # 3. User re-assigns the characteristic via Edit Requirement
    req_svc.set_requirement_fr_characteristics(req.id, [sec_char.id])

    # 4. Now the rejected mapping is cleared, and suggestion reappears fresh
    sugs_restored = engine.analyze_requirement(req.id)
    assert len(sugs_restored) == 1
    assert sugs_restored[0]["current_status"] == "Not Analyzed"


def test_delete_rule_mapping(temp_engine):
    engine, req_svc, db = temp_engine
    chars = req_svc.get_all_fr_characteristics()
    sec_char = next(c for c in chars if "Security" in c.name)

    req = req_svc.create_requirement(
        Requirement(project_id=1, req_code="FR-DEL-RULE", type="FR", title="Rule Delete Test", priority="High"),
        [sec_char.id]
    )

    s = engine.analyze_requirement(req.id)[0]
    measure_ids = [m["id"] for m in s["available_measures"]]

    # Apply rule
    engine.apply_rule_suggestion(
        req_id=req.id,
        fc_id=s["fr_characteristic_id"],
        qc_id=s["quality_characteristic_id"],
        qsc_id=s["subcharacteristic_id"],
        rule_id=s["rule_id"],
        measure_ids=measure_ids
    )

    mappings_before = engine.get_mappings_for_requirement(req.id)
    assert len(mappings_before) >= 1

    # Delete rule mapping
    deleted = engine.delete_rule_mapping(req.id, sec_char.id, s["quality_characteristic_id"])
    assert deleted is True

    mappings_after = engine.get_mappings_for_requirement(req.id)
    assert len(mappings_after) == 0

    sugs_after = engine.analyze_requirement(req.id)
    assert len(sugs_after) == 1
    assert sugs_after[0]["current_status"] == "Not Analyzed"



