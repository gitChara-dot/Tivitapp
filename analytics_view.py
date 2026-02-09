from db import DatabaseManager
from PyQt6.QtWidgets import (QWidget, QGridLayout)
class AnalyticsView(QWidget):
    def __init__(self, database : DatabaseManager):
        super().__init__()

        self._main_layout : QGridLayout = QGridLayout
        self.setLayout(self._main_layout)

        self._database : DatabaseManager = database

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        pass
    def _apply_styles(self):
        pass





