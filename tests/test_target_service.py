import pytest
import os
import tempfile
from app.database.db import Database
from app.services.target_service import MetricTargetService
from app.services.catalog_service import QualityCatalogService


@pytest.fixture
def temp_target_service():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = Database(path)
    tgt_svc = MetricTargetService(db)
    cat_svc = QualityCatalogService(db)
    yield tgt_svc, cat_svc, db
    db.close()
    if os.path.exists(path):
        os.remove(path)


def test_target_configuration(temp_target_service):
    tgt_svc, cat_svc, db = temp_target_service
    measures = cat_svc.get_measures_for_characteristic(2)  # Performance efficiency
    assert len(measures) >= 1
    m = measures[0]

    # Set user target
    target = tgt_svc.set_target(
        req_id=1,
        quality_measure_id=m.id,
        operator="<=",
        target_value="250",
        target_unit="ms",
        rational_note="Target latensi SLA API resep",
        is_dummy=1
    )

    assert target.operator == "<="
    assert target.target_value == "250"
    assert target.target_unit == "ms"
    assert target.is_dummy == 1

    # Verify retrieval
    targets = tgt_svc.get_targets_for_requirement(1)
    found = next((t for t in targets if t.quality_measure_id == m.id), None)
    assert found is not None
    assert found.target_value == "250"

    # Reset to dummy default
    reset_t = tgt_svc.reset_to_dummy_target(1, m.id)
    assert reset_t.target_value == "300"
    assert reset_t.is_dummy == 1
