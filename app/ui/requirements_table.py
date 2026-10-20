"""
Requirements Table View Widget.
Primary workspace table showing requirements with sorting, filtering, searching,
solid status badges, and synchronization with the NFR analysis panel.
"""
from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QComboBox, QPushButton, QHeaderView, QLabel,
    QAbstractItemView, QMenu, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from app.models.requirement import Requirement
from app.ui.widgets.status_badge import StatusBadge, create_badge_cell
from app.core.constants import Priority, RequirementStatus, MappingStatus


class RequirementsTableView(QWidget):
    requirement_selected = Signal(object)
    edit_requested = Signal(object)
    delete_requested = Signal(object)
    create_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.requirements: List[Requirement] = []
        self.displayed_requirements: List[Requirement] = []
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(8)

        # Filter and Search Bar
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(8)

        # Search Input
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search code, title, or description...")
        self.search_edit.textChanged.connect(self.apply_filter)
        filter_bar.addWidget(self.search_edit, stretch=3)

        # Type Filter
        self.type_filter_combo = QComboBox()
        self.type_filter_combo.addItems(["All Types", "FR Only", "NFR Only"])
        self.type_filter_combo.currentTextChanged.connect(self.apply_filter)
        filter_bar.addWidget(self.type_filter_combo, stretch=1)

        # Priority Filter
        self.priority_filter_combo = QComboBox()
        self.priority_filter_combo.addItems(["All Priorities"] + [p.value for p in Priority])
        self.priority_filter_combo.currentTextChanged.connect(self.apply_filter)
        filter_bar.addWidget(self.priority_filter_combo, stretch=1)

        # Mapping Status Filter
        self.mapping_filter_combo = QComboBox()
        self.mapping_filter_combo.addItems(["All Mapping Statuses"] + [m.value for m in MappingStatus])
        self.mapping_filter_combo.currentTextChanged.connect(self.apply_filter)
        filter_bar.addWidget(self.mapping_filter_combo, stretch=1)

        main_layout.addLayout(filter_bar)

        # Table Widget
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Type", "Requirement Title",
            "Priority", "Mapping Status", "Mapping Characters"
        ])

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setWordWrap(True)

        # Generous row height (40px) to prevent vertical clipping of tags and allow multi-line title wrapping
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.verticalHeader().setMinimumSectionSize(36)

        # Column sizing with adequate minimum widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.resizeSection(0, 85)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.resizeSection(1, 60)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.resizeSection(2, 300)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.resizeSection(3, 90)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        header.resizeSection(4, 125)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        header.resizeSection(5, 150)

        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.doubleClicked.connect(self.on_double_clicked)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.on_context_menu)

        main_layout.addWidget(self.table)

        # Bottom Count Bar & Editing Hint
        bottom_bar = QHBoxLayout()
        self.count_label = QLabel("Showing 0 of 0 requirements")
        self.count_label.setObjectName("tableStatusLabel")

        self.hint_label = QLabel("💡 Tip: Double-click row, right-click, press Enter / F2, or click 'Edit Requirement' to edit.")
        self.hint_label.setObjectName("tableHintLabel")

        bottom_bar.addWidget(self.count_label)
        bottom_bar.addStretch()
        bottom_bar.addWidget(self.hint_label)
        main_layout.addLayout(bottom_bar)

    def set_requirements(self, reqs: List[Requirement]):
        self.requirements = reqs
        self.apply_filter()

    def apply_filter(self):
        query = self.search_edit.text().strip().lower()
        type_filter = self.type_filter_combo.currentText()
        priority_filter = self.priority_filter_combo.currentText()
        mapping_filter = self.mapping_filter_combo.currentText()

        filtered = []
        for r in self.requirements:
            if type_filter in ("FR Only", "FR Saja") and r.type != "FR":
                continue
            if type_filter in ("NFR Only", "NFR Saja") and r.type != "NFR":
                continue

            if priority_filter not in ("All Priorities", "Semua Prioritas") and r.priority != priority_filter:
                continue

            if mapping_filter not in ("All Mapping Statuses", "Semua Status Pemetaan") and r.mapping_status != mapping_filter:
                continue

            if query:
                in_code = query in r.req_code.lower()
                in_title = query in r.title.lower()
                in_desc = query in (r.description or "").lower()
                if not (in_code or in_title or in_desc):
                    continue

            filtered.append(r)

        self.displayed_requirements = filtered
        self.populate_table()

    def populate_table(self):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.displayed_requirements))

        for row, r in enumerate(self.displayed_requirements):
            # 0: Req ID
            id_item = QTableWidgetItem(r.req_code)
            id_item.setData(Qt.ItemDataRole.UserRole, r.id)
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, id_item)

            # 1: Type Solid Badge
            type_badge = create_badge_cell(r.type, "type")
            self.table.setCellWidget(row, 1, type_badge)

            # 2: Title
            title_item = QTableWidgetItem(r.title)
            title_item.setToolTip(r.title)
            self.table.setItem(row, 2, title_item)

            # 3: Priority Solid Badge
            p_badge = create_badge_cell(r.priority, "priority")
            self.table.setCellWidget(row, 3, p_badge)

            # 4: Mapping Status Solid Badge
            m_badge = create_badge_cell(r.mapping_status, "mapping")
            self.table.setCellWidget(row, 4, m_badge)

            # 5: Mapping Characters summary
            char_codes = [fc.code for fc in r.fr_characteristics]
            chars_str = ", ".join(char_codes) if char_codes else "-"
            char_item = QTableWidgetItem(chars_str)
            char_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 5, char_item)

        self.table.setSortingEnabled(True)
        self.count_label.setText(
            f"Showing {len(self.displayed_requirements)} of {len(self.requirements)} requirements"
        )
        self.adjust_title_column_width()

        if self.displayed_requirements:
            self.table.selectRow(0)
        else:
            self.requirement_selected.emit(None)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_title_column_width()

    def showEvent(self, event):
        super().showEvent(event)
        self.adjust_title_column_width()

    def adjust_title_column_width(self):
        header = self.table.horizontalHeader()
        if header.count() < 6:
            return
        other_widths = (
            header.sectionSize(0) +
            header.sectionSize(1) +
            header.sectionSize(3) +
            header.sectionSize(4) +
            header.sectionSize(5)
        )
        viewport_w = self.table.viewport().width()
        available = viewport_w - other_widths
        if available > 300:
            header.resizeSection(2, available)
        else:
            if header.sectionSize(2) < 300:
                header.resizeSection(2, 300)

    def select_requirement_by_id(self, req_id: int):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole) == req_id:
                self.table.selectRow(row)
                req = self.get_selected_requirement()
                if req:
                    self.requirement_selected.emit(req)
                return

    def get_selected_requirement(self) -> Optional[Requirement]:
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        item = self.table.item(row, 0)
        if not item:
            return None
        req_id = item.data(Qt.ItemDataRole.UserRole)
        for r in self.requirements:
            if r.id == req_id:
                return r
        return None

    def on_selection_changed(self):
        req = self.get_selected_requirement()
        self.requirement_selected.emit(req)

    def on_double_clicked(self, index):
        req = self.get_selected_requirement()
        if req:
            self.edit_requested.emit(req)

    def on_context_menu(self, pos):
        req = self.get_selected_requirement()
        if not req:
            return

        menu = QMenu(self)
        act_edit = menu.addAction(f"Edit {req.req_code}... (F2)")
        act_edit.triggered.connect(lambda: self.edit_requested.emit(req))

        act_del = menu.addAction(f"Delete {req.req_code}... (Del)")
        act_del.triggered.connect(lambda: self.delete_requested.emit(req))

        menu.addSeparator()

        act_copy = menu.addAction(f"Copy Code '{req.req_code}'")
        act_copy.triggered.connect(lambda: QApplication.clipboard().setText(req.req_code))

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_F2):
            req = self.get_selected_requirement()
            if req:
                self.edit_requested.emit(req)
                return
        elif event.key() == Qt.Key.Key_Delete:
            req = self.get_selected_requirement()
            if req:
                self.delete_requested.emit(req)
                return
        super().keyPressEvent(event)
