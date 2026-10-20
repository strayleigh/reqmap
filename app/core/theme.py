"""
Clean, minimal, academic-grade theme styling for ReqMap.
Typography is enlarged for excellent readability (14px base).
Tags use crisp solid colors as requested.
"""
from PySide6.QtGui import QPalette, QColor


def get_dark_palette() -> QPalette:
    p = QPalette()
    dark_window = QColor("#0f172a")
    panel_base = QColor("#1e293b")
    alternate_base = QColor("#151f30")
    text_color = QColor("#f8fafc")
    muted_text = QColor("#94a3b8")
    accent_blue = QColor("#2563eb")

    p.setColor(QPalette.ColorRole.Window, dark_window)
    p.setColor(QPalette.ColorRole.WindowText, text_color)
    p.setColor(QPalette.ColorRole.Base, panel_base)
    p.setColor(QPalette.ColorRole.AlternateBase, alternate_base)
    p.setColor(QPalette.ColorRole.ToolTipBase, panel_base)
    p.setColor(QPalette.ColorRole.ToolTipText, text_color)
    p.setColor(QPalette.ColorRole.Text, text_color)
    p.setColor(QPalette.ColorRole.Button, panel_base)
    p.setColor(QPalette.ColorRole.ButtonText, text_color)
    p.setColor(QPalette.ColorRole.BrightText, QColor("#ef4444"))
    p.setColor(QPalette.ColorRole.Link, QColor("#38bdf8"))
    p.setColor(QPalette.ColorRole.Highlight, accent_blue)
    p.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    p.setColor(QPalette.ColorRole.PlaceholderText, muted_text)

    # Disabled colors
    p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor("#64748b"))
    p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#64748b"))
    p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor("#64748b"))
    return p


def get_light_palette() -> QPalette:
    p = QPalette()
    light_window = QColor("#f8fafc")
    panel_base = QColor("#ffffff")
    alternate_base = QColor("#f8fafc")
    text_color = QColor("#0f172a")
    muted_text = QColor("#64748b")
    accent_blue = QColor("#2563eb")

    p.setColor(QPalette.ColorRole.Window, light_window)
    p.setColor(QPalette.ColorRole.WindowText, text_color)
    p.setColor(QPalette.ColorRole.Base, panel_base)
    p.setColor(QPalette.ColorRole.AlternateBase, alternate_base)
    p.setColor(QPalette.ColorRole.ToolTipBase, panel_base)
    p.setColor(QPalette.ColorRole.ToolTipText, text_color)
    p.setColor(QPalette.ColorRole.Text, text_color)
    p.setColor(QPalette.ColorRole.Button, panel_base)
    p.setColor(QPalette.ColorRole.ButtonText, text_color)
    p.setColor(QPalette.ColorRole.BrightText, QColor("#dc2626"))
    p.setColor(QPalette.ColorRole.Link, accent_blue)
    p.setColor(QPalette.ColorRole.Highlight, accent_blue)
    p.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    p.setColor(QPalette.ColorRole.PlaceholderText, muted_text)

    # Disabled colors
    p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor("#94a3b8"))
    p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#94a3b8"))
    p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor("#94a3b8"))
    return p


