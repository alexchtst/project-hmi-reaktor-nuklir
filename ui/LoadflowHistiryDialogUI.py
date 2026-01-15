from PyQt5.QtWidgets import (
    QDialog, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, Qt
import os
import json
from datetime import datetime
from asset.assetloader import LOGO
from utils import resource_path

class LoadflowHistoryDialogUI(QDialog):
    datareading = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Load Flow History")
        self.setWindowIcon(QIcon(fr"{LOGO}"))
        self.setFixedWidth(800)
        self.setFixedHeight(500)
        
        self.setWindowModality(Qt.ApplicationModal)
        
        self.data_folder = resource_path("data")
        
        self.setup_ui()
        
        self.load_history_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Label header
        header_label = QLabel("Load Flow History")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header_label)
        
        # Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["File Path", "Date Created", "Action"])
        
        # Set table properties
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 100)
        
        # Style table
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #ddd;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.table)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_history_data(self):
        """
        Load semua file JSON dari folder data
        """
        try:
            if not os.path.exists(self.data_folder):
                QMessageBox.warning(self, "Warning", "Data folder tidak ditemukan!")
                return
            
            # Get all .json files
            files = [f for f in os.listdir(self.data_folder) if f.endswith('.json')]
            
            if not files:
                QMessageBox.information(self, "Info", "Tidak ada file history yang ditemukan.")
                return
            
            files_with_time = []
            for f in files:
                file_path = os.path.join(self.data_folder, f)
                mtime = os.path.getmtime(file_path)
                files_with_time.append((f, file_path, mtime))
            
            files_with_time.sort(key=lambda x: x[2], reverse=True)
            
            self.table.setRowCount(len(files_with_time))
            
            for row, (filename, filepath, mtime) in enumerate(files_with_time):
                # Column 0: File Path
                path_item = QTableWidgetItem(filename)
                path_item.setToolTip(filepath)  # Full path as tooltip
                self.table.setItem(row, 0, path_item)
                
                # Column 1: Date Created
                date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                date_item = QTableWidgetItem(date_str)
                date_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 1, date_item)
                
                # Column 2: Action Button
                select_btn = QPushButton("Select")
                select_btn.setProperty("filepath", filepath)
                select_btn.clicked.connect(self.on_select_clicked)
                select_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        padding: 5px 15px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                    QPushButton:pressed {
                        background-color: #3d8b40;
                    }
                """)
                self.table.setCellWidget(row, 2, select_btn)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading history: {str(e)}")
    
    def on_select_clicked(self):
        sender = self.sender()
        filepath = sender.property("filepath")
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.datareading.emit(data)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reading file: {str(e)}")