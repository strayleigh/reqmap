"""
NFR Analysis & Mapping Panel.
Displays FR/NFR description, selected mapping characters, rule suggestions,
ISO 25023 subcharacteristics, quality measures, targets, and manual mapping actions.
Minimal, clean, and academic-grade design in English.
"""
from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QScrollArea, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QComboBox, QDialog, QFormLayout, QTextEdit,
    QAbstractItemView
)
from PySide6.QtGui import QUndoStack
from PySide6.QtCore import Qt, Signal
from app.models.requirement import Requirement
from app.models.mapping import RequirementMapping
from app.models.catalog import QualityMeasure
from app.models.target import MeasureTarget
from app.services.mapping_engine import MappingEngine
from app.services.catalog_service import QualityCatalogService
from app.services.target_service import MetricTargetService
from app.ui.widgets.status_badge import StatusBadge, create_badge_cell
from app.ui.target_dialog import MetricTargetDialog
from app.core.undo_manager import LambdaUndoCommand


class ManualMappingDialog(QDialog):
    """Dialog to manually add a custom FR/NFR-to-ISO mapping."""
    def __init__(self, catalog_service: QualityCatalogService, parent=None):
        super().__init__(parent)
        self.catalog_service = catalog_service
        self.setWindowTitle("Add Manual ISO Quality Mapping")
        self.resize(520, 360)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(14, 14, 14, 14)
        form = QFormLayout()
        form.setSpacing(8)

        self.qc_combo = QComboBox()
        self.qsc_combo = QComboBox()
        self.qm_combo = QComboBox()
        self.note_edit = QTextEdit()
        self.note_edit.setPlaceholderText("Rationale for selecting this quality characteristic...")
        self.note_edit.setMaximumHeight(80)

        self.characteristics = self.catalog_service.get_all_characteristics()
        for qc in self.characteristics:
            self.qc_combo.addItem(f"{qc.code} - {qc.name}", qc.id)

        self.qc_combo.currentIndexChanged.connect(self.on_qc_changed)
        self.qsc_combo.currentIndexChanged.connect(self.on_qsc_changed)

        form.addRow("Quality Characteristic (ISO):", self.qc_combo)
        form.addRow("Subcharacteristic:", self.qsc_combo)
        form.addRow("Quality Metric / Measure:", self.qm_combo)
        form.addRow("Rational Note / Justification:", self.note_edit)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Save")
        btn_save.setObjectName("primaryButton")
        btn_save.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

        if self.characteristics:
            self.on_qc_changed(0)

    def on_qc_changed(self, index: int):
        self.qsc_combo.clear()
        if index < 0 or index >= len(self.characteristics):
            return
        qc_id = self.qc_combo.currentData()
        subchars = self.catalog_service.get_subcharacteristics(qc_id)
        for sc in subchars:
            self.qsc_combo.addItem(f"{sc.code} - {sc.name}", sc.id)
        if subchars:
            self.on_qsc_changed(0)

    def on_qsc_changed(self, index: int):
        self.qm_combo.clear()
        qsc_id = self.qsc_combo.currentData()
        if not qsc_id:
            return
        measures = self.catalog_service.get_measures_for_subcharacteristic(qsc_id)
        for m in measures:
            self.qm_combo.addItem(f"{m.measure_id} - {m.name}", m.id)

    def get_selection(self) -> Dict[str, Any]:
        return {
            "qc_id": self.qc_combo.currentData(),
            "qsc_id": self.qsc_combo.currentData(),
            "qm_id": self.qm_combo.currentData(),
            "rational_note": self.note_edit.toPlainText().strip()
        }


