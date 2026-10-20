"""
Solid Color Status Badge for PySide6.
Features solid background colors with high-contrast white text,
clean typography, and fixed dimensions to prevent clipping.
Supports English terminology with backward compatibility.
"""
from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout
from PySide6.QtCore import Qt, QSize


class StatusBadge(QLabel):
    def __init__(self, text: str, badge_type: str = "status", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(24)
        fm = self.fontMetrics()
        self.setMinimumWidth(max(40, fm.horizontalAdvance(text) + 20))
        self.apply_style(text, badge_type)

    def setText(self, text: str):
        super().setText(text)
        fm = self.fontMetrics()
        self.setMinimumWidth(max(40, fm.horizontalAdvance(text) + 20))

    def sizeHint(self) -> QSize:
        fm = self.fontMetrics()
        return QSize(max(40, fm.horizontalAdvance(self.text()) + 20), 24)

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    def apply_style(self, text: str, badge_type: str):
        # Base solid tag style: bold text, rounded corners, clean padding
        base = "border-radius: 4px; font-size: 12px; font-weight: 600; padding: 2px 10px; color: #ffffff; "

        if badge_type == "type":
            if text == "FR":
                style = base + "background-color: #2563eb;"  # Solid Blue
            else:
                style = base + "background-color: #475569;"  # Solid Slate

        elif badge_type == "priority":
            if text in ("Critical", "Kritis"):
                style = base + "background-color: #dc2626;"  # Solid Red
            elif text in ("High", "Tinggi"):
                style = base + "background-color: #ea580c;"  # Solid Orange
            elif text in ("Medium", "Sedang"):
                style = base + "background-color: #d97706;"  # Solid Amber
            else:  # Low / Rendah
                style = base + "background-color: #64748b;"  # Solid Gray

        elif badge_type == "mapping":
            if text in ("Confirmed", "Terkonfirmasi"):
                style = base + "background-color: #16a34a;"  # Solid Green
            elif text in ("Suggested", "Disarankan"):
                style = base + "background-color: #2563eb;"  # Solid Blue
            elif text in ("Needs Review", "Perlu Ditinjau"):
                style = base + "background-color: #d97706;"  # Solid Amber
            elif text in ("Rejected", "Ditolak"):
                style = base + "background-color: #e11d48;"  # Solid Rose/Red
            else:  # Not Analyzed / Belum Dianalisis
                style = base + "background-color: #64748b;"  # Solid Slate

        elif badge_type == "dummy":
            style = base + "background-color: #b45309;"  # Solid Amber

        else:  # default requirement status
            if text in ("Approved", "Disetujui"):
                style = base + "background-color: #16a34a;"  # Solid Green
            elif text in ("Under Review", "Sedang Ditinjau"):
                style = base + "background-color: #d97706;"  # Solid Amber
            elif text in ("Implemented", "Diimplementasi"):
                style = base + "background-color: #2563eb;"  # Solid Blue
            else:  # Draft / Draf
                style = base + "background-color: #64748b;"  # Solid Slate

        self.setStyleSheet(style)


class BadgeCell(QWidget):
    """Container widget that centers a StatusBadge inside a table cell and forwards methods."""
    def __init__(self, text: str, badge_type: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.badge = StatusBadge(text, badge_type)
        layout.addWidget(self.badge)

    def text(self) -> str:
        return self.badge.text()

    def setText(self, text: str):
        self.badge.setText(text)

    def apply_style(self, text: str, badge_type: str):
        self.badge.apply_style(text, badge_type)


def create_badge_cell(text: str, badge_type: str) -> BadgeCell:
    """Creates a centered container for a badge widget inside a table cell."""
    return BadgeCell(text, badge_type)
