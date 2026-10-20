import os
import pytest
from PySide6.QtWidgets import QApplication
from app.database.db import Database
from app.ui.main_window import MainWindow
from app.ui.target_dialog import MetricTargetDialog
from app.services.catalog_service import QualityCatalogService

# Use offscreen platform for headless Qt testing
os.environ["QT_QPA_PLATFORM"] = "offscreen"


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_main_window_components(qapp):
    db = Database.get_instance()
    window = MainWindow(db)

    assert window.windowTitle().startswith("ReqMap")
    assert window.explorer is not None
    assert window.req_table_view is not None
    assert window.nfr_panel is not None

    # Check that requirements are populated in table
    assert window.req_table_view.table.rowCount() >= 8

    # Find and select an FR row
    fr_row = None
    nfr_row = None
    for r in range(window.req_table_view.table.rowCount()):
        badge = window.req_table_view.table.cellWidget(r, 1)
        if badge and badge.text() == "FR" and fr_row is None:
            fr_row = r
        elif badge and badge.text() == "NFR" and nfr_row is None:
            nfr_row = r

    assert fr_row is not None
    assert nfr_row is not None

    # Test selecting FR
    window.req_table_view.table.selectRow(fr_row)
    selected_req = window.req_table_view.get_selected_requirement()
    assert selected_req is not None
    assert selected_req.type == "FR"

    # Verify NFR panel loaded the selected requirement and enabled edit button
    assert window.nfr_panel.current_req.id == selected_req.id
    assert window.nfr_panel.btn_edit_req.isEnabled() is True
    assert window.nfr_panel.btn_add_target is not None

    # Test selecting NFR
    window.req_table_view.table.selectRow(nfr_row)
    selected_nfr = window.req_table_view.get_selected_requirement()
    assert selected_nfr is not None
    assert selected_nfr.type == "NFR"
    assert window.nfr_panel.current_req.id == selected_nfr.id
    assert window.nfr_panel.btn_edit_req.isEnabled() is True

    # Toggle theme (initial is Light mode: is_dark_theme == False)
    assert window.is_dark_theme is False
    window.toggle_theme()
    assert window.is_dark_theme is True
    window.toggle_theme()
    assert window.is_dark_theme is False

    # Test toggling Left Panel (Explorer)
    window.show()
    assert window.explorer.isVisible() is True
    window.toggle_left_panel(False)
    assert window.explorer.isVisible() is False
    window.toggle_left_panel(True)
    assert window.explorer.isVisible() is True

    # Test toggling Right Panel (Mapping & Analysis)
    assert window.nfr_panel.isVisible() is True
    window.toggle_right_panel(False)
    assert window.nfr_panel.isVisible() is False
    window.toggle_right_panel(True)
    assert window.nfr_panel.isVisible() is True

    window.close()


def test_metric_target_dialog_cascade(qapp):
    db = Database.get_instance()
    catalog_service = QualityCatalogService(db)

    dlg = MetricTargetDialog(catalog_service=catalog_service)
    assert dlg.qc_combo.count() == 8
    assert dlg.qsc_combo.count() > 0
    assert dlg.qm_combo.count() > 0

    data = dlg.get_target_data()
    assert data["quality_measure_id"] is not None
    assert data["operator"] in ["<=", ">=", "=", "<", ">", "range"]
    assert len(data["target_value"]) > 0

    dlg.close()
