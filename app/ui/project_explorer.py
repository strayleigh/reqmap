"""
Project Explorer Tree Widget
Displays hierarchical project view, requirements count, and ISO 25023 quality catalog navigation.
Clean, professional presentation without emoji clutter.
"""
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from app.models.project import Project
from app.services.catalog_service import QualityCatalogService


class ProjectExplorerWidget(QWidget):
    filter_requested = Signal(str, str)  # (filter_type, filter_value)
    catalog_item_selected = Signal(int)  # qc_id
    close_requested = Signal()

    def __init__(self, catalog_service: QualityCatalogService, parent=None):
        super().__init__(parent)
        self.catalog_service = catalog_service
        self.current_project: Optional[Project] = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # Explorer Header
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        self.header_title = QLabel("Project Structure")
        self.header_title.setObjectName("explorerHeaderTitle")
        self.header_title.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(160)
        header_row.addWidget(self.header_title)
        header_row.addStretch()

        self.btn_hide = QPushButton("✕")
        self.btn_hide.setObjectName("panelCloseBtn")
        self.btn_hide.setToolTip("Hide Project Explorer (Ctrl+B)")
        self.btn_hide.clicked.connect(self.close_requested.emit)
        header_row.addWidget(self.btn_hide)
        layout.addLayout(header_row)

        # Tree Widget
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(False)
        self.tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree)

    def set_project(self, project: Optional[Project], stats: Optional[Dict[str, Any]] = None):
        self.current_project = project
        self.tree.clear()

        if not project:
            self.header_title.setText("No active project")
            self.header_title.setToolTip("")
            return

        self.header_title.setText(project.name)
        self.header_title.setToolTip(project.name)

        stats = stats or {"fr_count": 0, "nfr_count": 0, "confirmed_mappings": 0, "suggested_mappings": 0}

        # 1. Project Root Node
        proj_node = QTreeWidgetItem(self.tree, [project.name])
        proj_node.setExpanded(True)

        # 2. Requirements Group Node
        reqs_node = QTreeWidgetItem(proj_node, ["Requirements"])
        reqs_node.setData(0, Qt.ItemDataRole.UserRole, ("filter", "all"))
        reqs_node.setExpanded(True)

        fr_node = QTreeWidgetItem(reqs_node, [f"Functional (FR) [{stats.get('fr_count', 0)}]"])
        fr_node.setData(0, Qt.ItemDataRole.UserRole, ("type", "FR Only"))

        nfr_node = QTreeWidgetItem(reqs_node, [f"Non-Functional (NFR) [{stats.get('nfr_count', 0)}]"])
        nfr_node.setData(0, Qt.ItemDataRole.UserRole, ("type", "NFR Only"))

        # 3. ISO/IEC 25023 Catalog Node
        iso_node = QTreeWidgetItem(proj_node, ["ISO/IEC 25023 Quality Catalog"])
        iso_node.setExpanded(True)

        characteristics = self.catalog_service.get_all_characteristics()
        for qc in characteristics:
            subchars = self.catalog_service.get_subcharacteristics(qc.id)
            qc_item = QTreeWidgetItem(iso_node, [f"{qc.iso_number}. {qc.name} ({len(subchars)})"])
            qc_item.setData(0, Qt.ItemDataRole.UserRole, ("catalog", qc.id))

            for sc in subchars:
                measures = self.catalog_service.get_measures_for_subcharacteristic(sc.id)
                sc_item = QTreeWidgetItem(qc_item, [f"{sc.name} ({len(measures)})"])
                sc_item.setData(0, Qt.ItemDataRole.UserRole, ("subcharacteristic", sc.id))

        # 4. Mapping Status Breakdown
        status_node = QTreeWidgetItem(proj_node, ["Mapping Status"])
        status_node.setExpanded(False)

        conf_item = QTreeWidgetItem(status_node, [f"Confirmed [{stats.get('confirmed_mappings', 0)}]"])
        conf_item.setData(0, Qt.ItemDataRole.UserRole, ("mapping", "Confirmed"))

        sug_item = QTreeWidgetItem(status_node, [f"Suggested [{stats.get('suggested_mappings', 0)}]"])
        sug_item.setData(0, Qt.ItemDataRole.UserRole, ("mapping", "Suggested"))

        un_item = QTreeWidgetItem(status_node, ["Not Analyzed"])
        un_item.setData(0, Qt.ItemDataRole.UserRole, ("mapping", "Not Analyzed"))

    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        action_type, val = data
        if action_type in ("type", "mapping", "filter"):
            self.filter_requested.emit(action_type, str(val))
        elif action_type == "catalog":
            self.catalog_item_selected.emit(int(val))
