import pytest
import os
import tempfile
from app.database.db import Database
from app.services.requirement_service import RequirementService
from app.models.requirement import Requirement


@pytest.fixture
def temp_service():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = Database(path)
    svc = RequirementService(db)
    yield svc, db
    db.close()
    if os.path.exists(path):
        os.remove(path)


def test_crud_requirement(temp_service):
    svc, db = temp_service
    chars = svc.get_all_fr_characteristics()
    assert len(chars) == 8

    # Create new FR
    new_req = Requirement(
        project_id=1,
        req_code="FR-999",
        type="FR",
        title="Pembayaran Tagihan Rawat Inap via QRIS",
        description="Pasien dapat membayar biaya tagihan rumah sakit menggunakan QRIS dinamis.",
        priority="High",
        status="Draft",
        mapping_status="Not Analyzed"
    )

    created = svc.create_requirement(new_req, [chars[0].id, chars[1].id])
    assert created.id is not None
    assert created.req_code == "FR-999"
    assert len(created.fr_characteristics) == 2

    # Read
    fetched = svc.get_requirement_by_id(created.id)
    assert fetched is not None
    assert fetched.title == "Pembayaran Tagihan Rawat Inap via QRIS"

    # Update
    fetched.title = "Pembayaran Tagihan Rawat Inap Terintegrasi QRIS & Virtual Account"
    fetched.status = "Under Review"
    updated = svc.update_requirement(fetched)
    assert "Virtual Account" in updated.title
    assert updated.status == "Under Review"

    # Delete
    deleted = svc.delete_requirement(created.id)
    assert deleted is True
    assert svc.get_requirement_by_id(created.id) is None


def test_filtering_and_searching(temp_service):
    svc, db = temp_service
    # Seeded project has 10 requirements
    all_reqs = svc.get_requirements(1)
    assert len(all_reqs) >= 8

    fr_only = svc.get_requirements(1, type_filter="FR")
    assert all(r.type == "FR" for r in fr_only)
    assert len(fr_only) >= 5

    nfr_only = svc.get_requirements(1, type_filter="NFR")
    assert all(r.type == "NFR" for r in nfr_only)
    assert len(nfr_only) >= 2

    search_res = svc.get_requirements(1, search_query="resep")
    assert len(search_res) >= 1
    assert any("resep" in r.title.lower() for r in search_res)


def test_sequential_code_generation(temp_service):
    svc, db = temp_service
    next_fr = svc.generate_next_code(1, "FR")
    assert next_fr.startswith("FR-")
    next_nfr = svc.generate_next_code(1, "NFR")
    assert next_nfr.startswith("NFR-")