LIGHT_THEME_QSS = """
* {
    font-family: 'Segoe UI', 'Noto Sans', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
    font-size: 14px;
    color: #0f172a;
}

QMainWindow, QDialog, QWidget {
    background-color: #f8fafc;
    color: #0f172a;
}

/* Menu Bar */
QMenuBar {
    background-color: #ffffff;
    color: #334155;
    border-bottom: 1px solid #e2e8f0;
    padding: 4px 6px;
    font-size: 14px;
}
QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 3px;
}
QMenuBar::item:selected {
    background-color: #f1f5f9;
    color: #0f172a;
}
QMenu {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 4px;
}
QMenu::item {
    background-color: transparent;
    padding: 7px 24px 7px 12px;
    border-radius: 3px;
    font-size: 14px;
}
QMenu::item:selected {
    background-color: #f1f5f9;
    color: #1d4ed8;
}
QMenu::separator {
    height: 1px;
    background-color: #e2e8f0;
    margin: 4px 0;
}

/* ToolBar */
QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    spacing: 4px;
    padding: 3px 8px;
}
QToolButton {
    background-color: transparent;
    color: #334155;
    border: none;
    border-radius: 4px;
    padding: 4px 6px;
    margin: 1px 2px;
}
QToolButton:hover {
    background-color: #f1f5f9;
    color: #0f172a;
}
QToolButton:pressed {
    background-color: #e2e8f0;
}
QToolButton:checked {
    background-color: #f1f5f9;
    border: none;
}
QToolBar::separator {
    width: 1px;
    background-color: #e2e8f0;
    margin: 4px 6px;
}

/* Status Bar */
QStatusBar {
    background-color: #ffffff;
    color: #475569;
    border-top: 1px solid #e2e8f0;
    font-size: 13px;
    padding: 5px 12px;
}
QStatusBar QLabel {
    background-color: transparent;
    color: #475569;
    font-size: 13px;
}

/* Splitter */
QSplitter {
    background-color: #f8fafc;
}
QSplitter::handle {
    background-color: #e2e8f0;
}
QSplitter::handle:horizontal {
    width: 2px;
}
QSplitter::handle:vertical {
    height: 2px;
}

/* Content Panels, Trees & Tables */
QTreeView, QTableView, QTableWidget, QTreeWidget, QListWidget, QTextBrowser {
    background-color: #ffffff;
    alternate-background-color: #f8fafc;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    gridline-color: #f1f5f9;
    selection-background-color: #f1f5f9;
    selection-color: #1d4ed8;
    outline: none;
    font-size: 14px;
}
QTreeView::item, QTableWidget::item, QTableView::item {
    background-color: transparent;
    padding: 6px 8px;
    border-bottom: 1px solid #f8fafc;
}
QTreeView::item:hover, QTableWidget::item:hover, QTableView::item:hover {
    background-color: #f8fafc;
}
QTreeView::item:selected, QTableWidget::item:selected, QTableView::item:selected {
    background-color: #f1f5f9;
    color: #1d4ed8;
    font-weight: 500;
}
QHeaderView::section {
    background-color: #f8fafc;
    color: #475569;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid #cbd5e1;
    border-right: 1px solid #f1f5f9;
    font-size: 13px;
    font-weight: 600;
}

/* Input Fields */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 3px;
    padding: 7px 10px;
    font-size: 14px;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
    border: 1px solid #3b82f6;
    background-color: #ffffff;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}

/* Buttons */
QPushButton {
    background-color: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
    border-radius: 3px;
    padding: 7px 16px;
    font-size: 14px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #f8fafc;
    border-color: #94a3b8;
    color: #0f172a;
}
QPushButton:pressed {
    background-color: #f1f5f9;
}
QPushButton#primaryButton {
    background-color: #ffffff;
    border: 1px solid #3b82f6;
    color: #1d4ed8;
    font-weight: 600;
}
QPushButton#primaryButton:hover {
    background-color: #f1f5f9;
    border-color: #1d4ed8;
}
QPushButton#successButton {
    background-color: #ffffff;
    border: 1px solid #10b981;
    color: #047857;
    font-weight: 600;
}
QPushButton#successButton:hover {
    background-color: #f1f5f9;
    border-color: #059669;
}
QPushButton#dangerButton {
    background-color: #ffffff;
    border: 1px solid #f87171;
    color: #b91c1c;
    font-size: 12px;
    padding: 3px 10px;
    border-radius: 3px;
    font-weight: 500;
    min-height: 24px;
    min-width: 50px;
}
QPushButton#dangerButton:hover {
    background-color: #fef2f2;
    border-color: #dc2626;
    color: #991b1b;
}
QPushButton#targetButton {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    color: #334155;
    font-size: 12px;
    padding: 3px 8px;
    border-radius: 3px;
    font-weight: 500;
    min-height: 24px;
    min-width: 75px;
}
QPushButton#targetButton:hover {
    background-color: #f1f5f9;
    border-color: #94a3b8;
    color: #0f172a;
}

/* Card & Box Containers */
QFrame#headerFrame, QFrame#suggestionCard, QFrame#charItemBox, QFrame#noticeBox {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 10px;
}
QFrame#headerFrame QWidget, QFrame#suggestionCard QWidget, QFrame#charItemBox QWidget, QFrame#noticeBox QWidget, QFrame#restoreBox QWidget {
    background-color: transparent;
}
QFrame#restoreBox {
    background-color: #f8fafc;
    border: 1px dashed #cbd5e1;
    border-radius: 6px;
    padding: 6px 10px;
}
QFrame#cardSeparator {
    color: #e2e8f0;
    margin: 4px 0;
}

/* Semantic Labels */
QLabel#ruleLabel {
    color: #334155;
    font-size: 13px;
    font-weight: 500;
}
QLabel#explanationLabel {
    color: #475569;
    font-size: 12px;
}
QLabel#subSectionHeader {
    font-weight: 600;
    font-size: 12px;
    color: #1e293b;
}
QLabel#measureItemLabel {
    font-size: 12px;
    color: #0f172a;
}
QLabel#tableStatusLabel {
    color: #64748b;
    font-size: 13px;
}
QLabel#tableHintLabel {
    color: #64748b;
    font-size: 12px;
    font-style: italic;
}
QLabel#mutedHint {
    color: #64748b;
    font-size: 12px;
}
QLabel#emptyHintLabel {
    color: #64748b;
    font-size: 13px;
    padding: 12px;
}
QLabel#explorerHeaderTitle {
    font-weight: 600;
    font-size: 13px;
    color: #111827;
}

/* Panel Buttons */
QPushButton#panelCloseBtn {
    background: transparent;
    border: none;
    font-size: 11px;
    color: #64748b;
    padding: 2px 5px;
    border-radius: 3px;
    font-weight: bold;
}
QPushButton#panelCloseBtn:hover {
    background-color: #e2e8f0;
    color: #0f172a;
}
QPushButton#restoreButton {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 3px;
    font-size: 11px;
    padding: 3px 10px;
    color: #2563eb;
    font-weight: 500;
}
QPushButton#restoreButton:hover {
    background-color: #eff6ff;
    border-color: #93c5fd;
    color: #1d4ed8;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    background-color: #ffffff;
    border-radius: 4px;
}
QTabBar::tab {
    background-color: #f8fafc;
    color: #475569;
    padding: 7px 14px;
    border: 1px solid #e2e8f0;
    border-bottom: none;
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
    margin-right: 2px;
    font-size: 13px;
    font-weight: 500;
}
QTabBar::tab:selected {
    background-color: #ffffff;
    color: #1d4ed8;
    font-weight: 600;
    border-bottom: 2px solid #3b82f6;
}

/* GroupBox */
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    margin-top: 14px;
    font-weight: 600;
    color: #1e293b;
    padding-top: 14px;
    font-size: 14px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    padding: 0 4px;
    background-color: #ffffff;
}

/* ScrollBars */
QScrollBar:vertical {
    background-color: #f8fafc;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    min-height: 24px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

DARK_THEME_QSS = """
* {
    font-family: 'Segoe UI', 'Noto Sans', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
    font-size: 14px;
    color: #f1f5f9;
}

