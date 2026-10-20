"""
ISO/IEC 25023:2016 Quality Catalog Reference Viewer.
Clean, academic-grade browser for quality characteristics, subcharacteristics, and measures.
"""
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QTextBrowser, QSplitter, QPushButton, QHeaderView
)
from PySide6.QtCore import Qt
from app.services.catalog_service import QualityCatalogService


class CatalogViewerDialog(QDialog):
    def __init__(self, catalog_service: QualityCatalogService, select_qc_id: Optional[int] = None, parent=None):
        super().__init__(parent)
        self.catalog_service = catalog_service
        self.select_qc_id = select_qc_id

        self.setWindowTitle("ISO/IEC 25023 Software Product Quality Catalog")
        self.resize(880, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["ISO/IEC 25023 Quality Catalog"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.itemClicked.connect(self.on_item_clicked)
        splitter.addWidget(self.tree)

        # Right: Detail Viewer
        self.detail_browser = QTextBrowser()
        self.detail_browser.setOpenExternalLinks(True)
        splitter.addWidget(self.detail_browser)

        splitter.setSizes([320, 560])
        layout.addWidget(splitter)

        # Bottom close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        self.populate_tree()

    def populate_tree(self):
        full_tree = self.catalog_service.get_full_catalog_tree()
        select_item = None

        for qc in full_tree:
            qc_node = QTreeWidgetItem(self.tree, [f"{qc['iso_number']}. {qc['name']}"])
            qc_node.setData(0, Qt.ItemDataRole.UserRole, ("qc", qc))

            if self.select_qc_id and qc["id"] == self.select_qc_id:
                select_item = qc_node

            for sc in qc["subcharacteristics"]:
                sc_node = QTreeWidgetItem(qc_node, [sc["name"]])
                sc_node.setData(0, Qt.ItemDataRole.UserRole, ("sc", sc, qc))

                for m in sc["measures"]:
                    m_node = QTreeWidgetItem(sc_node, [f"[{m['measure_id']}] {m['name']}"])
                    m_node.setData(0, Qt.ItemDataRole.UserRole, ("measure", m, sc, qc))

        self.tree.expandAll()
        if select_item:
            self.tree.setCurrentItem(select_item)
            self.on_item_clicked(select_item, 0)
        elif self.tree.topLevelItemCount() > 0:
            first = self.tree.topLevelItem(0)
            self.tree.setCurrentItem(first)
            self.on_item_clicked(first, 0)

    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        kind = data[0]

        if kind == "qc":
            qc = data[1]
            html = f"""
            <div style='font-family: -apple-system, sans-serif; color: #1f2937;'>
                <h2 style='font-size: 16px; margin-bottom: 4px;'>{qc['iso_number']}. {qc['name']} ({qc['code']})</h2>
                <p style='color: #4b5563; font-size: 12px; margin-top: 0;'>ISO/IEC 25023:2016 Clause 8.{qc['iso_number']}</p>
                <p style='font-size: 13px; line-height: 1.5; color: #374151;'>{qc['description']}</p>
                <hr style='border: none; border-top: 1px solid #e5e7eb; margin: 12px 0;'/>
                <h3 style='font-size: 13px; font-weight: 600; color: #111827;'>Covered Subcharacteristics ({len(qc['subcharacteristics'])}):</h3>
                <ul style='font-size: 12px; line-height: 1.6; color: #374151;'>
            """
            for sc in qc["subcharacteristics"]:
                html += f"<li><b>{sc['code']} - {sc['name']}</b>: {sc['description']}</li>"
            html += "</ul></div>"
            self.detail_browser.setHtml(html)

        elif kind == "sc":
            sc, qc = data[1], data[2]
            html = f"""
            <div style='font-family: -apple-system, sans-serif; color: #1f2937;'>
                <h2 style='font-size: 15px; margin-bottom: 2px;'>{sc['name']} ({sc['code']})</h2>
                <p style='color: #4b5563; font-size: 12px; margin-top: 0;'>Parent Characteristic: {qc['name']} ({qc['code']})</p>
                <p style='font-size: 13px; line-height: 1.5; color: #374151;'>{sc['description']}</p>
                <hr style='border: none; border-top: 1px solid #e5e7eb; margin: 12px 0;'/>
                <h3 style='font-size: 13px; font-weight: 600; color: #111827;'>Related Quality Measures ({len(sc['measures'])}):</h3>
                <ul style='font-size: 12px; line-height: 1.6; color: #374151;'>
            """
            for m in sc["measures"]:
                html += f"""
                <li style='margin-bottom: 8px;'>
                    <b>{m['measure_id']} - {m['name']}</b><br/>
                    Formula: <code style='background-color: #f3f4f6; padding: 2px 4px; border-radius: 3px;'>{m['formula']}</code><br/>
                    Unit: {m['unit']} | Direction: {m['direction']}
                </li>
                """
            html += "</ul></div>"
            self.detail_browser.setHtml(html)

        elif kind == "measure":
            m, sc, qc = data[1], data[2], data[3]
            html = f"""
            <div style='font-family: -apple-system, sans-serif; color: #1f2937;'>
                <h2 style='font-size: 15px; margin-bottom: 4px;'>{m['name']}</h2>
                <table cellpadding='4' cellspacing='0' style='width: 100%; font-size: 12px; border-collapse: collapse;'>
                    <tr><td style='width: 140px; color: #6b7280;'>Measure ID:</td><td><b>{m['measure_id']}</b></td></tr>
                    <tr><td style='color: #6b7280;'>Parent Characteristic:</td><td>{qc['name']}</td></tr>
                    <tr><td style='color: #6b7280;'>Subcharacteristic:</td><td>{sc['name']} ({sc['code']})</td></tr>
                    <tr><td style='color: #6b7280;'>Reference Standard:</td><td>{m['reference_source']}</td></tr>
                    <tr><td style='color: #6b7280;'>Unit:</td><td>{m['unit']}</td></tr>
                    <tr><td style='color: #6b7280;'>Quality Direction:</td><td>{m['direction']}</td></tr>
                    <tr><td style='color: #6b7280;'>Verification Method:</td><td>{m['verification_method']}</td></tr>
                </table>
                <hr style='border: none; border-top: 1px solid #e5e7eb; margin: 10px 0;'/>
                <h3 style='font-size: 13px; font-weight: 600; margin-bottom: 4px;'>Measurement Formula / Function:</h3>
                <div style='background-color: #f9fafb; border: 1px solid #e5e7eb; padding: 8px; border-radius: 3px; font-family: monospace; font-size: 12px;'>
                    {m['formula']}
                </div>
                <h3 style='font-size: 13px; font-weight: 600; margin-top: 12px; margin-bottom: 4px;'>Description:</h3>
                <p style='font-size: 12px; line-height: 1.5; color: #374151;'>{m['description']}</p>
            </div>
            """
            self.detail_browser.setHtml(html)
