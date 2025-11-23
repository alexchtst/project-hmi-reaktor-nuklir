from PyQt5.QtWidgets import (
    QDialog, QPushButton, QLabel, 
    QHBoxLayout, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox,
    QWidget, QFormLayout, QComboBox, QDoubleSpinBox,
    QMessageBox, QSpinBox
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import pyqtSignal, Qt
from ui.DynamicProcessDialogUI import DynamicProcessDialogUI

class RunDynamicUI(QDialog):
    datareading = pyqtSignal(str)
    
    def __init__(
        self, 
        ds_pf_pathfile = None, 
        proj_name = None, 
        case_name = None
    ):
        super().__init__()
        
        self.ds_pf_pathfile = ds_pf_pathfile
        self.proj_name = proj_name
        self.case_name = case_name
        
        self.__start_sim = None
        self.__stop_sim = None
        self.__sim_step = None
        self.__start_fault = None
        self.__stop_fault = None
        
        self.setWindowTitle("Run Dynamic Simulation")
        self.setWindowIcon(QIcon(r"C:\Users\Alex\NgodingDulu\project-hmi-nuklir-new\asset\logo-ugm.jpg"))
        self.setFixedWidth(600)
        self.setFixedHeight(500)
        self.setWindowModality(Qt.ApplicationModal)
        
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Dynamic Simulation Configuration")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Project Info
        info_group = QGroupBox("Project Information")
        info_layout = QFormLayout()
        
        lbl_proj = QLabel(self.proj_name if self.proj_name else "Not Set")
        lbl_proj.setStyleSheet("color: #2196F3; font-weight: bold;")
        info_layout.addRow("Project:", lbl_proj)
        
        lbl_case = QLabel(self.case_name if self.case_name else "Not Set")
        lbl_case.setStyleSheet("color: #2196F3; font-weight: bold;")
        info_layout.addRow("Study Case:", lbl_case)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
        
        # Simulation Time Parameters
        sim_group = QGroupBox("Simulation Time Parameters")
        sim_layout = QFormLayout()
        sim_layout.setSpacing(10)
        
        self.spin_start_sim = QDoubleSpinBox()
        self.spin_start_sim.setRange(-1000.0, 10000.0)
        self.spin_start_sim.setValue(0.0)
        self.spin_start_sim.setSuffix(" s")
        self.spin_start_sim.setDecimals(2)
        self.spin_start_sim.setSingleStep(0.1)
        self.spin_start_sim.setMinimumHeight(30)
        sim_layout.addRow("Start Simulation:", self.spin_start_sim)
        
        self.spin_stop_sim = QDoubleSpinBox()
        self.spin_stop_sim.setRange(-1000.0, 10000.0)
        self.spin_stop_sim.setValue(100.0)
        self.spin_stop_sim.setSuffix(" s")
        self.spin_stop_sim.setDecimals(2)
        self.spin_stop_sim.setSingleStep(1.0)
        self.spin_stop_sim.setMinimumHeight(30)
        sim_layout.addRow("Stop Simulation:", self.spin_stop_sim)
        
        sim_group.setLayout(sim_layout)
        main_layout.addWidget(sim_group)
        
        # Fault Time Parameters
        fault_group = QGroupBox("Fault Time Parameters")
        fault_layout = QFormLayout()
        fault_layout.setSpacing(10)
        
        self.spin_start_fault = QDoubleSpinBox()
        self.spin_start_fault.setRange(0.0, 10000.0)
        self.spin_start_fault.setValue(5.0)
        self.spin_start_fault.setSuffix(" s")
        self.spin_start_fault.setDecimals(2)
        self.spin_start_fault.setSingleStep(0.1)
        self.spin_start_fault.setMinimumHeight(30)
        fault_layout.addRow("Start Fault:", self.spin_start_fault)
        
        self.spin_clear_fault = QDoubleSpinBox()
        self.spin_clear_fault.setRange(0.0, 10000.0)
        self.spin_clear_fault.setValue(5.1)
        self.spin_clear_fault.setSuffix(" s")
        self.spin_clear_fault.setDecimals(2)
        self.spin_clear_fault.setSingleStep(0.1)
        self.spin_clear_fault.setMinimumHeight(30)
        fault_layout.addRow("Clear Fault:", self.spin_clear_fault)
        
        fault_group.setLayout(fault_layout)
        main_layout.addWidget(fault_group)
        
        main_layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.btn_run = QPushButton("Run Simulation")
        self.btn_run.setMinimumHeight(40)
        self.btn_run.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.btn_run.clicked.connect(self.on_run_clicked)
        button_layout.addWidget(self.btn_run)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setMinimumHeight(40)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c1170a;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QDoubleSpinBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #2196F3;
            }
        """)
    
    def on_run_clicked(self):
        self.__start_sim = self.spin_start_sim.value()
        self.__stop_sim = self.spin_stop_sim.value()
        self.__start_fault = self.spin_start_fault.value()
        self.__stop_fault = self.spin_clear_fault.value()
        
        self.accept()
        
        self.progress_dialog = DynamicProcessDialogUI(
            ds_pf_pathfle = self.ds_pf_pathfile,
            proj_name = self.proj_name,
            case_name = self.case_name,
            start_sim = self.__start_sim,
            stop_sim= self.__stop_sim,
            start_fault = self.__start_fault,
            stop_fault = self.__stop_fault,
        )
        self.progress_dialog.show()
    
    def get_parameters(self):
        return {
            "start_sim": self.__start_sim,
            "stop_sim": self.__stop_sim,
            "start_fault": self.__start_fault,
            "clear_fault": self.__stop_fault
        }