QMainWindow, QDialog, QWidget {
    background-color: #0f172a;
    color: #f8fafc;
}

/* Menu Bar */
QMenuBar {
    background-color: #1e293b;
    color: #cbd5e1;
    border-bottom: 1px solid #334155;
    padding: 4px 6px;
    font-size: 14px;
}
QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 3px;
}
QMenuBar::item:selected {
    background-color: #334155;
    color: #ffffff;
}
QMenu {
    background-color: #1e293b;
    color: #f1f5f9;
    border: 1px solid #334155;
    border-radius: 4px;
    padding: 4px;
}
QMenu::item {
    background-color: transparent;
    padding: 7px 24px 7px 12px;
    border-radius: 3px;
    font-size: 14px;
}
QMenu::item:selected {
    background-color: #334155;
    color: #60a5fa;
}
QMenu::separator {
    height: 1px;
    background-color: #334155;
    margin: 4px 0;
}

/* ToolBar */
QToolBar {
    background-color: #1e293b;
    border-bottom: 1px solid #334155;
    spacing: 4px;
    padding: 3px 8px;
}
QToolButton {
    background-color: transparent;
    color: #e2e8f0;
    border: none;
    border-radius: 4px;
    padding: 4px 6px;
    margin: 1px 2px;
}
QToolButton:hover {
    background-color: #334155;
    color: #ffffff;
}
QToolButton:pressed {
    background-color: #0f172a;
}
QToolButton:checked {
    background-color: #243247;
    border: none;
}
QToolBar::separator {
    width: 1px;
    background-color: #334155;
    margin: 4px 6px;
}

