"""
Main Application Window for ReqMap Desktop Application.
Provides ReqView-inspired professional requirements engineering layout:
- Top Menu and Toolbar
- Left Project Explorer
- Central Requirements Table View
- Right Properties and NFR Analysis Panel
- Bottom Status Bar
"""
import json
import csv
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QStatusBar, QLabel, QToolBar, QMessageBox, QFileDialog, QApplication
)
from PySide6.QtGui import (
    QAction, QKeySequence, QIcon, QPixmap, QPainter, QColor, QPen, QBrush,
    QPainterPath, QFont
)
from PySide6.QtCore import Qt, QRectF, QPointF, QSize

from app.database.db import Database
from app.models.project import Project
from app.models.requirement import Requirement
from app.services.project_service import ProjectService
from app.services.requirement_service import RequirementService
from app.services.catalog_service import QualityCatalogService
from app.services.mapping_engine import MappingEngine
from app.services.target_service import MetricTargetService

from app.ui.project_explorer import ProjectExplorerWidget
from app.ui.requirements_table import RequirementsTableView
from app.ui.nfr_analysis_panel import NFRAnalysisPanel
from app.ui.requirement_dialog import RequirementDialog
from app.ui.catalog_viewer import CatalogViewerDialog
from app.core.theme import LIGHT_THEME_QSS, DARK_THEME_QSS, get_dark_palette, get_light_palette