class NFRAnalysisPanel(QWidget):
    mapping_changed = Signal()
    edit_requirement_requested = Signal(object)
    close_requested = Signal()

    def __init__(
        self,
        mapping_engine: MappingEngine,
        catalog_service: QualityCatalogService,
        target_service: MetricTargetService,
        undo_stack: Optional[QUndoStack] = None,
        parent=None
    ):
        super().__init__(parent)
        self.mapping_engine = mapping_engine
        self.catalog_service = catalog_service
        self.target_service = target_service
        self.undo_stack = undo_stack
        self.current_req: Optional[Requirement] = None

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(8)

        # Header: Selected Requirement Info with explicit Edit Button
        self.header_frame = QFrame()
        self.header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(self.header_frame)
        header_layout.setSpacing(4)

        top_row = QHBoxLayout()
        self.req_code_lbl = QLabel("Select Requirement")
        self.req_code_lbl.setStyleSheet("font-size: 15px; font-weight: 600;")
        self.req_badge = StatusBadge("Not Analyzed", "mapping")

        self.btn_edit_req = QPushButton("Edit Requirement")
        self.btn_edit_req.setObjectName("primaryButton")
        self.btn_edit_req.setStyleSheet("font-size: 12px; padding: 4px 12px; font-weight: 600;")
        self.btn_edit_req.setToolTip("Edit requirement details, priority, status, or mapping characters")
        self.btn_edit_req.clicked.connect(self.on_edit_req_clicked)
        self.btn_edit_req.setEnabled(False)

        self.btn_hide = QPushButton("✕")
        self.btn_hide.setObjectName("panelCloseBtn")
        self.btn_hide.setToolTip("Hide Mapping & Analysis Panel (Ctrl+M)")
        self.btn_hide.clicked.connect(self.close_requested.emit)

        top_row.addWidget(self.req_code_lbl)
        top_row.addWidget(self.req_badge)
        top_row.addStretch()
        top_row.addWidget(self.btn_edit_req)
        top_row.addWidget(self.btn_hide)
        header_layout.addLayout(top_row)

        self.req_title_lbl = QLabel("Select a requirement row in the table to review mappings or edit.")
        self.req_title_lbl.setWordWrap(True)
        self.req_title_lbl.setStyleSheet("font-size: 13px;")
        header_layout.addWidget(self.req_title_lbl)

        self.char_tags_lbl = QLabel("Mapping Characters: -")
        self.char_tags_lbl.setWordWrap(True)
        self.char_tags_lbl.setStyleSheet("font-size: 12px;")
        header_layout.addWidget(self.char_tags_lbl)

        main_layout.addWidget(self.header_frame)

        # Tabs for Analysis Sections
        self.tabs = QTabWidget()

        # Tab 1: Mapping Rules (formerly Aturan Table III)
        self.suggestions_tab = QWidget()
        sug_layout = QVBoxLayout(self.suggestions_tab)
        sug_layout.setContentsMargins(6, 6, 6, 6)
        sug_layout.setSpacing(6)

        self.sug_scroll = QScrollArea()
        self.sug_scroll.setWidgetResizable(True)
        self.sug_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.sug_container = QWidget()
        self.sug_container_layout = QVBoxLayout(self.sug_container)
        self.sug_container_layout.setSpacing(8)
        self.sug_container_layout.setContentsMargins(2, 2, 2, 2)
        self.sug_scroll.setWidget(self.sug_container)
        sug_layout.addWidget(self.sug_scroll)

        # Action Bar in Suggestions Tab: Manual Mapping button
        sug_actions = QHBoxLayout()
        self.btn_manual_map = QPushButton("+ Add Custom Mapping")
        self.btn_manual_map.setObjectName("primaryButton")
        self.btn_manual_map.setToolTip("Manually map this requirement to any ISO/IEC 25023 quality characteristic and metric")
        self.btn_manual_map.clicked.connect(self.on_add_manual_mapping)

        sug_actions.addStretch()
        sug_actions.addWidget(self.btn_manual_map)
        sug_layout.addLayout(sug_actions)

        self.tabs.addTab(self.suggestions_tab, "Mapping Rules")

        # Tab 2: Quality Targets
        self.targets_tab = QWidget()
        tgt_layout = QVBoxLayout(self.targets_tab)
        tgt_layout.setContentsMargins(6, 6, 6, 6)
        tgt_layout.setSpacing(8)

        # Action Bar at top of Tab 2
        tgt_top_bar = QHBoxLayout()
        tgt_info = QLabel("Quality Metric Targets (ISO/IEC 25023):")
        tgt_info.setStyleSheet("font-size: 13px; font-weight: 500;")

        self.btn_add_target = QPushButton("+ Add Metric Target")
        self.btn_add_target.setObjectName("primaryButton")
        self.btn_add_target.setToolTip("Add or configure quality measure target values for this requirement")
        self.btn_add_target.clicked.connect(lambda: self.on_open_target_dialog(None))

        tgt_top_bar.addWidget(tgt_info)
        tgt_top_bar.addStretch()
        tgt_top_bar.addWidget(self.btn_add_target)
        tgt_layout.addLayout(tgt_top_bar)

        self.targets_empty_lbl = QLabel(
            "No metric targets configured for this requirement.\n"
            "Click '+ Add / Configure Metric Target' above to specify evaluation targets based on ISO/IEC 25023."
        )
        self.targets_empty_lbl.setWordWrap(True)
        self.targets_empty_lbl.setObjectName("mutedHint")
        self.targets_empty_lbl.setStyleSheet("padding: 10px;")
        tgt_layout.addWidget(self.targets_empty_lbl)

        self.targets_table = QTableWidget(0, 5)
        self.targets_table.setHorizontalHeaderLabels([
            "ISO Metric", "Operator", "Target Value", "Data Status", "Actions"
        ])
        self.targets_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.targets_table.setWordWrap(True)
        self.targets_table.verticalHeader().setDefaultSectionSize(44)
        self.targets_table.verticalHeader().setMinimumSectionSize(36)

        tgt_hdr = self.targets_table.horizontalHeader()
        tgt_hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        tgt_hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        tgt_hdr.resizeSection(1, 80)
        tgt_hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        tgt_hdr.resizeSection(2, 120)
        tgt_hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        tgt_hdr.resizeSection(3, 110)
        tgt_hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        tgt_hdr.resizeSection(4, 160)
        self.targets_table.doubleClicked.connect(self.on_target_table_double_clicked)
        tgt_layout.addWidget(self.targets_table)

        self.tabs.addTab(self.targets_tab, "Metric Targets")

        # Tab 3: Confirmed Traceability
        self.trace_tab = QWidget()
        trace_layout = QVBoxLayout(self.trace_tab)
        trace_layout.setContentsMargins(6, 6, 6, 6)

        self.trace_table = QTableWidget(0, 5)
        self.trace_table.setHorizontalHeaderLabels([
            "Characteristic", "Subcharacteristic", "Metric", "Status", "Rationale / Source"
        ])
        self.trace_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.trace_table.setWordWrap(True)
        self.trace_table.verticalHeader().setDefaultSectionSize(48)
        self.trace_table.verticalHeader().setMinimumSectionSize(36)
        self.trace_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        trace_hdr = self.trace_table.horizontalHeader()
        trace_hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        trace_hdr.resizeSection(0, 150)
        trace_hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        trace_hdr.resizeSection(1, 170)
        trace_hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        trace_hdr.resizeSection(2, 260)
        trace_hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        trace_hdr.resizeSection(3, 95)
        trace_hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        trace_hdr.resizeSection(4, 250)
        trace_hdr.setStretchLastSection(False)
        trace_layout.addWidget(self.trace_table)

        self.tabs.addTab(self.trace_tab, "Traceability Matrix")

        main_layout.addWidget(self.tabs)

    def on_edit_req_clicked(self):
        if self.current_req:
            self.edit_requirement_requested.emit(self.current_req)

    def set_requirement(self, req: Optional[Requirement]):
        self.current_req = req
        self.btn_edit_req.setEnabled(req is not None)

        if not req:
            self.req_code_lbl.setText("No requirement selected")
            self.req_title_lbl.setText("Select a requirement in the table to review mappings or edit.")
            self.char_tags_lbl.setText("")
            self.clear_suggestions()
            self.targets_table.setRowCount(0)
            self.targets_empty_lbl.show()
            self.trace_table.setRowCount(0)
            return

        self.req_code_lbl.setText(f"{req.req_code} ({req.type})")
        self.req_badge.setText(req.mapping_status)
        self.req_badge.apply_style(req.mapping_status, "mapping")
        self.req_title_lbl.setText(req.title)

        char_names = [fc.name for fc in req.fr_characteristics]
        if char_names:
            self.char_tags_lbl.setText(f"Mapping Characters: {', '.join(char_names)}")
        else:
            self.char_tags_lbl.setText("Mapping Characters: None assigned yet.")

        self.refresh_analysis()

    def clear_suggestions(self):
        while self.sug_container_layout.count():
            item = self.sug_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def refresh_analysis(self):
        if not self.current_req:
            return

        self.clear_suggestions()

        suggestions = self.mapping_engine.analyze_requirement(self.current_req.id)
        existing_mappings = self.mapping_engine.get_mappings_for_requirement(self.current_req.id)

        # Filter out rejected rule suggestions so they do not clutter the active mapping rules tab
        active_suggestions = [s for s in suggestions if s.get("current_status") not in ("Rejected", "Ditolak")]
        rejected_suggestions = [s for s in suggestions if s.get("current_status") in ("Rejected", "Ditolak")]

        # Manual / custom mappings not linked to an automated mapping rule
        manual_mappings = [m for m in existing_mappings if m.fr_characteristic_id is None and m.mapping_rule_id is None]

        # Group both automated rule suggestions and custom mappings by quality_characteristic_id
        qc_order = []
        qc_suggestions: Dict[int, List[Dict[str, Any]]] = {}
        qc_manuals: Dict[int, List[RequirementMapping]] = {}

        for s in active_suggestions:
            qc_id = s["quality_characteristic_id"]
            if qc_id not in qc_order:
                qc_order.append(qc_id)
            qc_suggestions.setdefault(qc_id, []).append(s)

        for m in manual_mappings:
            qc_id = m.quality_characteristic_id
            if qc_id not in qc_order:
                qc_order.append(qc_id)
            qc_manuals.setdefault(qc_id, []).append(m)

        has_items = False

        measure_to_mapping = {m.quality_measure_id: m for m in existing_mappings if m.quality_measure_id}

        if qc_order:
            has_items = True
            for qc_id in qc_order:
                sug_list = qc_suggestions.get(qc_id, [])
                man_list = qc_manuals.get(qc_id, [])
                card = self.create_unified_qc_card(qc_id, sug_list, man_list, measure_to_mapping)
                self.sug_container_layout.addWidget(card)

        # Show subtle banner if there are rejected rule recommendations
        if rejected_suggestions:
            has_items = True
            rej_box = QFrame()
            rej_box.setObjectName("restoreBox")
            rej_layout = QHBoxLayout(rej_box)
            rej_layout.setContentsMargins(4, 2, 4, 2)

            rej_names = ", ".join(f"{s['quality_characteristic_code']} - {s['quality_characteristic_name']}" for s in rejected_suggestions)
            rej_lbl = QLabel(f"Dismissed rule recommendations: {rej_names}")
            rej_lbl.setObjectName("mutedHint")
            rej_layout.addWidget(rej_lbl)
            rej_layout.addStretch()

            btn_restore = QPushButton("Restore Recommendation")
            btn_restore.setObjectName("restoreButton")
            btn_restore.setToolTip("Restore dismissed rule recommendations for this requirement")
            btn_restore.clicked.connect(lambda checked, r_list=rejected_suggestions: self.on_restore_rejected_suggestions(r_list))
            rej_layout.addWidget(btn_restore)

            self.sug_container_layout.addWidget(rej_box)

        if not has_items:
            no_sug = QLabel(
                "No quality mappings or mapping characters for this requirement.\n\n"
                "• Click 'Edit Requirement' above to assign mapping characters (Tab 2).\n"
                "• Or click '+ Add Custom Mapping' below to directly map to ISO/IEC 25023 characteristics."
            )
            no_sug.setWordWrap(True)
            no_sug.setObjectName("emptyHintLabel")
            self.sug_container_layout.addWidget(no_sug)

        self.sug_container_layout.addStretch()
        self.refresh_targets_table()
        self.refresh_traceability_table()

    def create_unified_qc_card(
        self,
        qc_id: int,
        sug_list: List[Dict[str, Any]],
        man_list: List[RequirementMapping],
        measure_to_mapping: Optional[Dict[int, RequirementMapping]] = None
    ) -> QFrame:
        """
        Renders a single unified card for a Quality Characteristic (e.g. QC-4 - Usability),
        grouping all rule recommendations and manual / custom mappings by subcharacteristic
        under one seamless view without dividing into separate custom mapping blocks.
        """
        if measure_to_mapping is None:
            if self.current_req:
                existing = self.mapping_engine.get_mappings_for_requirement(self.current_req.id)
                measure_to_mapping = {m.quality_measure_id: m for m in existing if m.quality_measure_id}
            else:
                measure_to_mapping = {}

        card = QFrame()
        card.setObjectName("suggestionCard")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)

        # 1. Header: QC Title + Combined Status Badge
        header_row = QHBoxLayout()
        if sug_list:
            qc_title_text = f"{sug_list[0]['quality_characteristic_code']} - {sug_list[0]['quality_characteristic_name']}"
        elif man_list:
            qc_title_text = f"{man_list[0].qc_name or 'ISO Quality Characteristic'}"
        else:
            qc_title_text = "Quality Characteristic"

        qc_title = QLabel(qc_title_text)
        qc_title.setStyleSheet("font-weight: 600; font-size: 14px;")

        # Determine badge: Confirmed if any confirmed, else Suggested / Not Analyzed
        is_confirmed = (
            any(s.get("current_status") in ("Confirmed", "Terkonfirmasi") for s in sug_list) or
            any(m.status in ("Confirmed", "Terkonfirmasi") for m in man_list)
        )
        is_suggested = any(s.get("current_status") in ("Suggested", "Disarankan") for s in sug_list)
        status_text = "Confirmed" if is_confirmed else ("Suggested" if is_suggested else "Not Analyzed")

        badge = StatusBadge(status_text, "mapping")
        header_row.addWidget(qc_title)
        header_row.addStretch()
        header_row.addWidget(badge)
        card_layout.addLayout(header_row)

        # Group all subcharacteristics under this QC
        sub_order = []
        sub_sug: Dict[Any, Dict[str, Any]] = {}
        sub_man: Dict[Any, List[RequirementMapping]] = {}

        for s in sug_list:
            sub_id = s.get("subcharacteristic_id")
            if sub_id not in sub_order:
                sub_order.append(sub_id)
            sub_sug[sub_id] = s

        for m in man_list:
            sub_id = m.quality_subcharacteristic_id
            if sub_id not in sub_order:
                sub_order.append(sub_id)
            sub_man.setdefault(sub_id, []).append(m)

        for idx, sub_id in enumerate(sub_order):
            if idx > 0:
                sep = QFrame()
                sep.setFrameShape(QFrame.Shape.HLine)
                sep.setObjectName("cardSeparator")
                card_layout.addWidget(sep)

            s = sub_sug.get(sub_id)
            m_list = sub_man.get(sub_id, [])

            if s:
                sub_info = QLabel(f"Subcharacteristic: {s['subcharacteristic_name'] or '-'}")
                sub_info.setStyleSheet("font-size: 13px; font-weight: 500;")
                card_layout.addWidget(sub_info)

                rule_info = QLabel(f"Mapping Rule: {s['fr_characteristic_name']}")
                rule_info.setObjectName("ruleLabel")
                card_layout.addWidget(rule_info)

                if s.get("rule_explanation"):
                    expl = QLabel(s["rule_explanation"])
                    expl.setWordWrap(True)
                    expl.setObjectName("explanationLabel")
                    card_layout.addWidget(expl)

                # Quality Measures container
                measures = s.get("available_measures", [])
                if measures or m_list:
                    measures_container = QWidget()
                    measures_container.setStyleSheet("background-color: transparent;")
                    m_box_layout = QVBoxLayout(measures_container)
                    m_box_layout.setContentsMargins(0, 4, 0, 4)
                    m_box_layout.setSpacing(4)

                    rule_qm_ids = {qm['id'] for qm in measures}
                    extra_man = [m for m in m_list if m.quality_measure_id and m.quality_measure_id not in rule_qm_ids]
                    total_count = len(measures) + len(extra_man)

                    m_header = QLabel(f"Related Quality Measures ({total_count}):")
                    m_header.setObjectName("subSectionHeader")
                    m_box_layout.addWidget(m_header)

                    # List rule measures
                    for qm in measures:
                        m_row = QHBoxLayout()
                        m_txt = QLabel(f"• {qm['measure_id']} - {qm['name']} ({qm['unit'] or '-'})")
                        m_txt.setObjectName("measureItemLabel")
                        m_txt.setWordWrap(True)
                        m_txt.setToolTip(qm['name'])
                        m_row.addWidget(m_txt, stretch=1)

                        btn_cfg_target = QPushButton("+ Set Target")
                        btn_cfg_target.setObjectName("targetButton")
                        btn_cfg_target.setToolTip(f"Set target value for metric {qm['measure_id']}")
                        btn_cfg_target.clicked.connect(lambda checked, qm_dict=qm: self.on_open_target_dialog(qm_dict))
                        m_row.addWidget(btn_cfg_target)

                        # If this rule measure is currently mapped in database, provide a Delete button
                        qm_mapping = measure_to_mapping.get(qm["id"])
                        if qm_mapping:
                            btn_del = QPushButton("Delete")
                            btn_del.setObjectName("dangerButton")
                            btn_del.setToolTip(f"Delete mapping for {qm['measure_id']}")
                            btn_del.clicked.connect(lambda checked, mid=qm_mapping.id: self.on_delete_mapping(mid))
                            m_row.addWidget(btn_del)

                        m_box_layout.addLayout(m_row)

                    # List extra manual measures for this same subcharacteristic (if any)
                    for m in extra_man:
                        m_row = QHBoxLayout()
                        unit_str = f" ({m.measure_unit})" if getattr(m, "measure_unit", None) else ""
                        m_txt = QLabel(f"• {m.measure_id_code} - {m.measure_name}{unit_str}")
                        m_txt.setObjectName("measureItemLabel")
                        m_txt.setWordWrap(True)
                        m_txt.setToolTip(m.measure_name)
                        m_row.addWidget(m_txt, stretch=1)

                        btn_cfg_target = QPushButton("+ Set Target")
                        btn_cfg_target.setObjectName("targetButton")
                        btn_cfg_target.setToolTip(f"Set target value for metric {m.measure_id_code}")
                        btn_cfg_target.clicked.connect(lambda checked, qmid=m.quality_measure_id: self.on_open_target_dialog({"id": qmid}))
                        m_row.addWidget(btn_cfg_target)

                        btn_del = QPushButton("Delete")
                        btn_del.setObjectName("dangerButton")
                        btn_del.setToolTip("Delete this custom metric mapping")
                        btn_del.clicked.connect(lambda checked, mid=m.id: self.on_delete_mapping(mid))
                        m_row.addWidget(btn_del)

                        m_box_layout.addLayout(m_row)

                    card_layout.addWidget(measures_container)

                # Rule Action Buttons:
                rule_status = s.get("current_status")
                mapping_id = s.get("existing_mapping_id")
                action_row = QHBoxLayout()
                action_row.addStretch()

                if rule_status in ("Confirmed", "Terkonfirmasi"):
                    btn_del_rule = QPushButton("Delete Rule Mapping")
                    btn_del_rule.setObjectName("dangerButton")
                    btn_del_rule.setToolTip("Delete this rule recommendation mapping and revert it to unmapped")
                    btn_del_rule.clicked.connect(lambda checked, s_dict=s: self.on_delete_rule_mapping(s_dict))
                    action_row.addWidget(btn_del_rule)
                    card_layout.addLayout(action_row)
                else:
                    btn_create = QPushButton("Apply Rule Recommendation")
                    btn_create.setObjectName("primaryButton")
                    btn_create.setToolTip("Apply this mapping rule recommendation and map its ISO 25023 quality measures")
                    btn_create.clicked.connect(lambda checked, s_dict=s: self.on_create_mapping_from_suggestion(s_dict))
                    action_row.addWidget(btn_create)

                    btn_reject = QPushButton("Reject Rule")
                    btn_reject.setObjectName("dangerButton")
                    btn_reject.setToolTip("Reject and dismiss this rule recommendation")
                    if mapping_id:
                        btn_reject.clicked.connect(lambda checked, mid=mapping_id: self.on_reject_mapping(mid))
                    else:
                        btn_reject.clicked.connect(lambda checked, s_dict=s: self.on_reject_suggestion(s_dict))
                    action_row.addWidget(btn_reject)

                    card_layout.addLayout(action_row)

            else:
                # Custom subcharacteristic: formatted exactly like the recommendation section
                sub_name = m_list[0].qsc_name if m_list else "-"
                sub_info = QLabel(f"Subcharacteristic: {sub_name or '-'}")
                sub_info.setStyleSheet("font-size: 13px; font-weight: 500;")
                card_layout.addWidget(sub_info)

                rule_info = QLabel("Mapping Rule: Custom / Manual Mapping")
                rule_info.setObjectName("ruleLabel")
                card_layout.addWidget(rule_info)

                note_text = m_list[0].rational_note if (m_list and m_list[0].rational_note) else ""
                if note_text and note_text != "Manual mapping by requirements engineer.":
                    expl = QLabel(note_text)
                    expl.setWordWrap(True)
                    expl.setObjectName("explanationLabel")
                    card_layout.addWidget(expl)

                # Quality measures for custom subcharacteristic
                valid_m = [m for m in m_list if m.quality_measure_id]
                if valid_m:
                    measures_container = QWidget()
                    measures_container.setStyleSheet("background-color: transparent;")
                    m_box_layout = QVBoxLayout(measures_container)
                    m_box_layout.setContentsMargins(0, 4, 0, 4)
                    m_box_layout.setSpacing(4)

                    m_header = QLabel(f"Related Quality Measures ({len(valid_m)}):")
                    m_header.setObjectName("subSectionHeader")
                    m_box_layout.addWidget(m_header)

                    for m in valid_m:
                        m_row = QHBoxLayout()
                        unit_str = f" ({m.measure_unit})" if getattr(m, "measure_unit", None) else ""
                        m_txt = QLabel(f"• {m.measure_id_code} - {m.measure_name}{unit_str}")
                        m_txt.setObjectName("measureItemLabel")
                        m_txt.setWordWrap(True)
                        m_row.addWidget(m_txt, stretch=1)

                        btn_cfg_target = QPushButton("+ Set Target")
                        btn_cfg_target.setObjectName("targetButton")
                        btn_cfg_target.setToolTip(f"Set target value for metric {m.measure_id_code}")
                        btn_cfg_target.clicked.connect(lambda checked, qmid=m.quality_measure_id: self.on_open_target_dialog({"id": qmid}))
                        m_row.addWidget(btn_cfg_target)

                        btn_del = QPushButton("Delete")
                        btn_del.setObjectName("dangerButton")
                        btn_del.setToolTip("Delete this custom metric mapping")
                        btn_del.clicked.connect(lambda checked, mid=m.id: self.on_delete_mapping(mid))
                        m_row.addWidget(btn_del)

                        m_box_layout.addLayout(m_row)

                    card_layout.addWidget(measures_container)

        return card

    def create_suggestion_card(self, s: Dict[str, Any]) -> QFrame:
        return self.create_unified_qc_card(s["quality_characteristic_id"], [s], [])

    def create_manual_mapping_card(self, m: RequirementMapping) -> QFrame:
        return self.create_unified_qc_card(m.quality_characteristic_id, [], [m])

    def on_delete_mapping(self, mapping_id: int):
        confirm = QMessageBox.question(
            self,
            "Confirm Delete Mapping",
            "Are you sure you want to delete this quality characteristic mapping?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.mapping_engine.delete_mapping(mapping_id)
            self.refresh_analysis()
            self.mapping_changed.emit()

    def on_delete_rule_mapping(self, s: Dict[str, Any]):
        if not self.current_req:
            return
        confirm = QMessageBox.question(
            self,
            "Confirm Delete Rule Mapping",
            f"Are you sure you want to delete the mapping for rule '{s['fr_characteristic_name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            req_id = self.current_req.id
            fc_id = s["fr_characteristic_id"]
            qc_id = s["quality_characteristic_id"]
            qsc_id = s.get("subcharacteristic_id")
            rule_id = s.get("rule_id")
            measure_ids = [m["id"] for m in s.get("available_measures", [])]
            rational_note = f"Accepted from mapping rule recommendation: {s['fr_characteristic_name']}."

            self.mapping_engine.delete_rule_mapping(
                req_id=req_id,
                fc_id=fc_id,
                qc_id=qc_id
            )
            self.refresh_analysis()
            self.mapping_changed.emit()

            if self.undo_stack:
                def undo_delete():
                    self.mapping_engine.apply_rule_suggestion(
                        req_id=req_id,
                        fc_id=fc_id,
                        qc_id=qc_id,
                        qsc_id=qsc_id,
                        rule_id=rule_id,
                        measure_ids=measure_ids,
                        rational_note=rational_note
                    )
                    self.refresh_analysis()
                    self.mapping_changed.emit()

                def redo_delete():
                    self.mapping_engine.delete_rule_mapping(
                        req_id=req_id,
                        fc_id=fc_id,
                        qc_id=qc_id
                    )
                    self.refresh_analysis()
                    self.mapping_changed.emit()

                self.undo_stack.push(LambdaUndoCommand(undo_delete, redo_delete, f"Delete rule mapping '{s['fr_characteristic_name']}'"))

    def on_create_mapping_from_suggestion(self, s: Dict[str, Any]):
        if not self.current_req:
            return
        req_id = self.current_req.id
        fc_id = s["fr_characteristic_id"]
        qc_id = s["quality_characteristic_id"]
        qsc_id = s.get("subcharacteristic_id")
        rule_id = s.get("rule_id")
        measure_ids = [m["id"] for m in s.get("available_measures", [])]
        rational_note = f"Accepted from mapping rule recommendation: {s['fr_characteristic_name']}."

        self.mapping_engine.apply_rule_suggestion(
            req_id=req_id,
            fc_id=fc_id,
            qc_id=qc_id,
            qsc_id=qsc_id,
            rule_id=rule_id,
            measure_ids=measure_ids,
            rational_note=rational_note
        )
        self.refresh_analysis()
        self.mapping_changed.emit()

        if self.undo_stack:
            def undo_apply():
                self.mapping_engine.delete_rule_mapping(
                    req_id=req_id,
                    fc_id=fc_id,
                    qc_id=qc_id
                )
                self.refresh_analysis()
                self.mapping_changed.emit()

            def redo_apply():
                self.mapping_engine.apply_rule_suggestion(
                    req_id=req_id,
                    fc_id=fc_id,
                    qc_id=qc_id,
                    qsc_id=qsc_id,
                    rule_id=rule_id,
                    measure_ids=measure_ids,
                    rational_note=rational_note
                )
                self.refresh_analysis()
                self.mapping_changed.emit()

            self.undo_stack.push(LambdaUndoCommand(undo_apply, redo_apply, f"Apply rule '{s['fr_characteristic_name']}'"))

    def on_confirm_mapping(self, mapping_id: int):
        self.mapping_engine.confirm_mapping(mapping_id)
        self.refresh_analysis()
        self.mapping_changed.emit()

    def on_reject_mapping(self, mapping_id: int):
        self.mapping_engine.reject_mapping(mapping_id)
        self.refresh_analysis()
        self.mapping_changed.emit()

    def on_reject_suggestion(self, s: Dict[str, Any]):
        if not self.current_req:
            return
        self.mapping_engine.reject_rule_suggestion(
            req_id=self.current_req.id,
            fc_id=s["fr_characteristic_id"],
            qc_id=s["quality_characteristic_id"],
            qsc_id=s.get("subcharacteristic_id"),
            rule_id=s.get("rule_id"),
            reason="Rejected by user."
        )
        self.refresh_analysis()
        self.mapping_changed.emit()

    def on_restore_rejected_suggestions(self, rejected_list: List[Dict[str, Any]]):
        if not self.current_req:
            return
        for s in rejected_list:
            self.mapping_engine.restore_rule_suggestion(
                req_id=self.current_req.id,
                fc_id=s["fr_characteristic_id"],
                qc_id=s["quality_characteristic_id"]
            )
        self.refresh_analysis()
        self.mapping_changed.emit()

    def on_add_manual_mapping(self):
        if not self.current_req:
            return
        dlg = ManualMappingDialog(self.catalog_service, self)
        if dlg.exec():
            sel = dlg.get_selection()
            self.mapping_engine.add_manual_mapping(
                req_id=self.current_req.id,
                qc_id=sel["qc_id"],
                qsc_id=sel["qsc_id"],
                qm_id=sel["qm_id"],
                rational_note=sel["rational_note"]
            )
            self.refresh_analysis()
            self.mapping_changed.emit()

    def on_open_target_dialog(self, qm_dict: Optional[Dict[str, Any]] = None, existing_target: Optional[MeasureTarget] = None):
        if not self.current_req:
            QMessageBox.information(self, "Select Requirement", "Please select a requirement first.")
            return

        measure = None
        if qm_dict and "id" in qm_dict:
            measure = self.catalog_service.get_measure_by_id(qm_dict["id"])

        targets = self.target_service.get_targets_for_requirement(self.current_req.id)
        if measure and not existing_target:
            existing_target = next((t for t in targets if t.quality_measure_id == measure.id), None)

        dlg = MetricTargetDialog(
            measure=measure,
            target=existing_target,
            catalog_service=self.catalog_service,
            parent=self
        )
        if dlg.exec():
            data = dlg.get_target_data()
            qm_id = data.get("quality_measure_id") or (measure.id if measure else None)
            if not qm_id:
                QMessageBox.warning(self, "Validation", "Please select an ISO metric.")
                return
            self.target_service.set_target(
                req_id=self.current_req.id,
                quality_measure_id=qm_id,
                operator=data["operator"],
                target_value=data["target_value"],
                target_unit=data["target_unit"],
                rational_note=data["rational_note"],
                is_dummy=data["is_dummy"]
            )
            self.refresh_targets_table()

    def on_target_table_double_clicked(self, index):
        row = index.row()
        item = self.targets_table.item(row, 0)
        if not item or not self.current_req:
            return
        qm_id = item.data(Qt.ItemDataRole.UserRole)
        targets = self.target_service.get_targets_for_requirement(self.current_req.id)
        target = next((t for t in targets if t.quality_measure_id == qm_id), None)
        self.on_open_target_dialog({"id": qm_id}, target)

    def on_delete_target(self, target_id: int):
        confirm = QMessageBox.question(
            self,
            "Confirm Delete Target",
            "Are you sure you want to delete this metric target?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.target_service.delete_target(target_id)
            self.refresh_targets_table()

    def refresh_targets_table(self):
        self.targets_table.setRowCount(0)
        if not self.current_req:
            self.targets_empty_lbl.setText("Select a requirement to view or configure metric targets.")
            self.targets_empty_lbl.show()
            return

        targets = self.target_service.get_targets_for_requirement(self.current_req.id)
        if not targets:
            self.targets_empty_lbl.setText(
                "No metric targets configured for this requirement.\n"
                "Click '+ Add / Configure Metric Target' above to specify evaluation targets based on ISO/IEC 25023."
            )
            self.targets_empty_lbl.show()
        else:
            self.targets_empty_lbl.hide()

        self.targets_table.setRowCount(len(targets))

        read_only_flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        for row, t in enumerate(targets):
            metric_desc = f"{t.measure_id_code} - {t.measure_name}"
            m_item = QTableWidgetItem(metric_desc)
            m_item.setData(Qt.ItemDataRole.UserRole, t.quality_measure_id)
            m_item.setFlags(read_only_flags)
            m_item.setToolTip(metric_desc)
            self.targets_table.setItem(row, 0, m_item)

            op_item = QTableWidgetItem(t.operator)
            op_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            op_item.setFlags(read_only_flags)
            op_item.setToolTip(f"Operator: {t.operator}")
            self.targets_table.setItem(row, 1, op_item)

            val_str = f"{t.target_value} {t.target_unit or ''}".strip()
            val_item = QTableWidgetItem(val_str)
            val_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            val_item.setFlags(read_only_flags)
            val_item.setToolTip(f"Target Value: {val_str}")
            self.targets_table.setItem(row, 2, val_item)

            badge_widget = create_badge_cell("Simulation", "dummy")
            self.targets_table.setCellWidget(row, 3, badge_widget)

            # Actions: Edit and Delete buttons
            actions_widget = QWidget()
            actions_widget.setStyleSheet("background-color: transparent;")
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(6, 2, 6, 2)
            actions_layout.setSpacing(6)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_edit = QPushButton("Edit")
            btn_edit.setStyleSheet("font-size: 12px; min-width: 55px; height: 26px; padding: 2px 8px;")
            btn_edit.setToolTip("Edit this metric target value")
            btn_edit.clicked.connect(lambda checked, tid=t.quality_measure_id, tgt=t: self.on_open_target_dialog({"id": tid}, tgt))
            actions_layout.addWidget(btn_edit)

            btn_del = QPushButton("Delete")
            btn_del.setObjectName("dangerButton")
            btn_del.setStyleSheet("font-size: 12px; min-width: 60px; height: 26px; padding: 2px 8px;")
            btn_del.setToolTip("Delete this metric target")
            btn_del.clicked.connect(lambda checked, tid=t.id: self.on_delete_target(tid))
            actions_layout.addWidget(btn_del)

            self.targets_table.setCellWidget(row, 4, actions_widget)

        self.targets_table.setColumnWidth(4, 160)
        self.targets_table.setColumnWidth(3, 110)
        self.targets_table.setColumnWidth(2, 120)
        self.targets_table.setColumnWidth(1, 80)

    def refresh_traceability_table(self):
        self.trace_table.setRowCount(0)
        if not self.current_req:
            return

        mappings = self.mapping_engine.get_mappings_for_requirement(self.current_req.id)
        self.trace_table.setRowCount(len(mappings))

        read_only_flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        for row, m in enumerate(mappings):
            item_qc = QTableWidgetItem(m.qc_name or "-")
            item_qc.setFlags(read_only_flags)
            item_qc.setToolTip(m.qc_name or "")
            self.trace_table.setItem(row, 0, item_qc)

            item_qsc = QTableWidgetItem(m.qsc_name or "-")
            item_qsc.setFlags(read_only_flags)
            item_qsc.setToolTip(m.qsc_name or "")
            self.trace_table.setItem(row, 1, item_qsc)

            metric_str = f"{m.measure_id_code}: {m.measure_name}" if m.measure_name else "-"
            item_m = QTableWidgetItem(metric_str)
            item_m.setFlags(read_only_flags)
            item_m.setToolTip(m.measure_name if m.measure_name else metric_str)
            self.trace_table.setItem(row, 2, item_m)

            badge_widget = create_badge_cell(m.status, "mapping")
            self.trace_table.setCellWidget(row, 3, badge_widget)

            rat_str = m.rational_note or m.rule_source or "-"
            item_rat = QTableWidgetItem(rat_str)
            item_rat.setFlags(read_only_flags)
            item_rat.setToolTip(rat_str)
            self.trace_table.setItem(row, 4, item_rat)

        self.adjust_trace_table_columns()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_trace_table_columns()

    def adjust_trace_table_columns(self):
        w = self.trace_table.viewport().width()
        base = [150, 170, 260, 95, 250]
        total_base = sum(base)
        if w > total_base:
            extra = w - total_base
            w0 = base[0] + int(extra * 0.10)
            w1 = base[1] + int(extra * 0.15)
            w2 = base[2] + int(extra * 0.40)
            w3 = base[3]
            w4 = w - (w0 + w1 + w2 + w3)
            self.trace_table.setColumnWidth(0, w0)
            self.trace_table.setColumnWidth(1, w1)
            self.trace_table.setColumnWidth(2, w2)
            self.trace_table.setColumnWidth(3, w3)
            self.trace_table.setColumnWidth(4, w4)
        else:
            self.trace_table.setColumnWidth(0, base[0])
            self.trace_table.setColumnWidth(1, base[1])
            self.trace_table.setColumnWidth(2, base[2])
            self.trace_table.setColumnWidth(3, base[3])
            self.trace_table.setColumnWidth(4, base[4])
