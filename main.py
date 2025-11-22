from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QCheckBox,
    QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QListWidget, QLineEdit, QTextEdit, QComboBox,
    QMessageBox, QDoubleSpinBox
)
import sys
import os

from module.qt_custom_style import *
from module.config_manager import *
from module.digsilent_pf import *
from module.digsilent_worker import *

from ui.DetailDynamicUI import *
from ui.NewConfigUI import *
from ui.LoadConfigUI import *
from ui.DetailLoadFlowUI import *
from ui.ProgressBarUI import *
  
class MainWindow(QMainWindow):
    ready_state_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self.loadflow_data = None
        self.ready_to_run = False
        self.dynamic_loadflow_res_file = None   
        self.all_study_cases = []
        self.log_texts = []
        self.is_validated = False  # Track validation status

        self.setWindowTitle("HMI REAKTOR NUKLIR")
        self.setGeometry(100, 60, 1100, 640)
        self.setMinimumSize(1100, 640)
        self.setStyleSheet(CUSTOM_GLOBAL_STYLESHEET)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.wrapper_layout = QVBoxLayout()

        self.main_layout = QHBoxLayout()
        self.status_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.center_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()

        self.wrapper_layout.addLayout(self.main_layout)
        self.central_widget.setLayout(self.wrapper_layout)

        self.status_label = QLabel("Running....")
        self.status_layout.addWidget(self.status_label)
        
        self.progress_bar = ProgressBar(self, minimum=0, maximum=0, objectName="BlueProgressBar", textVisible=False)
        self.status_layout.addWidget(self.progress_bar, 1)

        self.wrapper_layout.addLayout(self.status_layout)

        self.status_label.hide()
        self.progress_bar.hide()

        self.left_panel = QGroupBox("Running History")
        self.left_panel.setLayout(self.left_layout)

        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_history_item_clicked)
        self.left_layout.addWidget(self.history_list)

        # ========== CENTER PANEL ==========

        # Config Control Group
        self.config_group = QGroupBox("Config Control")
        self.config_layout = QVBoxLayout()
        self.config_group.setLayout(self.config_layout)

        # Sim time
        self.config_layout.addWidget(QLabel("Simulation Time"))
        self.start_sim_spin = QDoubleSpinBox()
        self.start_sim_spin.setRange(0.0, 100.0)
        self.start_sim_spin.setValue(0.0)
        self.start_sim_spin.valueChanged.connect(self.update_summary)

        self.stop_sim_spin = QDoubleSpinBox()
        self.stop_sim_spin.setRange(1.0, 300.0)
        self.stop_sim_spin.setValue(20.0)
        self.stop_sim_spin.valueChanged.connect(self.update_summary)

        self.config_layout.addWidget(QLabel("Start Simulation (s):"))
        self.config_layout.addWidget(self.start_sim_spin)
        self.config_layout.addWidget(QLabel("Stop Simulation (s):"))
        self.config_layout.addWidget(self.stop_sim_spin)

        # Fault toggle
        self.toggle_usefault = QCheckBox("Using Fault Scenario")
        self.toggle_usefault.stateChanged.connect(self.on_toggle_fault_changed)
        self.config_layout.addWidget(self.toggle_usefault)

        # Fault time
        self.config_layout.addWidget(QLabel("Fault Time"))
        self.start_fault_spin = QDoubleSpinBox()
        self.start_fault_spin.setRange(0, 100.0)
        self.start_fault_spin.setValue(2.0)
        self.start_fault_spin.valueChanged.connect(self.update_summary)

        self.stop_fault_spin = QDoubleSpinBox()
        self.stop_fault_spin.setRange(0, 100.0)
        self.stop_fault_spin.setValue(2.1)
        self.stop_fault_spin.valueChanged.connect(self.update_summary)

        self.config_layout.addWidget(QLabel("Start Fault (s):"))
        self.config_layout.addWidget(self.start_fault_spin)
        self.config_layout.addWidget(QLabel("Stop Fault (s):"))
        self.config_layout.addWidget(self.stop_fault_spin)

        # Summary label
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("font-weight: bold; color: #0078D7;")
        self.config_layout.addWidget(self.summary_label)

        # Start Simulation Button
        self.start_sim_btn = QPushButton("Start Simulation")
        self.start_sim_btn.clicked.connect(self.on_run_button)
        self.config_layout.addWidget(self.start_sim_btn)

        self.center_layout.addWidget(self.config_group, 3)

        # --- Log History Group ---
        self.log_group = QGroupBox("Log History")
        self.log_layout = QVBoxLayout()
        self.log_group.setLayout(self.log_layout)

        self.log_text = QTextEdit()
        self.log_text.setPlaceholderText("Simulation logs will appear here...")
        self.log_text.setReadOnly(True)
        self.log_layout.addWidget(self.log_text)

        self.center_layout.addWidget(self.log_group, 3)

        # --- Search Box ---
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search log query...")
        self.center_layout.addWidget(self.search_box, 1)

        # ========== RIGHT PANEL ==========

        # --- Scenario Options Group ---
        self.skenario_group = QGroupBox("Scenario Options")
        self.skenario_layout = QVBoxLayout()
        self.skenario_group.setLayout(self.skenario_layout)

        self.scenario_combobox = QComboBox()
        self.scenario_combobox.addItems(["Load Flow", "Dynamic Simulation"])
        self.scenario_combobox.currentTextChanged.connect(
            self.on_scenario_changed)
        self.cases_combobox = QComboBox()

        self.skenario_layout.addWidget(QLabel("Set Your Scenario Simulation"))
        self.skenario_layout.addWidget(self.scenario_combobox)
        self.skenario_layout.addWidget(QLabel("Set Your Cases from Project"))
        self.skenario_layout.addWidget(self.cases_combobox)

        self.right_layout.addWidget(self.skenario_group)

        # --- Connect And Load Config Group (MOVED TO TOP) ---
        self.display_group = QGroupBox("Connect And Load Config")
        self.display_layout = QVBoxLayout()
        self.display_group.setLayout(self.display_layout)

        # New Config Button
        self.new_config_btn = QPushButton("New Config")
        self.new_config_btn.clicked.connect(self.on_new_config_clicked)
        self.display_layout.addWidget(self.new_config_btn)

        # Exist Load Config Button
        self.load_config_btn = QPushButton("Exist Load Config")
        self.load_config_btn.clicked.connect(self.on_load_config_clicked)
        self.display_layout.addWidget(self.load_config_btn)

        # Config Info Display
        self.display_layout.addWidget(QLabel("DigSILENT Path:"))
        self.digsilent_path_label = QLabel("-")
        self.digsilent_path_label.setStyleSheet(
            "padding-left: 10px; color: #666;")
        self.display_layout.addWidget(self.digsilent_path_label)

        self.display_layout.addWidget(QLabel("Project Name:"))
        self.project_name_label = QLabel("-")
        self.project_name_label.setStyleSheet(
            "padding-left: 10px; color: #666;")
        self.display_layout.addWidget(self.project_name_label)

        # Validate Button
        self.validate_btn = QPushButton("Validate")
        self.validate_btn.clicked.connect(self.on_validate_clicked)
        self.display_layout.addWidget(self.validate_btn)

        self.right_layout.addWidget(self.display_group)

        # ========== ASSEMBLE MAIN LAYOUT ==========
        self.main_layout.addWidget(self.left_panel)
        self.main_layout.addLayout(self.center_layout)
        self.main_layout.addLayout(self.right_layout)

        # ========== INITIALIZE STATE ==========
        self.detail_windows = []
        self.initialize_ui_state()

        self.ready_state_changed.connect(self.on_ready_state_changed)

    def initialize_ui_state(self):
        """Initialize UI state - disable everything until validation"""
        # Disable scenario selection until validated
        self.scenario_combobox.setEnabled(False)
        self.cases_combobox.setEnabled(False)

        # Disable all simulation fields
        self.disable_simulation_fields()

        # Update summary
        self.update_summary()

    def disable_simulation_fields(self):
        """Nonaktifkan semua input simulasi dan fault"""
        self.start_sim_spin.setEnabled(False)
        self.stop_sim_spin.setEnabled(False)
        self.toggle_usefault.setEnabled(False)
        self.start_fault_spin.setEnabled(False)
        self.stop_fault_spin.setEnabled(False)
        self.start_sim_btn.setEnabled(False)

    def enable_simulation_fields(self):
        """Aktifkan input simulasi dan toggle fault (fault time masih disabled)"""
        self.start_sim_spin.setEnabled(True)
        self.stop_sim_spin.setEnabled(True)
        self.toggle_usefault.setEnabled(True)
        # Fault time tetap disabled sampai checkbox dicentang
        self.start_fault_spin.setEnabled(False)
        self.stop_fault_spin.setEnabled(False)
        self.start_sim_btn.setEnabled(True)

    def on_toggle_fault_changed(self, state):
        is_checked = self.toggle_usefault.isChecked()
        self.start_fault_spin.setEnabled(is_checked)
        self.stop_fault_spin.setEnabled(is_checked)
        self.update_summary()

    def update_summary(self):
        scenario = self.scenario_combobox.currentText()

        if scenario == "Load Flow":
            self.summary_label.setText(f"Scenario: {scenario}")
        else:  # Dynamic Simulation
            start_sim = self.start_sim_spin.value()
            stop_sim = self.stop_sim_spin.value()
            summary = f"Scenario: {scenario} | Duration: {stop_sim - start_sim}s"

            if self.toggle_usefault.isChecked():
                start_fault = self.start_fault_spin.value()
                stop_fault = self.stop_fault_spin.value()
                fault_dur = stop_fault - start_fault
                summary += f" | Fault: {start_fault}-{stop_fault}s ({round(fault_dur, 3)}s)"

            self.summary_label.setText(summary)

    def on_ready_state_changed(self):
        self.start_sim_btn.setEnabled(self.ready_to_run)
        self.toggle_usefault.setEnabled(self.ready_to_run)

    def refresh_result(self):
        data_path = "./data"
        
        os.path.abspath(data_path)

        hist_list = os.listdir(data_path)
        # print(hist_list)

        self.history_list.clear()

        self.history_list.addItems(hist_list)
    
    def append_log(self, message: str):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def on_history_item_clicked(self, item):
        history_name = os.path.join(os.getcwd(), "data", item.text())
        import json
        if ".json" in history_name:
            print(history_name)
            with open(history_name, "r") as file:
                data_dict = json.load(file)
            detail_window = DetailLoadflowWindow(data_dict, self)
            detail_window.show()
            self.detail_windows.append(detail_window)
        else:
            detail_window = DetailDynamicWindow(history_name, self)
            detail_window.show()
            self.detail_windows.append(detail_window)

    def on_scenario_changed(self, text):
        """Handler ketika scenario berubah - atur enable/disable fields"""
        if not self.is_validated:
            return  # Jangan lakukan apa-apa jika belum validated

        if text == "Load Flow":
            self.disable_simulation_fields()
            self.start_sim_btn.setEnabled(True)
        elif text == "Dynamic Simulation":
            self.enable_simulation_fields()

        self.update_summary()

    def on_new_config_clicked(self):
        """Handler untuk tombol New Config"""
        new_config_window = NewConfigWindow(self)
        new_config_window.show()

    def on_load_config_clicked(self):
        """Handler untuk tombol Exist Load Config"""
        load_config_window = LoadConfigWindow(os.getcwd(), self)
        load_config_window.show()

    def set_config(self, digsilent_path, project_name):
        """Method untuk menerima config dari child windows"""
        self.digsilent_path_label.setText(digsilent_path)
        self.project_name_label.setText(project_name)

        if hasattr(self, 'log_text'):
            self.append_log(f"[INFO] Config loaded:")
            self.append_log(f"[INFO] DigSILENT Path: {digsilent_path}")
            self.append_log(f"[INFO] Project Name: {project_name}")

    def on_validate_clicked(self):
        digsilent_path = self.digsilent_path_label.text()
        project_name = self.project_name_label.text()
        self.start_sim_btn.setEnabled(False)
        self.validate_btn.setEnabled(False)
        self.scenario_combobox.setEnabled(False)
        self.cases_combobox.setEnabled(False)
        self.validate_btn.setText("Validating...")
        self.progress_bar.show()

        if digsilent_path == "-" or project_name == "-":
            QMessageBox.warning(
                self, "Warning", "Please load or create a config first!"
            )
            self.start_sim_btn.setEnabled(True)
            self.validate_btn.setEnabled(True)
            self.validate_btn.setText("Validate")
            self.progress_bar.hide()
            return

        self.append_log("[INFO] Starting validation of DIgSILENT PowerFactory configuration...")

        self.connectandsetupthread = QThread()
        self.digsilent_worker = DigsilentWorker(
            digsilent_path=digsilent_path,
            proj_name=project_name,
            case_name=None,
            start_sim=None,
            stop_sim=None,
            sim_step=None,
            start_fault=None,
            stop_fault=None,
            fault_type=None,
        )

        self.digsilent_worker.moveToThread(self.connectandsetupthread)
        self.connectandsetupthread.started.connect(self.digsilent_worker.work_connectsetup)
        
        self.connectandsetupthread.start()

        self.digsilent_worker.message.connect(self.on_message_pf)
        self.digsilent_worker.finishpayload.connect(self.on_finished_pf)
        
        self.digsilent_worker.finished.connect(self.digsilent_worker.deleteLater)
        self.connectandsetupthread.finished.connect(self.connectandsetupthread.deleteLater)
        self.digsilent_worker.finished.connect(self.connectandsetupthread.quit)
    
    def on_finished_pf(self, data):
        self.append_log(f"[INFO] Done running the process")
        self.progress_bar.hide()
        self.start_sim_btn.setEnabled(False)
        self.start_sim_btn.setText("running...")

        if data["status"] == "ERROR":
            QMessageBox.warning(
                self, f"{data['type']} Status {data['status']}", data['msg']
            )
        elif data["status"] == "SUCCESS":
            QMessageBox.information(
                self, f"{data['type']} Status {data['status']}", data['msg']
            )
            if data["type"] == "CONNECTANDSETUP":
                self.cases_combobox.addItems(data["data"].split(","))
            
            elif data["type"] == "LOADFLOW":
                pass

            self.refresh_result()
        else:
            QMessageBox.information(
                self, "Undefined process status", "Process is done, do it again"
            )
        
        self.validate_btn.setEnabled(True)
        self.start_sim_btn.setEnabled(True)
        self.scenario_combobox.setEnabled(True)
        self.cases_combobox.setEnabled(True)
        self.validate_btn.setText("Validate")
        self.start_sim_btn.setText("Start Simulation")
    
    def on_message_pf(self, msg):
        self.append_log(msg)

    def on_run_button(self):
        self.start_sim_btn.setEnabled(False)
        self.validate_btn.setEnabled(False)
        self.scenario_combobox.setEnabled(False)
        self.cases_combobox.setEnabled(False)
        self.progress_bar.show()

        if self.scenario_combobox.currentText() == "Load Flow":
            self.loadflow_thread = QThread()
            self.digsilent_worker = DigsilentWorker(
                digsilent_path=self.digsilent_path_label.text(),
                proj_name=self.project_name_label.text(),
                case_name=self.cases_combobox.currentText(),
                start_sim=None,
                stop_sim=None,
                sim_step=None,
                start_fault=None,
                stop_fault=None,
                fault_type=None,
            )

            self.digsilent_worker.moveToThread(self.loadflow_thread)
            self.loadflow_thread.started.connect(self.digsilent_worker.work_runloadflow)

            self.loadflow_thread.start()

            self.digsilent_worker.finishpayload.connect(self.on_message_pf)
            self.digsilent_worker.finishpayload.connect(self.on_finished_pf)

            self.digsilent_worker.finished.connect(self.digsilent_worker.deleteLater)
            self.loadflow_thread.finished.connect(self.loadflow_thread.deleteLater)
            self.digsilent_worker.finished.connect(self.loadflow_thread.quit)

        elif self.scenario_combobox.currentText() == "Dynamic Simulation":
            self.dynamicrun_thread = QThread()
            self.digsilent_worker = DigsilentWorker(
                digsilent_path=self.digsilent_path_label.text(),
                proj_name=self.project_name_label.text(),
                case_name=self.cases_combobox.currentText(),
                start_sim=self.start_sim_spin.value(),
                stop_sim=self.stop_sim_spin.value(),
                sim_step=1,
                start_fault=self.start_fault_spin.value(),
                stop_fault=self.stop_fault_spin.value(),
                fault_type=None,
            )

            self.digsilent_worker.moveToThread(self.dynamicrun_thread)
            self.dynamicrun_thread.started.connect(self.digsilent_worker.work_runloadflow)

            self.dynamicrun_thread.start()

            self.digsilent_worker.finishpayload.connect(self.on_message_pf)
            self.digsilent_worker.finishpayload.connect(self.on_finished_pf)

            self.digsilent_worker.finished.connect(self.digsilent_worker.deleteLater)
            self.dynamicrun_thread.finished.connect(self.dynamicrun_thread.deleteLater)
            self.digsilent_worker.finished.connect(self.dynamicrun_thread.quit)

        print("Finished....")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    sys.exit(1)