class MainWindow(QMainWindow):
    def __init__(self, db: Optional[Database] = None):
        super().__init__()
        self.db = db or Database.get_instance()

        # Initialize Services
        self.project_service = ProjectService(self.db)
        self.requirement_service = RequirementService(self.db)
        self.catalog_service = QualityCatalogService(self.db)
        self.mapping_engine = MappingEngine(self.db)
        self.target_service = MetricTargetService(self.db)

        self.current_project: Optional[Project] = None
        self.is_dark_theme = False

        self.setWindowTitle("ReqMap - Desktop Requirements Engineering (ISO/IEC 25023)")
        self.resize(1366, 768)
        self.setMinimumSize(1024, 600)

        self.init_ui()
        self.load_initial_project()

    def init_ui(self):
        # 1. Menu Bar
        self.create_menu_bar()

        # 2. Tool Bar
        self.create_tool_bar()

        # 3. Central Widget with 3-Pane Splitter
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(4, 4, 4, 4)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Project Explorer Tree
        self.explorer = ProjectExplorerWidget(self.catalog_service)
        self.explorer.filter_requested.connect(self.on_explorer_filter)
        self.explorer.catalog_item_selected.connect(self.on_open_catalog_viewer)
        self.main_splitter.addWidget(self.explorer)

        # Center: Requirements Table View
        self.req_table_view = RequirementsTableView()
        self.req_table_view.requirement_selected.connect(self.on_requirement_selected)
        self.req_table_view.edit_requested.connect(self.on_edit_requirement)
        self.req_table_view.delete_requested.connect(self.on_delete_requirement)
        self.main_splitter.addWidget(self.req_table_view)

        # Right: NFR Analysis Panel
        self.nfr_panel = NFRAnalysisPanel(
            mapping_engine=self.mapping_engine,
            catalog_service=self.catalog_service,
            target_service=self.target_service
        )
        self.nfr_panel.mapping_changed.connect(self.on_mapping_changed)
        self.nfr_panel.edit_requirement_requested.connect(self.on_edit_requirement)
        self.main_splitter.addWidget(self.nfr_panel)

        self.saved_left_width = 220
        self.saved_right_width = 460
        self.explorer.close_requested.connect(lambda: self.toggle_left_panel(False))
        self.nfr_panel.close_requested.connect(lambda: self.toggle_right_panel(False))

        # Proportions: Explorer (220px), Table (600px), Right Panel (460px)
        self.main_splitter.setSizes([220, 600, 460])
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setStretchFactor(2, 0)
        central_layout.addWidget(self.main_splitter)
        self.setCentralWidget(central_widget)

        # 4. Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_project_lbl = QLabel("Project: -")
        self.status_counts_lbl = QLabel("FR: 0 | NFR: 0")
        self.status_mapping_lbl = QLabel("Mappings: 0 Confirmed")
        self.status_db_lbl = QLabel("SQLite: Local")

        self.status_bar.addWidget(self.status_project_lbl, 2)
        self.status_bar.addWidget(self.status_counts_lbl, 2)
        self.status_bar.addWidget(self.status_mapping_lbl, 2)
        self.status_bar.addPermanentWidget(self.status_db_lbl)

    def create_menu_bar(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")

        act_export_json = QAction("Export Requirements to JSON...", self)
        act_export_json.triggered.connect(self.on_export_json)
        file_menu.addAction(act_export_json)

        act_export_csv = QAction("Export Requirements to CSV...", self)
        act_export_csv.triggered.connect(self.on_export_csv)
        file_menu.addAction(act_export_csv)

        file_menu.addSeparator()

        act_exit = QAction("Exit", self)
        act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        # Requirements Menu
        req_menu = menubar.addMenu("Requirements")

        act_new_fr = QAction("Add Functional Requirement (FR)...", self)
        act_new_fr.setShortcut("Ctrl+F")
        act_new_fr.triggered.connect(lambda: self.on_create_requirement("FR"))
        req_menu.addAction(act_new_fr)

        act_new_nfr = QAction("Add Non-Functional Requirement (NFR)...", self)
        act_new_nfr.setShortcut("Ctrl+N")
        act_new_nfr.triggered.connect(lambda: self.on_create_requirement("NFR"))
        req_menu.addAction(act_new_nfr)

        req_menu.addSeparator()

        act_edit_req = QAction("Edit Selected Requirement", self)
        act_edit_req.setShortcut("F2")
        act_edit_req.triggered.connect(lambda: self.on_edit_requirement(self.req_table_view.get_selected_requirement()))
        req_menu.addAction(act_edit_req)

        act_del_req = QAction("Delete Selected Requirement", self)
        act_del_req.setShortcut("Delete")
        act_del_req.triggered.connect(lambda: self.on_delete_requirement(self.req_table_view.get_selected_requirement()))
        req_menu.addAction(act_del_req)

        # Catalog Menu
        cat_menu = menubar.addMenu("ISO 25023 Catalog")

        act_view_catalog = QAction("Open ISO/IEC 25023 Quality Catalog...", self)
        act_view_catalog.setShortcut("Ctrl+K")
        act_view_catalog.triggered.connect(lambda: self.on_open_catalog_viewer())
        cat_menu.addAction(act_view_catalog)

        # View Menu
        view_menu = menubar.addMenu("View")

        self.menu_toggle_left = QAction("Show Project Explorer (Sidebar)", self)
        self.menu_toggle_left.setCheckable(True)
        self.menu_toggle_left.setChecked(True)
        self.menu_toggle_left.setShortcut("Ctrl+B")
        self.menu_toggle_left.triggered.connect(self.toggle_left_panel)
        view_menu.addAction(self.menu_toggle_left)

        self.menu_toggle_right = QAction("Show Mapping & Analysis Panel", self)
        self.menu_toggle_right.setCheckable(True)
        self.menu_toggle_right.setChecked(True)
        self.menu_toggle_right.setShortcut("Ctrl+M")
        self.menu_toggle_right.triggered.connect(self.toggle_right_panel)
        view_menu.addAction(self.menu_toggle_right)

        view_menu.addSeparator()

        self.act_toggle_theme = QAction("Switch to Dark Theme", self)
        self.act_toggle_theme.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.act_toggle_theme)

        # Help Menu
        help_menu = menubar.addMenu("Help")

        act_about = QAction("About ReqMap...", self)
        act_about.triggered.connect(self.show_about_dialog)
        help_menu.addAction(act_about)

    def create_sidebar_icon(self, dark: bool = False) -> QIcon:
        icon = QIcon()
        for is_active in [True, False]:
            pm = QPixmap(20, 20)
            pm.fill(Qt.transparent)
            p = QPainter(pm)
            p.setRenderHint(QPainter.Antialiasing)

            frame_color = QColor("#94a3b8" if dark else "#475569")
            panel_color = QColor("#38bdf8" if dark else "#2563eb") if is_active else QColor("#475569" if dark else "#cbd5e1")

            # Outer window frame
            pen = QPen(frame_color, 1.4)
            p.setPen(pen)
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(QRectF(2.0, 3.0, 16.0, 14.0), 2.0, 2.0)

            # Left sidebar section
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(panel_color))
            p.drawRoundedRect(QRectF(3.0, 4.0, 4.5, 12.0), 1.0, 1.0)

            # Divider line separating sidebar from main pane
            p.setPen(QPen(frame_color, 1.2))
            p.drawLine(QPointF(8.0, 3.0), QPointF(8.0, 17.0))

            p.end()
            state = QIcon.State.On if is_active else QIcon.State.Off
            icon.addPixmap(pm, QIcon.Mode.Normal, state)
        return icon

    def create_mapping_panel_icon(self, dark: bool = False) -> QIcon:
        icon = QIcon()
        for is_active in [True, False]:
            pm = QPixmap(20, 20)
            pm.fill(Qt.transparent)
            p = QPainter(pm)
            p.setRenderHint(QPainter.Antialiasing)

            frame_color = QColor("#94a3b8" if dark else "#475569")
            panel_color = QColor("#38bdf8" if dark else "#2563eb") if is_active else QColor("#475569" if dark else "#cbd5e1")

            # Outer window frame
            pen = QPen(frame_color, 1.4)
            p.setPen(pen)
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(QRectF(2.0, 3.0, 16.0, 14.0), 2.0, 2.0)

            # Right panel section
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(panel_color))
            p.drawRoundedRect(QRectF(12.5, 4.0, 4.5, 12.0), 1.0, 1.0)

            # Divider line separating main pane from right panel
            p.setPen(QPen(frame_color, 1.2))
            p.drawLine(QPointF(12.0, 3.0), QPointF(12.0, 17.0))

            p.end()
            state = QIcon.State.On if is_active else QIcon.State.Off
            icon.addPixmap(pm, QIcon.Mode.Normal, state)
        return icon

    def create_add_fr_icon(self, dark: bool = False) -> QIcon:
        pm = QPixmap(20, 20)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)

        fg = QColor("#94a3b8" if dark else "#475569")
        blue_accent = QColor("#38bdf8" if dark else "#2563eb")

        # Document sheet outline with folded top-right corner
        p.setPen(QPen(fg, 1.3))
        path = QPainterPath()
        path.moveTo(2.0, 2.0)
        path.lineTo(11.0, 2.0)
        path.lineTo(15.0, 6.0)
        path.lineTo(15.0, 18.0)
        path.lineTo(2.0, 18.0)
        path.closeSubpath()
        p.drawPath(path)
        p.drawLine(QPointF(11.0, 2.0), QPointF(11.0, 6.0))
        p.drawLine(QPointF(11.0, 6.0), QPointF(15.0, 6.0))

        # Distinct 'FR' label
        font = QFont("Segoe UI", 6, QFont.Weight.Bold)
        p.setFont(font)
        p.setPen(blue_accent)
        p.drawText(QRectF(2, 6, 12, 10), Qt.AlignmentFlag.AlignCenter, "FR")

        # Plus (+) circle badge
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(blue_accent))
        p.drawEllipse(QRectF(11.0, 11.0, 8.5, 8.5))
        p.setPen(QPen(QColor("#ffffff"), 1.4))
        p.drawLine(QPointF(15.2, 12.8), QPointF(15.2, 17.8))
        p.drawLine(QPointF(12.8, 15.2), QPointF(17.8, 15.2))

        p.end()
        return QIcon(pm)

    def create_add_nfr_icon(self, dark: bool = False) -> QIcon:
        pm = QPixmap(20, 20)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)

        fg = QColor("#94a3b8" if dark else "#475569")
        purple_accent = QColor("#c084fc" if dark else "#7c3aed")

        # Document sheet outline with folded top-right corner
        p.setPen(QPen(fg, 1.3))
        path = QPainterPath()
        path.moveTo(2.0, 2.0)
        path.lineTo(11.0, 2.0)
        path.lineTo(15.0, 6.0)
        path.lineTo(15.0, 18.0)
        path.lineTo(2.0, 18.0)
        path.closeSubpath()
        p.drawPath(path)
        p.drawLine(QPointF(11.0, 2.0), QPointF(11.0, 6.0))
        p.drawLine(QPointF(11.0, 6.0), QPointF(15.0, 6.0))

        # Distinct 'NFR' label
        font = QFont("Segoe UI", 5, QFont.Weight.Bold)
        p.setFont(font)
        p.setPen(purple_accent)
        p.drawText(QRectF(1.5, 6, 13, 10), Qt.AlignmentFlag.AlignCenter, "NFR")

        # Plus (+) circle badge
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(purple_accent))
        p.drawEllipse(QRectF(11.0, 11.0, 8.5, 8.5))
        p.setPen(QPen(QColor("#ffffff"), 1.4))
        p.drawLine(QPointF(15.2, 12.8), QPointF(15.2, 17.8))
        p.drawLine(QPointF(12.8, 15.2), QPointF(17.8, 15.2))

        p.end()
        return QIcon(pm)

    def create_edit_icon(self, dark: bool = False) -> QIcon:
        pm = QPixmap(20, 20)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)

        fg = QColor("#cbd5e1" if dark else "#475569")
        pen = QPen(fg, 1.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)

        path = QPainterPath()
        path.moveTo(12.5, 2.5)
        path.lineTo(17.5, 7.5)
        path.lineTo(7.5, 17.5)
        path.lineTo(2.5, 17.5)
        path.lineTo(2.5, 12.5)
        path.closeSubpath()
        p.drawPath(path)
        p.drawLine(QPointF(5.5, 14.5), QPointF(2.5, 17.5))
        p.drawLine(QPointF(10.5, 4.5), QPointF(15.5, 9.5))

        p.end()
        return QIcon(pm)

    def create_delete_icon(self, dark: bool = False) -> QIcon:
        pm = QPixmap(20, 20)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)

        fg = QColor("#f87171" if dark else "#dc2626")
        pen = QPen(fg, 1.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)

        # Handle and lid plate
        p.drawLine(QPointF(8.0, 2.5), QPointF(12.0, 2.5))
        p.drawLine(QPointF(3.5, 5.0), QPointF(16.5, 5.0))

        # Can body
        path = QPainterPath()
        path.moveTo(5.0, 5.0)
        path.lineTo(6.0, 17.5)
        path.lineTo(14.0, 17.5)
        path.lineTo(15.0, 5.0)
        p.drawPath(path)

        # Interior vertical ribs
        p.drawLine(QPointF(8.0, 8.0), QPointF(8.0, 14.5))
        p.drawLine(QPointF(12.0, 8.0), QPointF(12.0, 14.5))

        p.end()
        return QIcon(pm)

    def update_toolbar_icons(self):
        dark = self.is_dark_theme
        if hasattr(self, "act_toggle_left"):
            self.act_toggle_left.setIcon(self.create_sidebar_icon(dark))
        if hasattr(self, "act_fr"):
            self.act_fr.setIcon(self.create_add_fr_icon(dark))
        if hasattr(self, "act_nfr"):
            self.act_nfr.setIcon(self.create_add_nfr_icon(dark))
        if hasattr(self, "act_edit"):
            self.act_edit.setIcon(self.create_edit_icon(dark))
        if hasattr(self, "act_del"):
            self.act_del.setIcon(self.create_delete_icon(dark))
        if hasattr(self, "act_toggle_right"):
            self.act_toggle_right.setIcon(self.create_mapping_panel_icon(dark))

    def create_tool_bar(self):
        toolbar = QToolBar("Actions")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        self.act_toggle_left = toolbar.addAction("")
        self.act_toggle_left.setCheckable(True)
        self.act_toggle_left.setChecked(True)
        self.act_toggle_left.setToolTip("Sidebar")
        self.act_toggle_left.triggered.connect(self.toggle_left_panel)

        toolbar.addSeparator()

        self.act_fr = toolbar.addAction("")
        self.act_fr.setToolTip("Add FR")
        self.act_fr.triggered.connect(lambda: self.on_create_requirement("FR"))

        self.act_nfr = toolbar.addAction("")
        self.act_nfr.setToolTip("Add NFR")
        self.act_nfr.triggered.connect(lambda: self.on_create_requirement("NFR"))

        toolbar.addSeparator()

        self.act_edit = toolbar.addAction("")
        self.act_edit.setToolTip("Edit Requirement")
        self.act_edit.triggered.connect(lambda: self.on_edit_requirement(self.req_table_view.get_selected_requirement()))

        self.act_del = toolbar.addAction("")
        self.act_del.setToolTip("Delete Requirement")
        self.act_del.triggered.connect(lambda: self.on_delete_requirement(self.req_table_view.get_selected_requirement()))

        toolbar.addSeparator()

        self.act_toggle_right = toolbar.addAction("")
        self.act_toggle_right.setCheckable(True)
        self.act_toggle_right.setChecked(True)
        self.act_toggle_right.setToolTip("Mapping Panel")
        self.act_toggle_right.triggered.connect(self.toggle_right_panel)

        self.update_toolbar_icons()

    def load_initial_project(self):
        projects = self.project_service.get_projects()
        if projects:
            self.current_project = projects[0]
            self.refresh_all_views()

    def refresh_all_views(self):
        if not self.current_project:
            return

        stats = self.project_service.get_project_stats(self.current_project.id)

        self.explorer.set_project(self.current_project, stats)

        reqs = self.requirement_service.get_requirements(self.current_project.id)
        self.req_table_view.set_requirements(reqs)

        self.status_project_lbl.setText(f"Project: {self.current_project.name}")
        self.status_counts_lbl.setText(f"FR: {stats['fr_count']} | NFR: {stats['nfr_count']}")
        self.status_mapping_lbl.setText(f"Mappings: {stats['confirmed_mappings']} Confirmed")

    def on_requirement_selected(self, req: Optional[Requirement]):
        self.nfr_panel.set_requirement(req)

    def on_create_requirement(self, req_type: str = "FR"):
        if not self.current_project:
            return
        chars = self.requirement_service.get_all_fr_characteristics()
        suggested_code = self.requirement_service.generate_next_code(self.current_project.id, req_type)

        dlg = RequirementDialog(
            available_chars=chars,
            req=None,
            default_type=req_type,
            suggested_code=suggested_code,
            parent=self
        )
        if dlg.exec():
            new_req = dlg.get_data()
            new_req.project_id = self.current_project.id
            char_ids = dlg.get_selected_char_ids()
            self.requirement_service.create_requirement(new_req, char_ids)
            self.refresh_all_views()

    def on_edit_requirement(self, req: Optional[Requirement]):
        if not req or not self.current_project:
            return

        chars = self.requirement_service.get_all_fr_characteristics()
        dlg = RequirementDialog(
            available_chars=chars,
            req=req,
            parent=self
        )
        if dlg.exec():
            updated = dlg.get_data()
            char_ids = dlg.get_selected_char_ids()
            self.requirement_service.update_requirement(updated, char_ids)
            self.refresh_all_views()
            fresh_req = self.requirement_service.get_requirement_by_id(updated.id)
            if fresh_req:
                self.req_table_view.select_requirement_by_id(fresh_req.id)
                self.nfr_panel.set_requirement(fresh_req)

    def on_delete_requirement(self, req: Optional[Requirement]):
        if not req:
            return
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Delete requirement {req.req_code} ({req.title}) and its associated mappings?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.requirement_service.delete_requirement(req.id)
            self.refresh_all_views()

    def on_mapping_changed(self):
        current_id = self.nfr_panel.current_req.id if self.nfr_panel.current_req else None
        stats = self.project_service.get_project_stats(self.current_project.id)
        self.status_mapping_lbl.setText(f"Mappings: {stats['confirmed_mappings']} Confirmed")
        reqs = self.requirement_service.get_requirements(self.current_project.id)
        self.req_table_view.set_requirements(reqs)
        if current_id:
            fresh_req = self.requirement_service.get_requirement_by_id(current_id)
            if fresh_req:
                self.req_table_view.select_requirement_by_id(fresh_req.id)
                self.nfr_panel.set_requirement(fresh_req)

    def on_explorer_filter(self, filter_type: str, filter_val: str):
        if filter_type == "type":
            self.req_table_view.type_filter_combo.setCurrentText(filter_val)
        elif filter_type == "mapping":
            self.req_table_view.mapping_filter_combo.setCurrentText(filter_val)
        elif filter_type == "filter" and filter_val == "all":
            self.req_table_view.type_filter_combo.setCurrentText("All Types")
            self.req_table_view.mapping_filter_combo.setCurrentText("All Mapping Statuses")
            self.req_table_view.priority_filter_combo.setCurrentText("All Priorities")
            self.req_table_view.search_edit.clear()

    def on_open_catalog_viewer(self, qc_id: Optional[int] = None):
        dlg = CatalogViewerDialog(self.catalog_service, select_qc_id=qc_id, parent=self)
        dlg.exec()

    def toggle_left_panel(self, checked: Optional[bool] = None):
        if checked is None:
            new_state = not self.explorer.isVisible()
        else:
            new_state = bool(checked)

        if not new_state:
            sizes = self.main_splitter.sizes()
            if len(sizes) > 0 and sizes[0] > 0:
                self.saved_left_width = sizes[0]
            self.explorer.hide()
        else:
            self.explorer.show()
            sizes = self.main_splitter.sizes()
            left_w = max(self.saved_left_width, 220)
            center_w = sizes[1] if len(sizes) > 1 else 500
            right_w = sizes[2] if len(sizes) > 2 else 400
            self.main_splitter.setSizes([left_w, center_w, right_w])

        self.act_toggle_left.setChecked(new_state)
        self.menu_toggle_left.setChecked(new_state)

    def toggle_right_panel(self, checked: Optional[bool] = None):
        if checked is None:
            new_state = not self.nfr_panel.isVisible()
        else:
            new_state = bool(checked)

        if not new_state:
            sizes = self.main_splitter.sizes()
            if len(sizes) > 2 and sizes[2] > 0:
                self.saved_right_width = sizes[2]
            self.nfr_panel.hide()
        else:
            self.nfr_panel.show()
            sizes = self.main_splitter.sizes()
            left_w = sizes[0] if len(sizes) > 0 else 220
            center_w = sizes[1] if len(sizes) > 1 else 500
            right_w = max(self.saved_right_width, 380)
            self.main_splitter.setSizes([left_w, center_w, right_w])

        self.act_toggle_right.setChecked(new_state)
        self.menu_toggle_right.setChecked(new_state)

    def toggle_theme(self):
        app = QApplication.instance()
        if self.is_dark_theme:
            app.setPalette(get_light_palette())
            app.setStyleSheet(LIGHT_THEME_QSS)
            self.act_toggle_theme.setText("Switch to Dark Theme")
            self.is_dark_theme = False
        else:
            app.setPalette(get_dark_palette())
            app.setStyleSheet(DARK_THEME_QSS)
            self.act_toggle_theme.setText("Switch to Light Theme")
            self.is_dark_theme = True

        self.update_toolbar_icons()

    def on_export_json(self):
        if not self.current_project:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Requirements to JSON", "requirements.json", "JSON (*.json)")
        if not path:
            return

        reqs = self.requirement_service.get_requirements(self.current_project.id)
        data = []
        for r in reqs:
            mappings = self.mapping_engine.get_mappings_for_requirement(r.id)
            targets = self.target_service.get_targets_for_requirement(r.id)
            data.append({
                "req_code": r.req_code,
                "type": r.type,
                "title": r.title,
                "description": r.description,
                "priority": r.priority,
                "status": r.status,
                "mapping_status": r.mapping_status,
                "mapping_characteristics": [fc.name for fc in r.fr_characteristics],
                "mappings": [
                    {
                        "quality_characteristic": m.qc_name,
                        "subcharacteristic": m.qsc_name,
                        "measure": m.measure_name,
                        "status": m.status,
                        "note": m.rational_note
                    }
                    for m in mappings
                ],
                "targets": [
                    {
                        "measure_id": t.measure_id_code,
                        "measure_name": t.measure_name,
                        "operator": t.operator,
                        "target_value": t.target_value,
                        "target_unit": t.target_unit,
                        "is_dummy": bool(t.is_dummy)
                    }
                    for t in targets
                ]
            })

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        QMessageBox.information(self, "Export Successful", f"Successfully exported {len(data)} requirements to JSON.")

    def on_export_csv(self):
        if not self.current_project:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Requirements to CSV", "requirements.csv", "CSV (*.csv)")
        if not path:
            return

        reqs = self.requirement_service.get_requirements(self.current_project.id)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Code", "Type", "Title", "Description", "Priority", "Status", "Mapping Status", "Mapping Characters"
            ])
            for r in reqs:
                chars = ", ".join([fc.name for fc in r.fr_characteristics])
                writer.writerow([
                    r.req_code, r.type, r.title, r.description, r.priority, r.status, r.mapping_status, chars
                ])

        QMessageBox.information(self, "Export Successful", f"Successfully exported {len(reqs)} requirements to CSV.")

    def show_about_dialog(self):
        QMessageBox.about(
            self,
            "About ReqMap",
            "ReqMap v1.0\n\n"
            "Desktop Requirements Engineering Application with ISO/IEC 25023:2016 Quality Mapping.\n\n"
            "• Functional (FR) and Non-Functional (NFR) Requirements Management\n"
            "• FR-to-NFR Mapping Engine based on Mapping Rules\n"
            "• ISO/IEC 25023 Quality Catalog\n"
            "• Quality Metric Target Value Management\n"
            "• Local SQLite Storage"
        )
