"""
Metric Target Configuration Dialog
Allows users to configure, edit, and add quality measure target values.
Supports selecting metrics from the ISO/IEC 25023 catalog or editing an existing target.
Clearly distinguishes user-defined simulation targets from official ISO metric definitions.
"""
from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFormLayout, QGroupBox, QTextEdit,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from app.models.target import MeasureTarget
from app.models.catalog import QualityMeasure, QualityCharacteristic, QualitySubcharacteristic
from app.services.catalog_service import QualityCatalogService


class MetricTargetDialog(QDialog):
    def __init__(
        self,
        measure: Optional[QualityMeasure] = None,
        target: Optional[MeasureTarget] = None,
        catalog_service: Optional[QualityCatalogService] = None,
        parent=None
    ):
        super().__init__(parent)
        self.measure = measure
        self.target = target
        self.catalog_service = catalog_service
        self.characteristics: List[QualityCharacteristic] = []
        self.subcharacteristics: List[QualitySubcharacteristic] = []
        self.measures: List[QualityMeasure] = []

        title = f"Configure Metric Target - {measure.measure_id}" if measure else "Add ISO/IEC 25023 Metric Target"
        self.setWindowTitle(title)
        self.resize(580, 560)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # Notice box styled via theme
        notice = QFrame()
        notice.setObjectName("noticeBox")
        notice_layout = QVBoxLayout(notice)
        notice_layout.setContentsMargins(10, 8, 10, 8)

        notice_title = QLabel("Simulation & Evaluation Data Notice")
        notice_title.setStyleSheet("font-weight: 600; font-size: 13px;")
        notice_layout.addWidget(notice_title)

        notice_desc = QLabel(
            "The target values below represent user simulation baselines for requirement evaluation, "
            "maintained separately from official ISO/IEC 25023 standard specifications."
        )
        notice_desc.setWordWrap(True)
        notice_desc.setStyleSheet("font-size: 12px;")
        notice_layout.addWidget(notice_desc)
        main_layout.addWidget(notice)

        # Metric Selector (when no measure is pre-assigned)
        if self.measure is None and self.catalog_service:
            select_box = QGroupBox("Select ISO/IEC 25023 Metric")
            select_layout = QFormLayout(select_box)
            select_layout.setSpacing(8)

            self.qc_combo = QComboBox()
            self.qsc_combo = QComboBox()
            self.qm_combo = QComboBox()

            self.characteristics = self.catalog_service.get_all_characteristics()
            for qc in self.characteristics:
                self.qc_combo.addItem(f"{qc.code} - {qc.name}", qc.id)

            self.qc_combo.currentIndexChanged.connect(self.on_qc_changed)
            self.qsc_combo.currentIndexChanged.connect(self.on_qsc_changed)
            self.qm_combo.currentIndexChanged.connect(self.on_qm_changed)

            select_layout.addRow("Characteristic:", self.qc_combo)
            select_layout.addRow("Subcharacteristic:", self.qsc_combo)
            select_layout.addRow("Quality Metric:", self.qm_combo)
            main_layout.addWidget(select_box)

        # Measure Specification Box
        self.spec_box = QGroupBox("ISO/IEC 25023 Metric Specification")
        spec_layout = QFormLayout(self.spec_box)
        spec_layout.setSpacing(8)

        self.m_code_lbl = QLabel(f"{self.measure.measure_id} - {self.measure.name}" if self.measure else "-")
        self.m_code_lbl.setStyleSheet("font-weight: 600; font-size: 13px;")
        self.m_code_lbl.setWordWrap(True)

        self.m_formula_lbl = QLabel((self.measure.formula or "-") if self.measure else "-")
        self.m_formula_lbl.setWordWrap(True)
        self.m_formula_lbl.setStyleSheet("font-size: 12px;")

        self.m_unit_lbl = QLabel((self.measure.unit or "-") if self.measure else "-")
        self.m_unit_lbl.setStyleSheet("font-size: 12px;")

        self.m_dir_lbl = QLabel((self.measure.direction or "-") if self.measure else "-")
        self.m_dir_lbl.setStyleSheet("font-size: 12px;")

        spec_layout.addRow("Selected Metric:", self.m_code_lbl)
        spec_layout.addRow("Calculation Formula:", self.m_formula_lbl)
        spec_layout.addRow("ISO Unit:", self.m_unit_lbl)
        spec_layout.addRow("Quality Direction:", self.m_dir_lbl)

        main_layout.addWidget(self.spec_box)

        # Target Configuration Form
        config_box = QGroupBox("User Target Configuration")
        form_layout = QFormLayout(config_box)
        form_layout.setSpacing(8)

        self.operator_combo = QComboBox()
        self.operator_combo.addItems([
            "<=",
            ">=",
            "=",
            "<",
            ">",
            "range"
        ])
        if self.target and self.target.operator:
            self.operator_combo.setCurrentText(self.target.operator)
        else:
            self.operator_combo.setCurrentText("<=")

        default_val = self.target.target_value if self.target else "300"
        self.value_edit = QLineEdit(default_val)
        self.value_edit.setPlaceholderText("e.g., 300, 99.5, 5")

        default_unit = self.target.target_unit if self.target else (self.measure.unit if self.measure else "ms")
        self.unit_edit = QLineEdit(default_unit or "")
        self.unit_edit.setPlaceholderText("e.g., ms, %, sec")

        default_notes = self.target.rational_note if self.target else "Requirement evaluation target."
        self.notes_edit = QTextEdit(default_notes)
        self.notes_edit.setMaximumHeight(65)

        form_layout.addRow("Comparison Operator *:", self.operator_combo)
        form_layout.addRow("Target Value *:", self.value_edit)
        form_layout.addRow("Value Unit:", self.unit_edit)
        form_layout.addRow("Justification / Notes:", self.notes_edit)

        main_layout.addWidget(config_box)

        # Action Buttons
        btn_layout = QHBoxLayout()

        self.btn_reset = QPushButton("Reset to Default")
        self.btn_reset.clicked.connect(self.on_reset_default)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Save Target")
        self.btn_save.setObjectName("primaryButton")
        self.btn_save.clicked.connect(self.on_save)

        btn_layout.addWidget(self.btn_reset)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        main_layout.addLayout(btn_layout)

        # Trigger cascade initialization if selecting metric
        if self.measure is None and self.catalog_service and self.characteristics:
            self.on_qc_changed(0)

    def on_qc_changed(self, index: int):
        self.qsc_combo.clear()
        if index < 0 or index >= len(self.characteristics):
            return
        qc = self.characteristics[index]
        self.subcharacteristics = self.catalog_service.get_subcharacteristics(qc.id)
        for sc in self.subcharacteristics:
            self.qsc_combo.addItem(f"{sc.code} - {sc.name}", sc.id)
        if self.subcharacteristics:
            self.on_qsc_changed(0)

    def on_qsc_changed(self, index: int):
        self.qm_combo.clear()
        if index < 0 or index >= len(self.subcharacteristics):
            return
        qsc = self.subcharacteristics[index]
        self.measures = self.catalog_service.get_measures_for_subcharacteristic(qsc.id)
        for m in self.measures:
            self.qm_combo.addItem(f"{m.measure_id} - {m.name}", m.id)
        if self.measures:
            self.on_qm_changed(0)

    def on_qm_changed(self, index: int):
        if index < 0 or index >= len(self.measures):
            self.measure = None
            self.m_code_lbl.setText("-")
            self.m_formula_lbl.setText("-")
            self.m_unit_lbl.setText("-")
            self.m_dir_lbl.setText("-")
            return

        m = self.measures[index]
        self.measure = m
        self.m_code_lbl.setText(f"{m.measure_id} - {m.name}")
        self.m_formula_lbl.setText(m.formula or "-")
        self.m_unit_lbl.setText(m.unit or "-")
        self.m_dir_lbl.setText(m.direction or "-")
        if not self.target and m.unit:
            self.unit_edit.setText(m.unit)

    def on_reset_default(self):
        self.operator_combo.setCurrentText("<=")
        self.value_edit.setText("300")
        if self.measure and self.measure.unit:
            self.unit_edit.setText(self.measure.unit)
        else:
            self.unit_edit.setText("ms")
        self.notes_edit.setText("Default simulation target baseline.")

    def on_save(self):
        if not self.measure:
            QMessageBox.warning(self, "Validation", "Please select an ISO/IEC 25023 metric first.")
            return

        val = self.value_edit.text().strip()
        if not val:
            QMessageBox.warning(self, "Validation", "Target value cannot be empty.")
            self.value_edit.setFocus()
            return
        self.accept()

    def get_target_data(self) -> Dict[str, Any]:
        return {
            "quality_measure_id": self.measure.id if self.measure else None,
            "operator": self.operator_combo.currentText(),
            "target_value": self.value_edit.text().strip(),
            "target_unit": self.unit_edit.text().strip(),
            "rational_note": self.notes_edit.toPlainText().strip(),
            "is_dummy": 1
        }