/* Status Bar */
QStatusBar {
    background-color: #0f172a;
    color: #94a3b8;
    border-top: 1px solid #334155;
    font-size: 13px;
    padding: 5px 12px;
}
QStatusBar QLabel {
    background-color: transparent;
    color: #94a3b8;
    font-size: 13px;
}

/* Splitter */
QSplitter {
    background-color: #0f172a;
}
QSplitter::handle {
    background-color: #334155;
}
QSplitter::handle:horizontal {
    width: 2px;
}
QSplitter::handle:vertical {
    height: 2px;
}

/* Tables & Trees */
QTreeView, QTableView, QTableWidget, QTreeWidget, QListWidget, QTextBrowser {
    background-color: #1e293b;
    alternate-background-color: #151f30;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 4px;
    gridline-color: #0f172a;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    outline: none;
    font-size: 14px;
}
QTreeView::item, QTableWidget::item, QTableView::item {
    background-color: transparent;
    padding: 6px 8px;
    border-bottom: 1px solid #1e293b;
}
QTreeView::item:hover, QTableWidget::item:hover, QTableView::item:hover {
    background-color: #26354a;
}
QTreeView::item:selected, QTableWidget::item:selected, QTableView::item:selected {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: 500;
}
QHeaderView::section {
    background-color: #0f172a;
    color: #94a3b8;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid #334155;
    border-right: 1px solid #1e293b;
    font-size: 13px;
    font-weight: 600;
}

/* Input Fields */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 3px;
    padding: 7px 10px;
    font-size: 14px;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
    border: 1px solid #3b82f6;
    background-color: #1e293b;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #1e293b;
    color: #f8fafc;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    border: 1px solid #334155;
}

/* Buttons */
QPushButton {
    background-color: #1e293b;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 3px;
    padding: 6px 14px;
    font-size: 14px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #334155;
    color: #ffffff;
}
QPushButton#primaryButton {
    background-color: #2563eb;
    border: 1px solid #1d4ed8;
    color: #ffffff;
    font-weight: 600;
}
QPushButton#primaryButton:hover {
    background-color: #1d4ed8;
    border-color: #3b82f6;
    color: #ffffff;
}
QPushButton#successButton {
    background-color: #16a34a;
    border: 1px solid #15803d;
    color: #ffffff;
    font-weight: 600;
}
QPushButton#successButton:hover {
    background-color: #15803d;
}
QPushButton#dangerButton {
    background-color: #1e293b;
    border: 1px solid #ef4444;
    color: #fca5a5;
    font-size: 12px;
    padding: 3px 10px;
    border-radius: 3px;
    font-weight: 500;
    min-height: 24px;
    min-width: 50px;
}
QPushButton#dangerButton:hover {
    background-color: #7f1d1d;
    border-color: #f87171;
    color: #ffffff;
}
QPushButton#targetButton {
    background-color: #1e293b;
    border: 1px solid #334155;
    color: #e2e8f0;
    font-size: 12px;
    padding: 3px 8px;
    border-radius: 3px;
    font-weight: 500;
    min-height: 24px;
    min-width: 75px;
}
QPushButton#targetButton:hover {
    background-color: #334155;
    color: #ffffff;
}

