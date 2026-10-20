"""
FR Characteristic Multi-Selector Widget
Provides clean, minimal selection of Table III FR characteristics.
Fully adheres to unified theme colors and readable font sizes.
"""
from typing import List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QCheckBox, QScrollArea, QFrame, QLabel
)
from app.models.requirement import FRCharacteristic


class FRCharacteristicSelector(QWidget):
    def __init__(self, characteristics: List[FRCharacteristic], parent=None):
        super().__init__(parent)
        self.characteristics = characteristics
        self.checkboxes = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(6)
        container_layout.setContentsMargins(2, 2, 2, 2)

        for fc in self.characteristics:
            item_box = QFrame()
            item_box.setObjectName("charItemBox")
            item_layout = QVBoxLayout(item_box)
            item_layout.setContentsMargins(8, 6, 8, 6)
            item_layout.setSpacing(3)

            cb = QCheckBox(f"{fc.code}: {fc.name}")
            cb.setStyleSheet("font-weight: 600; font-size: 13px;")
            item_layout.addWidget(cb)

            if fc.description:
                desc = QLabel(fc.description)
                desc.setWordWrap(True)
                desc.setStyleSheet("font-size: 12px; padding-left: 24px;")
                item_layout.addWidget(desc)

            self.checkboxes[fc.id] = cb
            container_layout.addWidget(item_box)

        container_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def get_selected_ids(self) -> List[int]:
        return [char_id for char_id, cb in self.checkboxes.items() if cb.isChecked()]

    def set_selected_ids(self, selected_ids: List[int]):
        selected_set = set(selected_ids)
        for char_id, cb in self.checkboxes.items():
            cb.setChecked(char_id in selected_set)
