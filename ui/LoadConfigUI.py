from PyQt5.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget,
)
import os
from module.config_manager import *

class LoadConfigWindow(QMainWindow):

    def __init__(self, base_path = os.getcwd(), parent=None):
        super().__init__(parent)

        self.setWindowTitle("Load Existing Configuration")
        self.setGeometry(200, 150, 400, 300)
        self.setMinimumSize(400, 300)

        self.config = loadSanitizeSavedConfig(
            os.path.join(base_path, "config"))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        layout.addWidget(QLabel("Select Configuration:"))

        # List of existing configs
        self.config_list = QListWidget()
        self.config_list.addItems(self.config.keys())
        self.config_list.itemDoubleClicked.connect(self.load_selected_config)
        layout.addWidget(self.config_list)

        # Buttons
        btn_layout = QHBoxLayout()
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_selected_config)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)

        btn_layout.addStretch()
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def load_selected_config(self):
        current_item = self.config_list.currentItem()
        try:
            if current_item:
                config_name = current_item.text()

                # Simulasi load config
                digsilent_path = loadConfig(self.config[config_name])[
                    "digsilentpath"]
                project_name = loadConfig(self.config[config_name])[
                    "projectname"]

                # Emit data ke parent window
                if self.parent():
                    self.parent().set_config(digsilent_path, project_name)

                self.close()
        except Exception as e:
            pass