/* Card & Box Containers */
QFrame#headerFrame, QFrame#suggestionCard, QFrame#charItemBox, QFrame#noticeBox {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 4px;
    padding: 10px;
}
QFrame#headerFrame QWidget, QFrame#suggestionCard QWidget, QFrame#charItemBox QWidget, QFrame#noticeBox QWidget, QFrame#restoreBox QWidget {
    background-color: transparent;
}
QFrame#restoreBox {
    background-color: #151f30;
    border: 1px dashed #475569;
    border-radius: 6px;
    padding: 6px 10px;
}
QFrame#cardSeparator {
    color: #334155;
    margin: 4px 0;
}

/* Semantic Labels */
QLabel#ruleLabel {
    color: #93c5fd;
    font-size: 13px;
    font-weight: 500;
}
QLabel#explanationLabel {
    color: #94a3b8;
    font-size: 12px;
}
QLabel#subSectionHeader {
    font-weight: 600;
    font-size: 12px;
    color: #f1f5f9;
}
QLabel#measureItemLabel {
    font-size: 12px;
    color: #e2e8f0;
}
QLabel#tableStatusLabel {
    color: #94a3b8;
    font-size: 13px;
}
QLabel#tableHintLabel {
    color: #94a3b8;
    font-size: 12px;
    font-style: italic;
}
QLabel#mutedHint {
    color: #94a3b8;
    font-size: 12px;
}
QLabel#emptyHintLabel {
    color: #94a3b8;
    font-size: 13px;
    padding: 12px;
}
QLabel#explorerHeaderTitle {
    font-weight: 600;
    font-size: 13px;
    color: #f8fafc;
}

/* Panel Buttons */
QPushButton#panelCloseBtn {
    background: transparent;
    border: none;
    font-size: 11px;
    color: #94a3b8;
    padding: 2px 5px;
    border-radius: 3px;
    font-weight: bold;
}
QPushButton#panelCloseBtn:hover {
    background-color: #334155;
    color: #f8fafc;
}
QPushButton#restoreButton {
    background-color: #1e293b;
    border: 1px solid #3b82f6;
    border-radius: 3px;
    font-size: 11px;
    padding: 3px 10px;
    color: #60a5fa;
    font-weight: 500;
}
QPushButton#restoreButton:hover {
    background-color: #1e3a5f;
    border-color: #60a5fa;
    color: #93c5fd;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #334155;
    background-color: #1e293b;
    border-radius: 4px;
}
QTabBar::tab {
    background-color: #0f172a;
    color: #94a3b8;
    padding: 7px 14px;
    border: 1px solid #334155;
    border-bottom: none;
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
    margin-right: 2px;
    font-size: 13px;
    font-weight: 500;
}
QTabBar::tab:selected {
    background-color: #1e293b;
    color: #60a5fa;
    font-weight: 600;
    border-bottom: 2px solid #3b82f6;
}

/* GroupBox */
QGroupBox {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 4px;
    margin-top: 14px;
    font-weight: 600;
    color: #e2e8f0;
    padding-top: 14px;
    font-size: 14px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    padding: 0 4px;
    background-color: #1e293b;
}

/* ScrollBars */
QScrollBar:vertical {
    background-color: #0f172a;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #334155;
    min-height: 24px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background-color: #475569;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
