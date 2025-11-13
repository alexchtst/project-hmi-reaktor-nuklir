from PyQt5.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit,
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
import sys
import os
import pandas as pd
from module.config_manager import *

class NewConfigWindow(QMainWindow):
    """Window untuk membuat konfigurasi baru"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("New Configuration")
        self.setGeometry(200, 150, 500, 200)
        self.setMinimumSize(500, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # DigSILENT Path
        layout.addWidget(QLabel("DigSILENT Path:"))
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText(
            "Select DigSILENT installation path...")
        path_layout.addWidget(self.path_input)

        browse_path_btn = QPushButton("Browse...")
        browse_path_btn.clicked.connect(self.browse_digsilent_path)
        path_layout.addWidget(browse_path_btn)
        layout.addLayout(path_layout)

        # Project Name
        layout.addWidget(QLabel("Project Name:"))
        self.project_input = QLineEdit()
        self.project_input.setPlaceholderText("Enter project name...")
        layout.addWidget(self.project_input)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Config")
        save_btn.clicked.connect(self.save_config)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)

        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def browse_digsilent_path(self):
        from PyQt5.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(self, "Select DigSILENT Path")
        if path:
            self.path_input.setText(path)

    def save_config(self):
        digsilent_path = self.path_input.text()
        project_name = self.project_input.text()

        if not digsilent_path or not project_name:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Please fill all fields!")
            return

        # Emit data ke parent window
        if self.parent():
            self.parent().set_config(digsilent_path, project_name)

        self.close()
