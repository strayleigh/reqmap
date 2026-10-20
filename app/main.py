"""
ReqMap Desktop Application Entry Point.
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Ensure app package is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.database.db import Database
from app.ui.main_window import MainWindow
from app.core.theme import LIGHT_THEME_QSS, get_light_palette


def main():
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("ReqMap")
    app.setOrganizationName("ISO-RE-Lab")
    app.setPalette(get_light_palette())
    app.setStyleSheet(LIGHT_THEME_QSS)

    # Initialize Database
    db = Database.get_instance()

    # Create and show Main Window
    window = MainWindow(db)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
