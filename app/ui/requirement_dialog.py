"""
Requirement Create/Edit Dialog.
Allows creating and updating requirements with assigned mapping rule characteristics.
"""
from typing import Optional, List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QPushButton, QFormLayout, QGroupBox,
    QTabWidget, QWidget, QMessageBox
)
from app.models.requirement import Requirement, FRCharacteristic
from app.ui.widgets.char_selector import FRCharacteristicSelector
from app.core.constants import Priority, RequirementStatus, MappingStatus


class RequirementDialog(QDialog):
    def __init__(
        self,
        available_chars: List[FRCharacteristic],
        req: Optional[Requirement] = None,
        default_type: str = "FR",
        suggested_code: str = "",
        parent=None
    ):
        super().__init__(parent)
        self.req = req
        self.default_type = default_type
        self.suggested_code = suggested_code
        self.available_chars = available_chars
        self.char_selector: Optional[FRCharacteristicSelector] = None

        self.setWindowTitle("Edit Requirement" if req else "Add New Requirement")
        self.resize(680, 700)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)

        # Tab widget: Tab 1 (General Information), Tab 2 (Mapping Rules)
        self.tabs = QTabWidget()

        # Tab 1: General Details
        gen_tab = QWidget()
        form_layout = QFormLayout(gen_tab)
        form_layout.setSpacing(10)

        self.code_edit = QLineEdit(self.req.req_code if self.req else self.suggested_code)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["FR", "NFR"])
        self.type_combo.setCurrentText(self.req.type if self.req else self.default_type)
        self.type_combo.currentTextChanged.connect(self.on_type_changed)

        self.title_edit = QLineEdit(self.req.title if self.req else "")
        self.title_edit.setPlaceholderText("e.g., User Authentication with RBAC")

        self.desc_edit = QTextEdit(self.req.description if self.req else "")
        self.desc_edit.setPlaceholderText("Full description of functional or non-functional requirement...")
        self.desc_edit.setMinimumHeight(100)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems([p.value for p in Priority])
        self.priority_combo.setCurrentText(self.req.priority if self.req else Priority.MEDIUM.value)

        self.status_combo = QComboBox()
        self.status_combo.addItems([s.value for s in RequirementStatus])
        self.status_combo.setCurrentText(self.req.status if self.req else RequirementStatus.DRAFT.value)

        self.mapping_status_combo = QComboBox()
        self.mapping_status_combo.addItems([m.value for m in MappingStatus])
        self.mapping_status_combo.setCurrentText(
            self.req.mapping_status if self.req else MappingStatus.NOT_ANALYZED.value
        )

        form_layout.addRow("Requirement Code *:", self.code_edit)
        form_layout.addRow("Type *:", self.type_combo)
        form_layout.addRow("Requirement Title *:", self.title_edit)
        form_layout.addRow("Description:", self.desc_edit)
        form_layout.addRow("Priority:", self.priority_combo)
        form_layout.addRow("Engineering Status:", self.status_combo)
        form_layout.addRow("Mapping Status:", self.mapping_status_combo)

        self.tabs.addTab(gen_tab, "General Information")

        # Tab 2: Characteristic Selection (Mapping Rules) - Available for both FR and NFR
        self.char_tab = QWidget()
        char_layout = QVBoxLayout(self.char_tab)
        char_info = QLabel(
            "Select applicable characteristics based on mapping rules.\n"
            "Selected characteristics will be matched against ISO/IEC 25023 quality attributes "
            "(applicable to both FR and NFR)."
        )
        char_info.setWordWrap(True)
        char_info.setStyleSheet("color: #64748b; font-size: 12px; margin-bottom: 6px;")
        char_layout.addWidget(char_info)

        self.char_selector = FRCharacteristicSelector(self.available_chars)
        if self.req and self.req.fr_characteristics:
            selected_ids = [fc.id for fc in self.req.fr_characteristics if fc.id]
            self.char_selector.set_selected_ids(selected_ids)

        char_layout.addWidget(self.char_selector)
        self.tabs.addTab(self.char_tab, "Mapping Rules")

        main_layout.addWidget(self.tabs)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Save")
        self.btn_save.setObjectName("primaryButton")
        self.btn_save.clicked.connect(self.on_save)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        main_layout.addLayout(btn_layout)

    def on_type_changed(self, new_type: str):
        pass

    def on_save(self):
        code = self.code_edit.text().strip()
        title = self.title_edit.text().strip()

        if not code:
            QMessageBox.warning(self, "Validation", "Requirement code cannot be empty!")
            self.code_edit.setFocus()
            return

        if not title:
            QMessageBox.warning(self, "Validation", "Requirement title cannot be empty!")
            self.title_edit.setFocus()
            return

        self.accept()

    def get_data(self) -> Requirement:
        req = self.req or Requirement()
        req.req_code = self.code_edit.text().strip()
        req.type = self.type_combo.currentText()
        req.title = self.title_edit.text().strip()
        req.description = self.desc_edit.toPlainText().strip()
        req.priority = self.priority_combo.currentText()
        req.status = self.status_combo.currentText()
        req.mapping_status = self.mapping_status_combo.currentText()
        return req

    def get_selected_char_ids(self) -> List[int]:
        if self.char_selector:
            return self.char_selector.get_selected_ids()
        return []
